"""
Voice Agent Generator for Growth Automation Pipeline.

Creates personalized ElevenLabs voice agents for each business based on
their scraped content, tone, and industry-specific language patterns.

Features:
- Auto-generates agent personalities from business content
- Creates industry-specific system prompts
- Configures voice settings and conversation styles
- Integrates with per-business vector stores
- Generates agent configuration files
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from core.config import get_config
from pipeline.openrouter_client import OpenRouterClient, BusinessContext, AgentContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a business-specific voice agent."""

    domain: str
    agent_name: str
    system_prompt: str
    voice_id: Optional[str] = None
    personality: str = "professional"
    industry: str = "general"
    tone_keywords: List[str] = None
    conversation_style: str = "helpful"
    namespace: str = ""

    def __post_init__(self):
        if self.tone_keywords is None:
            self.tone_keywords = []
        if not self.namespace:
            self.namespace = f"kb:{self.domain}"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "domain": self.domain,
            "agent_name": self.agent_name,
            "system_prompt": self.system_prompt,
            "voice_id": self.voice_id,
            "personality": self.personality,
            "industry": self.industry,
            "tone_keywords": self.tone_keywords,
            "conversation_style": self.conversation_style,
            "namespace": self.namespace,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> AgentConfig:
        """Create from dictionary."""
        return cls(
            domain=data["domain"],
            agent_name=data["agent_name"],
            system_prompt=data["system_prompt"],
            voice_id=data.get("voice_id"),
            personality=data.get("personality", "professional"),
            industry=data.get("industry", "general"),
            tone_keywords=data.get("tone_keywords", []),
            conversation_style=data.get("conversation_style", "helpful"),
            namespace=data.get("namespace", f"kb:{data['domain']}"),
        )


class VoiceAgentGenerator:
    """Generates personalized voice agents for businesses."""

    def __init__(
        self,
        agents_dir: str = "pipeline/agents",
        config_path: str = "pipeline/config/agent_templates.json",
        use_llm: bool = True,
        openrouter_config: Optional[str] = None
    ):
        """Initialize voice agent generator.

        Args:
            agents_dir: Directory to store agent configurations
            config_path: Path to agent template configurations
            use_llm: Whether to use LLM for system prompt generation
            openrouter_config: Path to OpenRouter configuration file
        """
        self.agents_dir = Path(agents_dir)
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = Path(config_path)
        self.templates = self._load_templates()
        self.use_llm = use_llm

        # Initialize OpenRouter client for LLM system prompt generation
        if use_llm:
            try:
                self.llm_client = OpenRouterClient(openrouter_config)
                logger.info("🤖 Initialized OpenRouter client for system prompt generation")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenRouter client: {e}. Using template-based prompts.")
                self.use_llm = False
                self.llm_client = None

    def _load_templates(self) -> Dict[str, Dict]:
        """Load agent templates for different industries."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load templates: {e}")

        # Default templates
        return {
            "default": {
                "base_prompt": "You are a helpful AI assistant for {business_name}. You have access to the company's knowledge base and can provide information about their services, answer questions, and help potential customers.",
                "personalities": {
                    "professional": "Maintain a professional, courteous tone. Be informative and helpful.",
                    "friendly": "Be warm, approachable, and conversational. Show genuine interest in helping.",
                    "expert": "Position yourself as a knowledgeable expert. Provide detailed, technical information when appropriate."
                },
                "industry_defaults": {
                    "dentists": {
                        "personality": "professional",
                        "tone_keywords": ["caring", "experienced", "gentle", "professional"],
                        "conversation_style": "reassuring"
                    },
                    "law_firms": {
                        "personality": "professional",
                        "tone_keywords": ["experienced", "confidential", "reliable", "expert"],
                        "conversation_style": "authoritative"
                    },
                    "hvac": {
                        "personality": "friendly",
                        "tone_keywords": ["reliable", "efficient", "experienced", "responsive"],
                        "conversation_style": "practical"
                    },
                    "general": {
                        "personality": "professional",
                        "tone_keywords": ["helpful", "knowledgeable", "responsive"],
                        "conversation_style": "helpful"
                    }
                }
            }
        }

    def generate_agent_config(
        self,
        domain: str,
        business_name: str,
        industry: str,
        content_summary: Dict[str, str]
    ) -> AgentConfig:
        """Generate agent configuration for a business.

        Args:
            domain: Business domain
            business_name: Business name
            industry: Business industry
            content_summary: Summary of scraped content by type

        Returns:
            AgentConfig for the business
        """
        logger.info(f"🤖 Generating voice agent config for {business_name} ({domain})")

        # Get industry-specific settings
        industry_config = self.templates["default"]["industry_defaults"].get(
            industry.lower().replace(" ", "_"),
            self.templates["default"]["industry_defaults"]["general"]
        )

        # Analyze content to extract tone and personality
        personality, tone_keywords, conversation_style = self._analyze_business_content(
            content_summary, industry_config
        )

        # Generate system prompt
        system_prompt = self._generate_system_prompt_with_llm(
            business_name, domain, industry, content_summary, personality, tone_keywords
        ) if self.use_llm and self.llm_client else self._generate_system_prompt(
            business_name, industry, content_summary, personality, tone_keywords
        )

        # Create agent config
        config = AgentConfig(
            domain=domain,
            agent_name=f"{business_name} Assistant",
            system_prompt=system_prompt,
            personality=personality,
            industry=industry,
            tone_keywords=tone_keywords,
            conversation_style=conversation_style,
        )

        logger.info(f"✅ Generated agent config: {config.agent_name}")
        return config

    def _analyze_business_content(
        self,
        content_summary: Dict[str, str],
        industry_config: Dict
    ) -> tuple[str, List[str], str]:
        """Analyze business content to determine personality and tone.

        Args:
            content_summary: Summary of content by type
            industry_config: Industry-specific defaults

        Returns:
            Tuple of (personality, tone_keywords, conversation_style)
        """
        personality = industry_config["personality"]
        tone_keywords = industry_config["tone_keywords"].copy()
        conversation_style = industry_config["conversation_style"]

        # Analyze content for additional tone indicators
        all_content = " ".join(content_summary.values()).lower()

        # Check for friendly language patterns
        friendly_indicators = ["welcome", "happy to help", "please", "thank you", "excited"]
        friendly_count = sum(1 for word in friendly_indicators if word in all_content)

        # Check for professional language patterns
        professional_indicators = ["expertise", "experience", "professional", "qualified", "certified"]
        professional_count = sum(1 for word in professional_indicators if word in all_content)

        # Adjust personality based on content analysis
        if friendly_count > professional_count and friendly_count > 2:
            personality = "friendly"
            if "approachable" not in tone_keywords:
                tone_keywords.append("approachable")
            conversation_style = "conversational"
        elif professional_count > friendly_count and professional_count > 2:
            personality = "expert"
            if "authoritative" not in tone_keywords:
                tone_keywords.append("authoritative")
            conversation_style = "informative"

        return personality, tone_keywords, conversation_style

    def _generate_system_prompt(
        self,
        business_name: str,
        industry: str,
        content_summary: Dict[str, str],
        personality: str,
        tone_keywords: List[str]
    ) -> str:
        """Generate personalized system prompt for the agent following ElevenLabs best practices.

        Based on official ElevenLabs documentation for Conversational AI agents.

        Args:
            business_name: Name of the business
            industry: Business industry
            content_summary: Summary of scraped content
            personality: Agent personality type
            tone_keywords: Tone keywords for the agent

        Returns:
            Complete system prompt optimized for ElevenLabs agents
        """
        # Extract key information from content
        services = content_summary.get("services", "")
        about = content_summary.get("about", "")
        team = content_summary.get("team", "")

        # ElevenLabs System Prompt Structure (based on their documentation)
        # 1. Role Definition - Clear, specific role
        # 2. Context - Business background and expertise
        # 3. Communication Guidelines - How to interact
        # 4. Boundaries - What not to do and escalation paths
        # 5. Response Format - How to structure responses

        system_prompt = f"""# {business_name} AI Assistant

## Role
You are {business_name}'s official AI assistant, a knowledgeable representative specializing in {industry}. You provide accurate, helpful information about {business_name}'s services and expertise.

## Business Context
{f"About {business_name}: {about[:400]}" if about else f"{business_name} is a trusted {industry} business."}
{f"Services: {services[:500]}" if services else ""}
{f"Team: {team[:300]}" if team else ""}

## Communication Style
- **Personality**: {personality.title()}
- **Tone**: {', '.join(tone_keywords)}
- **Approach**: {'Conversational and approachable' if personality == 'friendly' else 'Professional and informative' if personality == 'expert' else 'Professional and reassuring'}

## Guidelines for Interaction
1. **Be Helpful & Accurate**: Provide clear, factual information based on {business_name}'s actual services and capabilities
2. **Stay In Character**: Always represent {business_name} positively and professionally
3. **Use Natural Language**: Respond conversationally, as if speaking to a customer
4. **Be Concise but Complete**: Give comprehensive answers without being verbose
5. **Show Empathy**: Acknowledge customer needs and concerns appropriately

## Response Best Practices
- Start with acknowledgment of the customer's question or need
- Provide direct, actionable information
- Use the customer's name if provided
- End with an offer to help further or provide next steps
- For complex inquiries, suggest speaking with a human representative

## Boundaries & Escalation
- Only provide information that {business_name} can actually deliver
- If unsure about details, acknowledge limitations and offer to connect with a team member
- Never make promises about pricing, availability, or services without verification
- For urgent or complex matters, always recommend human contact

## Response Format
- Keep responses under 2 minutes when spoken
- Use simple, clear language
- Structure responses with clear beginning, middle, and end
- Include specific next steps when appropriate

Remember: You are the voice of {business_name}. Every interaction should reinforce trust, expertise, and customer care."""

        return system_prompt

    def _generate_system_prompt_with_llm(
        self,
        business_name: str,
        domain: str,
        industry: str,
        content_summary: Dict[str, str],
        personality: str,
        tone_keywords: List[str]
    ) -> str:
        """Generate system prompt using LLM with ElevenLabs documentation guidance.

        Args:
            business_name: Name of the business
            domain: Business domain
            industry: Business industry
            content_summary: Summary of scraped content
            personality: Agent personality type
            tone_keywords: Tone keywords for the agent

        Returns:
            LLM-generated system prompt following ElevenLabs best practices
        """
        logger.info(f"🤖 Generating LLM system prompt for {business_name} with ElevenLabs guidance")

        try:
            # Create business context
            business_context = BusinessContext(
                name=business_name,
                domain=domain,
                industry=industry,
                services_content=content_summary.get("services"),
                about_content=content_summary.get("about"),
                team_content=content_summary.get("team"),
                blog_content=content_summary.get("blog")
            )

            # Create agent context (placeholder values since we're generating the prompt)
            agent_context = AgentContext(
                agent_name=f"{business_name} Assistant",
                personality=personality,
                tone_keywords=tone_keywords,
                conversation_style="helpful",
                industry=industry,
                system_prompt="",  # Will be generated
                namespace=f"kb:{domain}"
            )

            # Generate system prompt using LLM with ElevenLabs documentation
            system_prompt = self.llm_client.generate_agent_system_prompt(
                business_context, agent_context
            )

            logger.info(f"✅ Generated LLM system prompt for {business_name}")
            return system_prompt

        except Exception as e:
            logger.warning(f"LLM system prompt generation failed: {e}. Falling back to template.")
            # Fall back to template-based generation
            return self._generate_system_prompt(
                business_name, industry, content_summary, personality, tone_keywords
            )

    def create_elevenlabs_agent(self, config: AgentConfig) -> Optional[str]:
        """Create ElevenLabs agent from configuration.

        Args:
            config: Agent configuration

        Returns:
            Agent ID if successful, None otherwise
        """
        try:
            from elevenlabs.client import ElevenLabs

            elevenlabs_config = get_config()

            if not elevenlabs_config.elevenlabs_api_key:
                logger.error("❌ ElevenLabs API key not configured")
                return None

            client = ElevenLabs(api_key=elevenlabs_config.elevenlabs_api_key)

            # Create agent
            agent_data = {
                "name": config.agent_name,
                "system_prompt": config.system_prompt,
                "personality": config.personality,
                "conversation_config": {
                    "turn_detection": {
                        "type": "server_vad"
                    }
                }
            }

            # Set voice if specified
            if config.voice_id:
                agent_data["voice_id"] = config.voice_id

            agent = client.agents.create(**agent_data)
            agent_id = getattr(agent, "id", None) or getattr(agent, "agent_id", None)

            if agent_id:
                config.voice_id = getattr(agent, "voice_id", None)
                logger.info(f"🎤 Created ElevenLabs agent: {agent_id}")
                return agent_id
            else:
                logger.error("❌ Failed to get agent ID from ElevenLabs response")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to create ElevenLabs agent: {e}")
            return None

    def save_agent_config(self, config: AgentConfig) -> None:
        """Save agent configuration to file.

        Args:
            config: Agent configuration to save
        """
        domain_dir = self.agents_dir / config.domain.replace(".", "_")
        domain_dir.mkdir(parents=True, exist_ok=True)

        config_file = domain_dir / "agent.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved agent config to {config_file}")

    def generate_agent_for_business(
        self,
        domain: str,
        business_name: str,
        industry: str,
        content_summary: Optional[Dict[str, str]] = None,
        create_elevenlabs: bool = True
    ) -> Optional[AgentConfig]:
        """Complete pipeline: generate and optionally create ElevenLabs agent.

        Args:
            domain: Business domain
            business_name: Business name
            industry: Business industry
            content_summary: Summary of scraped content (will be generated if None)
            create_elevenlabs: Whether to create actual ElevenLabs agent

        Returns:
            AgentConfig if successful, None otherwise
        """
        try:
            # Load content summary if not provided
            if content_summary is None:
                content_summary = self._extract_content_summary(domain)

            if not content_summary:
                logger.warning(f"⚠️ No content summary available for {domain}")
                content_summary = {"general": f"Information about {business_name}, a {industry} business."}

            # Generate configuration
            config = self.generate_agent_config(domain, business_name, industry, content_summary)

            # Create ElevenLabs agent if requested
            if create_elevenlabs:
                agent_id = self.create_elevenlabs_agent(config)
                if agent_id:
                    # Update config with agent ID
                    config.voice_id = agent_id

            # Save configuration
            self.save_agent_config(config)

            logger.info(f"🎉 Successfully generated agent for {business_name}")
            return config

        except Exception as e:
            logger.error(f"❌ Failed to generate agent for {domain}: {e}")
            return None

    def _extract_content_summary(self, domain: str) -> Dict[str, str]:
        """Extract content summary from scraped business data.

        Args:
            domain: Business domain

        Returns:
            Dictionary of content type to summary text
        """
        data_dir = Path("pipeline/business_data") / domain.replace(".", "_")
        content_file = data_dir / "content.json"

        if not content_file.exists():
            return {}

        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)

            summaries = {}
            for content_type, items in content_data.items():
                if items:
                    # Combine content from same type, limit to prevent prompt overflow
                    combined_content = " ".join([item["content"] for item in items[:3]])  # First 3 pages
                    summaries[content_type] = combined_content[:1000]  # Limit length

            return summaries

        except Exception as e:
            logger.error(f"Failed to extract content summary for {domain}: {e}")
            return {}


def main():
    """CLI interface for voice agent generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate voice agents for businesses")
    parser.add_argument("--domain", required=True, help="Business domain")
    parser.add_argument("--business-name", required=True, help="Business name")
    parser.add_argument("--industry", required=True, help="Business industry")
    parser.add_argument("--create-elevenlabs", action="store_true", help="Create actual ElevenLabs agent")
    parser.add_argument("--agents-dir", default="pipeline/agents", help="Agents storage directory")

    args = parser.parse_args()

    generator = VoiceAgentGenerator(args.agents_dir)
    config = generator.generate_agent_for_business(
        domain=args.domain,
        business_name=args.business_name,
        industry=args.industry,
        create_elevenlabs=args.create_elevenlabs
    )

    if config:
        print(f"Successfully generated agent for {args.business_name}")
        print(f"Agent name: {config.agent_name}")
        if config.voice_id:
            print(f"ElevenLabs Agent ID: {config.voice_id}")
    else:
        print("Failed to generate agent")
        exit(1)


if __name__ == "__main__":
    main()
