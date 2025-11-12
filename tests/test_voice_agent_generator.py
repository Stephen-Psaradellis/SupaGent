"""Tests for the revamped VoiceAgentGenerator."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from pipeline.lead_generation import Lead
from pipeline.voice_agent_generator import (
    DEFAULT_VOICE_ID,
    AgentConfig,
    VoiceAgentGenerator,
    main,
)


class TestAgentConfig:
    """Validate the lightweight AgentConfig dataclass."""

    def test_to_request_body(self) -> None:
        payload: Dict[str, str] = {"name": "Demo Agent"}
        config = AgentConfig(domain="example.com", request_payload=payload)

        assert config.to_request_body() is payload
        config.agent_id = "agent_123"
        assert config.agent_id == "agent_123"


class TestVoiceAgentGenerator:
    """Unit tests for the new VoiceAgentGenerator."""

    def test_initialization_llm_failure(self) -> None:
        with patch("pipeline.voice_agent_generator.OpenRouterClient") as mock_client:
            mock_client.side_effect = Exception("boom")
            generator = VoiceAgentGenerator(agents_dir="does_not_matter", use_llm=True)
            assert generator.use_llm is False
            assert generator.llm_client is None

    def test_generate_agent_for_business_fallback(self, tmp_path: Path) -> None:
        generator = VoiceAgentGenerator(agents_dir=str(tmp_path), use_llm=False)

        lead = Lead(
            name="Bright Dental",
            domain="brightdental.com",
            industry="dentist",
            email="info@brightdental.com",
            source="test",
        )
        intelligence = {
            "lead_profile": {
                "name": "Bright Dental",
                "company": "Bright Dental",
                "industry": "dentist",
                "domain": "brightdental.com",
            }
        }

        config = generator.generate_agent_for_business(
            domain=lead.domain,
            business_name=lead.name,
            industry=lead.industry or "dentist",
            lead=lead,
            business_intelligence=intelligence,
            create_elevenlabs=False,
        )

        assert config is not None
        request = config.request_payload
        assert request["conversation_config"]["tts"]["voice_id"] == DEFAULT_VOICE_ID
        assert request["conversation_config"]["agent"]["prompt"]["llm"] == "gpt-4o-mini"

        config_file = tmp_path / lead.domain.replace(".", "_") / "agent_request.json"
        assert config_file.exists()
        saved = json.loads(config_file.read_text())
        assert saved["name"] == request["name"]

    def test_generate_agent_for_business_with_llm(self, tmp_path: Path) -> None:
        blueprint = {
            "name": "LLM Agent",
            "first_message": "Hello from the LLM agent!",
            "language": "en-US",
            "system_prompt": "# LLM Prompt\n\n## Role\nLLM agent role.",
            "tags": ["industry:dentist"],
        }

        mock_client = MagicMock()
        mock_client.generate_agent_blueprint.return_value = blueprint

        with patch("pipeline.voice_agent_generator.OpenRouterClient", return_value=mock_client):
            generator = VoiceAgentGenerator(agents_dir=str(tmp_path), use_llm=True)

        lead = Lead(name="LLM Dental", domain="llmdental.com", industry="dentist", source="test")
        intelligence = {"lead_profile": {"name": "LLM Dental", "company": "LLM Dental"}}

        config = generator.generate_agent_for_business(
            domain=lead.domain,
            business_name=lead.name,
            industry=lead.industry or "dentist",
            lead=lead,
            business_intelligence=intelligence,
            create_elevenlabs=False,
        )

        assert config.request_payload["name"] == "LLM Agent"
        mock_client.generate_agent_blueprint.assert_called_once()

    def test_create_elevenlabs_agent_success(self) -> None:
        generator = VoiceAgentGenerator(agents_dir="tmp", use_llm=False)
        config = AgentConfig(domain="example.com", request_payload={"name": "Example"})

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"agent_id": "agent_001"}

        with patch("pipeline.voice_agent_generator.get_config") as mock_get_config, patch(
            "pipeline.voice_agent_generator.requests.post", return_value=mock_response
        ) as mock_post:
            mock_get_config.return_value = Mock(elevenlabs_api_key="key")

            agent_id = generator.create_elevenlabs_agent(config)

        assert agent_id == "agent_001"
        mock_post.assert_called_once()


class TestVoiceAgentGeneratorCLI:
    """Ensure the CLI wiring still works."""

    @patch("sys.argv", ["voice_agent_generator.py", "--business-name", "Cli Biz", "--industry", "dentist"])
    @patch("pipeline.voice_agent_generator.VoiceAgentGenerator")
    def test_main_success(self, mock_generator_class: Mock) -> None:
        mock_instance = Mock()
        mock_instance.generate_agent_for_business.return_value = AgentConfig("cli", {"name": "CLI Agent"})
        mock_generator_class.return_value = mock_instance

        with patch("builtins.print") as mock_print:
            main()

        mock_print.assert_any_call("Successfully generated payload for Cli Biz")


class TestIntegration:
    """High-level smoke test for file outputs."""

    def test_full_generation_flow(self, tmp_path: Path) -> None:
        generator = VoiceAgentGenerator(agents_dir=str(tmp_path), use_llm=False)

        lead = Lead(name="Flow Biz", domain="flowbiz.com", industry="hvac", source="demo")
        intelligence = {"lead_profile": {"name": "Flow Biz", "company": "Flow Biz", "industry": "hvac"}}

        config = generator.generate_agent_for_business(
            domain=lead.domain,
            business_name=lead.name,
            industry="hvac",
            lead=lead,
            business_intelligence=intelligence,
            create_elevenlabs=False,
        )

        assert config is not None
        config_path = tmp_path / "flowbiz_com" / "agent_request.json"
        assert config_path.exists()
