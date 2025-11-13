"""
Voice Agent Generator for Growth Automation Pipeline.

Generates production-ready ElevenLabs Conversational AI agent payloads
using GPT-4o-mini via OpenRouter combined with structured business
intelligence collected from the pipeline.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from core.config import get_config
from pipeline.lead_generation import Lead
from pipeline.openrouter_client import OpenRouterClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ELEVENLABS_CREATE_AGENT_URL = "https://api.elevenlabs.io/v1/convai/agents/create"
DEFAULT_VOICE_ID = "j57KDF72L6gxbLk4sOo5"
DEFAULT_TTS_MODEL_ID = "eleven_turbo_v2"
DEFAULT_AUDIO_FORMAT = "pcm_16000"


@dataclass
class AgentConfig:
    """Runtime representation of an ElevenLabs agent payload."""

    domain: str
    request_payload: Dict[str, Any]
    agent_id: Optional[str] = None

    def to_request_body(self) -> Dict[str, Any]:
        """Return the JSON payload ready for the ElevenLabs create API."""
        return self.request_payload


class VoiceAgentGenerator:
    """Generate and optionally register ElevenLabs voice agents."""

    def __init__(
        self,
        agents_dir: str = "pipeline/agents",
        use_llm: bool = True,
        openrouter_config: Optional[str] = None,
    ) -> None:
        """Initialize the generator."""
        self.agents_dir = Path(agents_dir)
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.use_llm = use_llm
        self.voice_id = DEFAULT_VOICE_ID

        self.llm_client: Optional[OpenRouterClient] = None
        if use_llm:
            try:
                self.llm_client = OpenRouterClient(openrouter_config)
                logger.info("🤖 Initialized OpenRouter client for agent config generation")
            except Exception as exc:
                logger.warning("Failed to initialize OpenRouter client (%s). Falling back to templates.", exc)
                self.use_llm = False

    def generate_agent_for_business(
        self,
        domain: Optional[str],
        business_name: str,
        industry: str,
        lead: Optional[Lead] = None,
        business_intelligence: Optional[Dict[str, Any]] = None,
        create_elevenlabs: bool = True,
    ) -> Optional[AgentConfig]:
        """Create an agent payload and optionally register it with ElevenLabs."""
        lead = lead or self._build_placeholder_lead(domain, business_name, industry)
        intelligence = business_intelligence or {"lead_profile": self._lead_to_profile(lead, domain, industry)}
        if "lead_profile" not in intelligence:
            intelligence["lead_profile"] = self._lead_to_profile(lead, domain, industry)

        lead_profile = intelligence["lead_profile"]
        blueprint = self._generate_blueprint(lead_profile, intelligence, industry)
        payload = self._build_request_payload(blueprint)

        resolved_domain = lead_profile.get("domain") or domain or "unknown"
        config = AgentConfig(domain=resolved_domain.replace(" ", "_"), request_payload=payload)

        if create_elevenlabs:
            agent_id = self.create_elevenlabs_agent(config)
            if agent_id:
                config.agent_id = agent_id

        self.save_agent_config(config)
        logger.info("🎉 Generated agent payload for %s", business_name)
        return config

    def create_elevenlabs_agent(self, config: AgentConfig) -> Optional[str]:
        """Call ElevenLabs create API with the generated payload."""
        eleven_config = get_config()
        api_key = getattr(eleven_config, "elevenlabs_api_key", None)

        if not api_key:
            logger.warning("ElevenLabs API key not configured; skipping agent creation")
            return None

        try:
            response = requests.post(
                ELEVENLABS_CREATE_AGENT_URL,
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=config.to_request_body(),
                timeout=30,
            )
            if response.status_code >= 400:
                logger.error("❌ ElevenLabs create agent failed: %s - %s", response.status_code, response.text[:200])
                return None

            data = response.json()
            agent_id = data.get("agent_id")
            if not agent_id:
                logger.warning("Create agent response missing agent_id: %s", data)
                return None

            logger.info("🎤 Registered ElevenLabs agent: %s", agent_id)
            return agent_id
        except requests.RequestException as exc:
            logger.error("❌ ElevenLabs agent creation request failed: %s", exc)
            return None

    def save_agent_config(self, config: AgentConfig) -> None:
        """Persist the agent request payload to disk."""
        directory = self.agents_dir / config.domain.replace(".", "_")
        directory.mkdir(parents=True, exist_ok=True)

        config_file = directory / "agent_request.json"
        with open(config_file, "w", encoding="utf-8") as handle:
            json.dump(config.to_request_body(), handle, indent=2, ensure_ascii=False)

        logger.info("💾 Saved agent request payload to %s", config_file)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _build_placeholder_lead(self, domain: Optional[str], business_name: str, industry: str) -> Lead:
        """Create a minimal lead object when one is not supplied."""
        return Lead(
            name=business_name,
            domain=domain or "",
            industry=industry,
            source="manual_placeholder",
        )

    def _lead_to_profile(self, lead: Lead, domain: Optional[str], industry: str) -> Dict[str, Any]:
        """Convert a Lead into a blueprint-friendly profile."""
        domain = domain or lead.domain or (lead.email.split("@")[-1] if lead.email else None)
        profile = {
            "name": lead.name,
            "company": lead.metadata.get("apollo_contact_data", {}).get("organization_name") if lead.metadata else None,
            "industry": lead.industry or industry,
            "location": lead.location,
            "description": lead.description,
            "domain": domain,
            "primary_email": lead.email,
            "phone": lead.phone,
        }
        if not profile.get("company"):
            profile["company"] = lead.name
        return {k: v for k, v in profile.items() if v}

    def _generate_blueprint(
        self,
        lead_profile: Dict[str, Any],
        intelligence: Dict[str, Any],
        industry: str,
    ) -> Dict[str, Any]:
        """Generate blueprint fields via LLM with fallback."""
        if self.use_llm and self.llm_client:
            try:
                return self.llm_client.generate_agent_blueprint(lead_profile, intelligence, industry)
            except Exception as exc:
                logger.warning("LLM blueprint generation failed: %s", exc)

        return self._fallback_blueprint(lead_profile, industry)

    def _fallback_blueprint(self, lead_profile: Dict[str, Any], industry: str) -> Dict[str, Any]:
        """Fallback blueprint ensuring we can continue without the LLM."""
        business_name = lead_profile.get("company") or lead_profile.get("name", "Business")
        return {
            "name": f"{business_name} AI Assistant",
            "first_message": (
                f"Hi there! You're speaking with the AI assistant for {business_name}. "
                "I can help with services, availability, and next steps. How may I support you today?"
            ),
            "language": "en",
            "system_prompt": self._build_fallback_system_prompt(lead_profile, industry),
            "tags": [f"industry:{industry}", "source:voice_agent_pipeline"],
        }

    def _build_fallback_system_prompt(self, lead_profile: Dict[str, Any], industry: str) -> str:
        """Produce a deterministic system prompt when the LLM is unavailable."""
        company = lead_profile.get("company") or lead_profile.get("name", "the business")
        description = lead_profile.get("description") or f"{company} is a trusted {industry} provider."
        return f"""# {company} AI Assistant

## Role
You are {company}'s official AI assistant. Welcome callers, understand their needs, answer questions about services, and guide them to the best next step.

## Business Context
{description}

## Communication Style
- **Personality**: Professional and reassuring
- **Tone**: Warm, knowledgeable, and patient
- **Approach**: Conversational, concise, and action-oriented

## Guidelines for Interaction
1. Acknowledge the caller's request and use their name if provided.
2. Provide clear answers grounded in {company}'s services.
3. Offer to schedule appointments or escalate to a human when appropriate.
4. Ask clarifying questions if information is missing.
5. Summarize next steps before ending the conversation.

## Response Best Practices
- Use natural spoken language and short sentences.
- Keep answers focused on the caller's goal.
- Share relevant service highlights or differentiators.
- End with a helpful follow-up question or offer to assist further.

## Boundaries & Escalation
- Avoid pricing or guarantees unless explicitly provided by {company}.
- Escalate urgent, complex, or highly specialized requests to a human team member.
- Do not answer questions that fall outside of {company}'s services.

## Response Format
- Keep spoken responses between 30–90 seconds.
- Use a clear beginning, middle, and end.
- Offer one or two concrete next steps when helpful.

Remember: Every interaction should reinforce {company}'s expertise, reliability, and care."""

    def _build_request_payload(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Merge blueprint fields with standard conversation configuration."""
        conversation_config = {
            "agent": {
                "first_message": blueprint["first_message"].strip(),
                "language": blueprint.get("language", "en").split("-")[0],
                "prompt": {
                    "prompt": blueprint["system_prompt"],
                    "llm": "gemini-2.5-flash",
                },
            },
            "tts": {
                "model_id": DEFAULT_TTS_MODEL_ID,
                "voice_id": DEFAULT_VOICE_ID,
                "agent_output_audio_format": DEFAULT_AUDIO_FORMAT,
                "optimize_streaming_latency": 3,
                "stability": 0.45,
                "similarity_boost": 0.3,
            },
            "asr": {
                "provider": "elevenlabs",
                "quality": "high",
                "user_input_audio_format": DEFAULT_AUDIO_FORMAT,
            },
            "turn": {
                "turn_timeout": 30,
                "initial_wait_time": 1,
                "silence_end_call_timeout": 60,
                "soft_timeout_config": {
                    "timeout_seconds": 5,
                    "message": "I'm still here if you need anything else.",
                },
                "turn_eagerness": "normal",
            },
            "conversation": {
                "text_only": False,
                "max_duration_seconds": 900,
            },
        }

        payload: Dict[str, Any] = {
            "name": blueprint["name"],
            "conversation_config": conversation_config,
        }

        tags = blueprint.get("tags")
        if tags:
            payload["tags"] = tags

        return payload


def main() -> None:
    """CLI for ad-hoc agent payload generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate ElevenLabs agent payloads")
    parser.add_argument("--domain", help="Business domain (optional)")
    parser.add_argument("--business-name", required=True, help="Business name")
    parser.add_argument("--industry", required=True, help="Business industry")
    parser.add_argument("--create-elevenlabs", action="store_true", help="Create agent on ElevenLabs")
    parser.add_argument("--agents-dir", default="pipeline/agents", help="Directory to store payloads")

    args = parser.parse_args()

    generator = VoiceAgentGenerator(agents_dir=args.agents_dir, use_llm=True)
    placeholder_lead = Lead(
        name=args.business_name,
        domain=args.domain or "",
        industry=args.industry,
        source="cli",
    )
    intelligence = {"lead_profile": generator._lead_to_profile(placeholder_lead, args.domain, args.industry)}

    config = generator.generate_agent_for_business(
        domain=args.domain,
        business_name=args.business_name,
        industry=args.industry,
        lead=placeholder_lead,
        business_intelligence=intelligence,
        create_elevenlabs=args.create_elevenlabs,
    )

    if config:
        print(f"Successfully generated payload for {args.business_name}")
        if config.agent_id:
            print(f"Registered ElevenLabs agent ID: {config.agent_id}")
    else:
        print("Failed to generate agent payload")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
