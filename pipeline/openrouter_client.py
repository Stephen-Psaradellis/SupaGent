"""
OpenRouter Client for Intelligent Email Generation.

Uses Mistral Medium via OpenRouter API to generate personalized cold outreach emails
with access to MCP server tools and business intelligence data.

Features:
- MCP server integration for tool calling
- Vector store access for business data
- Contextual email generation
- Industry-specific personalization
- Agent configuration awareness
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter client."""

    api_key: str
    model: str = "mistralai/mistral-7b-instruct:free"
    base_url: str = "https://openrouter.ai/api/v1"
    temperature: float = 0.7
    max_tokens: int = 4000
    mcp_server_url: Optional[str] = None


@dataclass
class BusinessContext:
    """Context about the target business for email generation."""

    name: str
    domain: str
    industry: str
    location: Optional[str] = None
    email: Optional[str] = None
    services_content: Optional[str] = None
    about_content: Optional[str] = None
    team_content: Optional[str] = None
    blog_content: Optional[str] = None


@dataclass
class AgentContext:
    """Context about the voice agent configuration."""

    agent_name: str
    personality: str
    tone_keywords: List[str]
    conversation_style: str
    industry: str
    system_prompt: str
    namespace: str
    demo_url: Optional[str] = None


class OpenRouterClient:
    """OpenRouter client with MCP server integration for intelligent email generation and agent creation."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize OpenRouter client.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://supagent.ai",
            "X-Title": "SupaGent Growth Pipeline",
        })

        # MCP client for tool calling
        self.mcp_client = None
        if self.config.mcp_server_url:
            self._init_mcp_client()

        # Load ElevenLabs documentation for agent creation guidance
        self.elevenlabs_docs = self._load_elevenlabs_documentation()

    def _load_elevenlabs_documentation(self) -> str:
        """Load official ElevenLabs documentation for agent creation guidance.

        Returns:
            ElevenLabs documentation and best practices as string
        """
        docs = """
# Official ElevenLabs Conversational AI Agent Documentation

## System Prompt Best Practices

### 1. Role Definition
- **Be Specific**: Clearly define the agent's role, expertise, and relationship to the user/business
- **Include Context**: Mention the business name, industry, and what makes this agent unique
- **Set Expectations**: Explain what the agent can and cannot do

### 2. Communication Guidelines
- **Personality**: Define the agent's personality (professional, friendly, expert, reassuring)
- **Tone**: Specify tone keywords and communication style
- **Language**: Use natural, conversational language appropriate for voice interactions
- **Length**: Keep responses concise (under 2 minutes when spoken)

### 3. Response Structure
- **Beginning**: Acknowledge the user's question or need
- **Middle**: Provide clear, actionable information
- **End**: Offer next steps or further assistance
- **Empathy**: Show understanding of user concerns

### 4. Boundaries and Limitations
- **Scope**: Clearly define what information the agent can provide
- **Escalation**: When to recommend human contact
- **Verification**: Never make unverified promises
- **Accuracy**: Only provide information the business can actually deliver

### 5. Voice-Optimized Content
- **Natural Flow**: Write for spoken delivery, not just text
- **Simple Language**: Use clear, everyday language
- **Structured Format**: Use numbered lists, clear sections
- **Actionable**: Include specific next steps

## Agent Creation Guidelines

### Core Components
1. **System Prompt**: Comprehensive instructions for agent behavior
2. **Personality**: Defines communication style and tone
3. **Context**: Business background and capabilities
4. **Boundaries**: What the agent should/shouldn't do

### Voice Agent Characteristics
- **Conversational**: Speak naturally, like a human representative
- **Helpful**: Focus on solving user problems
- **Accurate**: Provide only verified information
- **Professional**: Maintain business-appropriate standards
- **Empathetic**: Show understanding of user needs

### Response Best Practices
- Start with greeting/acknowledgment
- Provide direct answers to questions
- Use simple, clear language
- End with clear next steps
- Offer human escalation when appropriate

## Technical Considerations
- **Response Length**: Keep under 1000 characters for voice
- **Natural Pauses**: Structure content for spoken delivery
- **Error Handling**: Graceful handling of unknown information
- **Consistency**: Maintain consistent personality across interactions

## Business Integration
- **Brand Voice**: Match the business's communication style
- **Service Knowledge**: Deep understanding of offerings
- **Team Awareness**: Know when to escalate to human staff
- **Quality Assurance**: Regular review and updates of prompts
"""

        return docs

    def _load_config(self, config_path: Optional[str]) -> OpenRouterConfig:
        """Load configuration from environment or file."""
        # Default config from environment
        config = OpenRouterConfig(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            model=os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free"),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "4000")),
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
        )

        # Load from file if provided
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    for key, value in file_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

        if not config.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        return config

    def _init_mcp_client(self) -> None:
        """Initialize MCP client for tool calling."""
        try:
            # We'll implement MCP tool calling through HTTP requests
            # since we can't directly import the MCP SDK here
            logger.info(f"Initialized MCP client for {self.config.mcp_server_url}")
        except Exception as e:
            logger.warning(f"Failed to initialize MCP client: {e}")

    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call an MCP server tool via HTTP.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response as string
        """
        if not self.config.mcp_server_url:
            return "MCP server not configured"

        try:
            # Construct MCP tool call request
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            response = self.session.post(
                self.config.mcp_server_url,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return str(result["result"])
                elif "error" in result:
                    return f"MCP Error: {result['error']}"
            else:
                return f"HTTP Error {response.status_code}: {response.text}"

        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return f"Tool call error: {str(e)}"

    def _search_business_knowledge(self, query: str, namespace: str) -> str:
        """Search business knowledge base for relevant information.

        Args:
            query: Search query
            namespace: Business namespace (e.g., 'kb:example.com')

        Returns:
            Relevant information from knowledge base
        """
        # Use MCP search tool with namespace filtering
        search_query = f"{query} namespace:{namespace}"

        # Try to call the MCP search tool
        try:
            result = self._call_mcp_tool("search_knowledge_base", {
                "query": search_query,
                "k": 5
            })
            return result
        except Exception as e:
            logger.warning(f"Knowledge base search failed: {e}")
            return "No relevant information found in knowledge base"

    def generate_agent_system_prompt(
        self,
        business_context: BusinessContext,
        agent_context: AgentContext
    ) -> str:
        """Generate an ElevenLabs-optimized system prompt using LLM with official documentation guidance.

        Args:
            business_context: Information about the target business
            agent_context: Configuration of the voice agent

        Returns:
            Optimized system prompt following ElevenLabs best practices
        """
        logger.info(f"🤖 Generating ElevenLabs-optimized system prompt for {business_context.name}")

        # Gather business intelligence from vector store
        business_intelligence = self._gather_business_intelligence(business_context)

        # Create comprehensive prompt for LLM with ElevenLabs documentation
        prompt = self._build_system_prompt_generation_prompt(
            business_context, agent_context, business_intelligence
        )

        # Generate system prompt using OpenRouter
        response = self._call_openrouter(prompt)

        # Parse and validate the response
        return self._parse_system_prompt_response(response, business_context)

    def generate_agent_blueprint(
        self,
        lead_profile: Dict[str, Any],
        business_intelligence: Dict[str, Any],
        industry: str,
    ) -> Dict[str, Any]:
        """Generate dynamic agent blueprint fields via GPT-4o-mini.

        Args:
            lead_profile: Normalized lead profile dictionary.
            business_intelligence: Intelligence bundle from the pipeline.
            industry: Industry descriptor for the business.

        Returns:
            Dictionary containing `name`, `first_message`, `language`, `system_prompt`, and optional tags.
        """
        trimmed_intelligence = self._trim_intelligence_payload(business_intelligence)
        trimmed_intelligence["industry"] = industry

        # Ensure the prompt remains compact while retaining critical context.
        lead_context_json = json.dumps(lead_profile, indent=2, ensure_ascii=False)
        intelligence_json = json.dumps(trimmed_intelligence, indent=2, ensure_ascii=False)

        prompt = f"""You are an elite voice AI prompt engineer working on ElevenLabs Conversational AI agents.

Follow the official documentation to craft a production-ready system prompt and conversational framing.

## OFFICIAL ELEVENLABS DOCUMENTATION
{self.elevenlabs_docs}

## OBJECTIVE
- Create a JSON blueprint describing the agent name, opening message, language, system prompt, and relevant tags.
- The system prompt MUST follow the documentation structure (Role, Business Context, Communication Style, Guidelines, Response Best Practices, Boundaries & Escalation, Response Format).
- The system prompt should be optimized for spoken delivery (concise sentences, natural transitions, empathy).
- The agent will later be assigned voice_id "j57KDF72L6gxbLk4sOo5" (do not include this in the JSON; it is provided for context).

## LEAD PROFILE
{lead_context_json}

## BUSINESS INTELLIGENCE
{intelligence_json}

## OUTPUT REQUIREMENTS
Return ONLY a JSON object with the following structure (no markdown code fences):
{{
  "name": "Short, on-brand agent name (e.g. '{lead_profile.get('company') or lead_profile.get('name')} AI Concierge')",
  "first_message": "Warm greeting introducing the business and offering help in <90 words",
  "language": "Locale code such as 'en-US'",
  "system_prompt": "Full markdown-formatted system prompt following the official documentation",
  "tags": ["industry:<industry>", "source:voice_agent_pipeline", "... optional additional tags"]
}}

- Ensure `first_message` is conversational, welcoming, and references the business by name.
- If the business serves customers in English, default to language 'en-US' unless strong evidence suggests otherwise.
- Keep `tags` concise (3-5 items max) and include the industry.
- Do NOT include any surrounding commentary.
"""

        response = self._call_openrouter(
            prompt,
            model="openai/gpt-4o-mini",
            temperature=0.35,
            max_tokens=3200,
        )

        blueprint = self._parse_json_response(response)

        if not blueprint:
            logger.warning("Agent blueprint generation failed; using fallback blueprint.")
            blueprint = {
                "name": f"{lead_profile.get('company') or lead_profile.get('name', 'Business')} AI Assistant",
                "first_message": (
                    f"Hi there! This is the AI assistant for {lead_profile.get('company') or lead_profile.get('name')}. "
                    "I can help with services, availability, and next steps. How can I support you today?"
                ),
                "language": "en-US",
                "system_prompt": self._fallback_system_prompt(lead_profile, industry),
                "tags": [f"industry:{industry}", "source:voice_agent_pipeline"],
            }

        blueprint.setdefault("language", "en-US")
        if not blueprint.get("name"):
            blueprint["name"] = f"{lead_profile.get('company') or lead_profile.get('name', 'Business')} AI Assistant"
        if not blueprint.get("first_message"):
            blueprint["first_message"] = (
                f"Hello! I'm the AI assistant for {lead_profile.get('company') or lead_profile.get('name')}. "
                "How may I help you today?"
            )
        if not blueprint.get("system_prompt"):
            blueprint["system_prompt"] = self._fallback_system_prompt(lead_profile, industry)
        if not blueprint.get("tags"):
            blueprint["tags"] = [f"industry:{industry}", "source:voice_agent_pipeline"]

        return blueprint

    def _fallback_system_prompt(self, lead_profile: Dict[str, Any], industry: str) -> str:
        """Fallback system prompt used when LLM generation fails."""
        company = lead_profile.get("company") or lead_profile.get("name", "the business")
        description = lead_profile.get("description") or f"{company} is a trusted {industry} provider."

        return f"""# {company} AI Assistant

## Role
You are {company}'s official AI voice assistant. You greet callers, answer questions about services, and guide them to the right next steps.

## Business Context
{description}

## Communication Style
- **Personality**: Professional and reassuring
- **Tone**: Warm, knowledgeable, and patient
- **Approach**: Conversational while staying focused on helping the caller quickly

## Guidelines for Interaction
1. Acknowledge the caller's request and use their name if provided.
2. Reference {company}'s services and strengths when answering questions.
3. Ask clarifying questions when needed to provide accurate information.
4. Offer to schedule appointments, provide contact details, or escalate to a human when appropriate.
5. Keep answers succinct while covering critical information.

## Response Best Practices
- Begin with a friendly greeting and a short summary of how you can help.
- Provide clear, actionable information using natural spoken language.
- Highlight relevant service offerings or differentiators.
- Close with a helpful question or suggested next step.

## Boundaries & Escalation
- Do not provide pricing or guarantees unless explicitly stated by {company}.
- If the caller needs urgent assistance or highly specialized help, escalate to a human team member.
- Avoid answering questions outside of {company}'s scope of services.

## Response Format
- Keep spoken responses between 30-90 seconds.
- Use short sentences and natural transitions.
- Offer one or two concrete next steps when helpful.

Remember: You represent {company}. Every interaction should reinforce trust, expertise, and care."""

    def _build_system_prompt_generation_prompt(
        self,
        business: BusinessContext,
        agent: AgentContext,
        intelligence: Dict[str, str]
    ) -> str:
        """Build comprehensive prompt for system prompt generation with ElevenLabs guidance.

        Args:
            business: Business context
            agent: Agent configuration
            intelligence: Business intelligence data

        Returns:
            Complete prompt for LLM including ElevenLabs documentation
        """
        prompt = f"""You are an expert AI prompt engineer specializing in creating high-quality system prompts for ElevenLabs Conversational AI agents.

Your task is to create an optimized system prompt that follows ElevenLabs best practices and documentation guidelines.

## OFFICIAL ELEVENLABS DOCUMENTATION REFERENCE:

{self.elevenlabs_docs}

## BUSINESS INFORMATION:

Business Name: {business.name}
Industry: {business.industry}
Domain: {business.domain}

Business Intelligence Available:
Services: {intelligence.get('services', 'Not available')}
About: {intelligence.get('about', 'Not available')}
Team: {intelligence.get('team', 'Not available')}
Industry Insights: {intelligence.get('industry_insights', 'Not available')}

## AGENT CONFIGURATION:

Agent Name: {agent.agent_name}
Personality: {agent.personality}
Tone Keywords: {', '.join(agent.tone_keywords)}
Conversation Style: {agent.conversation_style}
Current System Prompt: {agent.system_prompt}

## REQUIREMENTS:

Create a comprehensive system prompt that follows the ElevenLabs documentation structure:

1. **Role Definition** - Clear, specific role with business context
2. **Business Context** - Detailed information about the business and services
3. **Communication Guidelines** - Personality, tone, and interaction style
4. **Response Best Practices** - How to structure responses for voice
5. **Boundaries & Escalation** - What to do/not do, when to escalate
6. **Response Format Guidelines** - Voice-optimized formatting

## KEY ELEVENLABS PRINCIPLES TO FOLLOW:

- **Voice-First Design**: Write for spoken delivery, not just text
- **Natural Conversation**: Use conversational, human-like language
- **Response Length**: Keep responses under 2 minutes when spoken
- **Clear Structure**: Use numbered lists and clear sections
- **Empathy & Helpfulness**: Show understanding and provide actionable help
- **Professional Boundaries**: Know limitations and escalation paths
- **Brand Consistency**: Maintain business voice and values

## OUTPUT FORMAT:

Return a complete system prompt in the following markdown format:

# [Business Name] AI Assistant

## Role
[Clear role definition]

## Business Context
[Detailed business information]

## Communication Style
[Personality and tone guidelines]

## Guidelines for Interaction
[Numbered list of interaction guidelines]

## Response Best Practices
[Best practices for responses]

## Boundaries & Escalation
[What agent can/cannot do]

## Response Format
[Voice-optimized formatting guidelines]

Remember: [Key reminder about representing the business]

Generate the optimized system prompt now:"""

        return prompt

    def _parse_system_prompt_response(self, response: str, business: BusinessContext) -> str:
        """Parse the LLM response into a clean system prompt.

        Args:
            response: Raw LLM response
            business: Business context for fallback

        Returns:
            Clean system prompt
        """
        try:
            # Try to extract just the system prompt content
            # Look for markdown headers or structured content
            if "# " in response:
                # Extract from markdown format
                lines = response.strip().split('\n')
                # Find the start of the actual prompt
                start_idx = next((i for i, line in enumerate(lines) if line.startswith('# ')), 0)
                return '\n'.join(lines[start_idx:]).strip()
            else:
                # Use the response as-is if it's already formatted
                return response.strip()

        except Exception as e:
            logger.warning(f"Failed to parse system prompt response: {e}")
            # Return a basic fallback prompt
            return f"""# {business.name} AI Assistant

## Role
You are {business.name}'s AI assistant, specializing in {business.industry}.

## Business Context
{business.name} is a trusted {business.industry} business offering professional services.

## Communication Style
- **Personality**: Professional
- **Tone**: Helpful, knowledgeable, responsive
- **Approach**: Professional and reassuring

## Guidelines for Interaction
1. Be helpful and accurate
2. Stay in character as a representative of {business.name}
3. Use natural, conversational language
4. Show empathy and understanding

## Response Best Practices
- Acknowledge customer needs
- Provide clear information
- Offer specific next steps
- Suggest human contact when appropriate

Remember: You are the voice of {business.name}. Every interaction should build trust and demonstrate expertise."""

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse raw LLM output into a JSON object."""
        text = response.strip()

        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in text:
            text = text.split("```", 1)[1].split("```", 1)[0].strip()

        def _attempt_parse(candidate: str) -> Optional[Dict[str, Any]]:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None
            return None

        parsed = _attempt_parse(text)
        if parsed is not None:
            return parsed

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            parsed = _attempt_parse(text[start:end + 1])
            if parsed is not None:
                return parsed

        logger.warning("Failed to parse JSON from LLM response: %s", text[:200])
        return {}

    def generate_email_template(
        self,
        business_context: BusinessContext,
        agent_context: AgentContext,
        sender_info: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate intelligent email template using LLM with business context.

        Args:
            business_context: Information about the target business
            agent_context: Configuration of the voice agent
            sender_info: Information about the sender

        Returns:
            Generated email template with subject, body, and metadata
        """
        logger.info(f"🤖 Generating intelligent email for {business_context.name}")

        # Gather business intelligence from vector store
        business_intelligence = self._gather_business_intelligence(business_context)

        # Create comprehensive prompt for LLM
        prompt = self._build_email_generation_prompt(
            business_context,
            agent_context,
            sender_info,
            business_intelligence
        )

        # Generate email using OpenRouter
        response = self._call_openrouter(prompt)

        # Parse and structure the response
        return self._parse_email_response(response, business_context)

    def _gather_business_intelligence(self, business: BusinessContext) -> Dict[str, str]:
        """Gather intelligence about the business from various sources.

        Args:
            business: Business context information

        Returns:
            Dictionary of intelligence categories and their content
        """
        intelligence = {}

        # Search for services information
        if business.services_content:
            intelligence["services"] = business.services_content[:1000]
        else:
            services_search = self._search_business_knowledge(
                "services offered products solutions",
                business.domain.replace(".", "_")
            )
            intelligence["services"] = services_search

        # Search for company information
        if business.about_content:
            intelligence["about"] = business.about_content[:1000]
        else:
            about_search = self._search_business_knowledge(
                "about company mission values history",
                business.domain.replace(".", "_")
            )
            intelligence["about"] = about_search

        # Search for team information
        if business.team_content:
            intelligence["team"] = business.team_content[:500]
        else:
            team_search = self._search_business_knowledge(
                "team staff leadership expertise",
                business.domain.replace(".", "_")
            )
            intelligence["team"] = team_search

        # Industry pain points and value propositions
        intelligence["industry_insights"] = self._get_industry_insights(business.industry)

        return intelligence

    def _get_industry_insights(self, industry: str) -> str:
        """Get industry-specific insights and pain points.

        Args:
            industry: Business industry

        Returns:
            Industry insights as string
        """
        insights = {
            "dentists": """
            Pain Points: Patient scheduling, after-hours inquiries, service questions, insurance information, emergency care
            Value Props: 24/7 patient support, instant appointment booking, clear service information, emergency guidance
            Communication Style: Caring, professional, reassuring, patient-focused
            """,
            "law_firms": """
            Pain Points: Client intake, consultation scheduling, basic legal questions, document requests
            Value Props: Streamlined client onboarding, instant consultation booking, clear service information, confidentiality assurance
            Communication Style: Professional, authoritative, trustworthy, detail-oriented
            """,
            "hvac": """
            Pain Points: Emergency repairs, service scheduling, price estimates, maintenance questions
            Value Props: 24/7 emergency response, instant service booking, transparent pricing, preventive maintenance guidance
            Communication Style: Reliable, practical, responsive, trustworthy
            """,
            "plumbers": """
            Pain Points: Emergency plumbing issues, service scheduling, price estimates, basic troubleshooting
            Value Props: Fast emergency response, clear service information, transparent pricing, preventive maintenance
            Communication Style: Reliable, responsive, practical, experienced
            """,
            "restaurants": """
            Pain Points: Reservation management, menu questions, special requests, hours/location inquiries
            Value Props: Seamless reservation system, instant availability, dietary accommodation, special event planning
            Communication Style: Welcoming, attentive, accommodating, professional
            """
        }

        return insights.get(industry.lower().replace(" ", "_"), "General business insights and value propositions")

    def _trim_intelligence_payload(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce raw intelligence payload to the most relevant, LLM-friendly fields.

        Args:
            intelligence: Complete intelligence dictionary from the pipeline.

        Returns:
            Trimmed dictionary safe to embed inside prompts.
        """
        if not intelligence:
            return {}

        trimmed: Dict[str, Any] = {}

        digest = intelligence.get("llm_digest")
        if digest:
            trimmed["digest"] = digest[:2000]

        content_highlights = intelligence.get("content_highlights") or {}
        trimmed_highlights: Dict[str, List[str]] = {}
        for key, highlights in content_highlights.items():
            if isinstance(highlights, list) and highlights:
                trimmed_highlights[key] = highlights[:3]
        if trimmed_highlights:
            trimmed["content_highlights"] = trimmed_highlights

        keyword_signals = intelligence.get("keyword_signals")
        if keyword_signals:
            trimmed["keyword_signals"] = keyword_signals

        hunter = intelligence.get("hunter_enrichment")
        if hunter:
            domain_search = hunter.get("domain_search") or {}
            trimmed_hunter = {
                "organization": domain_search.get("organization"),
                "pattern": domain_search.get("pattern"),
                "emails": [
                    {
                        "value": email.get("value"),
                        "type": email.get("type"),
                        "confidence": email.get("confidence"),
                        "position": email.get("position"),
                    }
                    for email in (domain_search.get("emails") or [])[:3]
                ],
                "email_finder": hunter.get("email_finder"),
            }
            trimmed["hunter"] = trimmed_hunter

        metadata = intelligence.get("metadata_insights")
        if metadata:
            apollo = metadata.get("apollo_contact")
            if apollo:
                trimmed["apollo"] = {
                    "title": apollo.get("title"),
                    "organization_name": apollo.get("organization_name"),
                    "city": apollo.get("city"),
                    "state": apollo.get("state"),
                    "contact_emails": apollo.get("contact_emails"),
                    "phone_numbers": apollo.get("phone_numbers"),
                }

        lead_profile = intelligence.get("lead_profile")
        if lead_profile:
            trimmed["lead_profile"] = lead_profile

        return trimmed

    def _build_email_generation_prompt(
        self,
        business: BusinessContext,
        agent: AgentContext,
        sender: Dict[str, str],
        intelligence: Dict[str, str]
    ) -> str:
        """Build comprehensive prompt for email generation.

        Args:
            business: Business context
            agent: Agent configuration
            sender: Sender information
            intelligence: Business intelligence data

        Returns:
            Complete prompt for LLM
        """
        prompt = f"""You are an expert copywriter specializing in B2B cold outreach emails for AI solutions.

YOUR MISSION: Create a compelling cold outreach email that introduces a personalized voice agent to a business owner. The email should demonstrate deep understanding of their business and position the AI agent as a valuable solution to their specific pain points.

TARGET BUSINESS INFORMATION:
- Name: {business.name}
- Industry: {business.industry}
- Location: {business.location or 'Not specified'}
- Domain: {business.domain}

BUSINESS INTELLIGENCE GATHERED:
Services: {intelligence.get('services', 'Not available')}
About: {intelligence.get('about', 'Not available')}
Team: {intelligence.get('team', 'Not available')}
Industry Insights: {intelligence.get('industry_insights', 'Not available')}

VOICE AGENT CONFIGURATION:
- Agent Name: {agent.agent_name}
- Personality: {agent.personality}
- Tone Keywords: {', '.join(agent.tone_keywords)}
- Conversation Style: {agent.conversation_style}
- Industry: {agent.industry}
- Key Capabilities: 24/7 availability, instant responses, personalized interactions, deep business knowledge

SENDER INFORMATION:
- Name: {sender.get('name', 'AI Solutions Specialist')}
- Title: {sender.get('title', 'AI Solutions Specialist')}
- Company: {sender.get('company', 'VoiceGenius AI')}
- Email: {sender.get('email', 'hello@voicegenius.ai')}
- Phone: {sender.get('phone', '(555) 123-4567')}

EMAIL GOALS:
1. Demonstrate understanding of the business and their industry
2. Highlight specific pain points they likely face
3. Introduce the voice agent as a personalized solution
4. Include a clear call-to-action to try the agent demo
5. Build credibility and trust
6. Keep the tone professional but conversational

EMAIL STRUCTURE REQUIREMENTS:
- Subject line: Compelling, benefit-focused, under 60 characters
- Opening: Personalized greeting with business owner's name if known, otherwise professional greeting
- Hook: Show understanding of their business/industry challenges
- Value Proposition: Explain how the voice agent solves their specific problems
- Social Proof: Mention the agent's capabilities and personalization
- Call to Action: Clear next step (try the demo, book a call, etc.)
- Closing: Professional sign-off with contact information

KEY CONSTRAINTS:
- Do not mention ElevenLabs or any technical implementation details
- Focus on business benefits, not technical features
- Keep total email length to 150-250 words
- Use industry-appropriate language and terminology
- Include 2-3 specific, actionable value propositions
- End with a specific, time-bound call to action

RESPONSE FORMAT:
Return a JSON object with this exact structure:
{{
  "subject": "Compelling subject line here",
  "body": "Complete email body with proper formatting and line breaks",
  "key_personalizations": ["List 3-5 specific elements personalized to this business"],
  "value_propositions_used": ["List the 2-3 main value propositions highlighted"],
  "confidence_score": "High/Medium/Low - how well this email addresses their specific needs"
}}

Generate the email now:"""

        return prompt

    def _call_openrouter(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Call OpenRouter API with the given prompt.

        Args:
            prompt: The prompt to send to the LLM
            model: Optional override for the model identifier.
            temperature: Optional temperature override.
            max_tokens: Optional max token override.

        Returns:
            LLM response as string
        """
        model_name = model or self.config.model
        request_temperature = temperature if temperature is not None else self.config.temperature
        request_max_tokens = max_tokens or self.config.max_tokens

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": request_temperature,
            "max_tokens": request_max_tokens,
        }

        try:
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return content
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return '{"error": "API call failed", "subject": "AI-Powered Customer Service Solution", "body": "We offer personalized AI voice agents for your business. Contact us to learn more.", "key_personalizations": [], "value_propositions_used": [], "confidence_score": "Low"}'

        except Exception as e:
            logger.error(f"OpenRouter API request failed: {e}")
            return '{"error": "Request failed", "subject": "AI-Powered Customer Service Solution", "body": "We offer personalized AI voice agents for your business. Contact us to learn more.", "key_personalizations": [], "value_propositions_used": [], "confidence_score": "Low"}'

    def _parse_email_response(self, response: str, business: BusinessContext) -> Dict[str, str]:
        """Parse the LLM response into structured email template.

        Args:
            response: Raw LLM response
            business: Business context for fallback

        Returns:
            Structured email template
        """
        try:
            # Try to parse as JSON
            result = json.loads(response.strip())

            # Validate required fields
            if "subject" not in result or "body" not in result:
                raise ValueError("Missing required fields")

            # Ensure we have all expected fields
            template = {
                "subject": result.get("subject", f"AI Solution for {business.name}"),
                "body": result.get("body", "Please contact us to learn about our AI solutions."),
                "recipient_email": business.email or "",
                "recipient_name": None,  # Would be extracted from LinkedIn/other sources
                "business_name": business.name,
                "domain": business.domain,
                "industry": business.industry,
                "key_personalizations": result.get("key_personalizations", []),
                "value_propositions_used": result.get("value_propositions_used", []),
                "confidence_score": result.get("confidence_score", "Medium"),
                "generated_by": "mistral_medium_openrouter",
            }

            return template

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            logger.warning(f"Raw response: {response[:500]}...")

            # Fallback template
            return {
                "subject": f"AI-Powered Customer Service for {business.name}",
                "body": f"""Hi there,

I noticed {business.name} in {business.industry} and wanted to reach out about our AI voice agent solution.

Our personalized AI assistants can help handle customer inquiries, provide instant responses, and improve your customer experience around the clock.

Would you be interested in learning more about how this could work for your business?

Best regards,
AI Solutions Specialist
VoiceGenius AI
hello@voicegenius.ai
(555) 123-4567""",
                "recipient_email": business.email or "",
                "recipient_name": None,
                "business_name": business.name,
                "domain": business.domain,
                "industry": business.industry,
                "key_personalizations": [f"Industry: {business.industry}", f"Business: {business.name}"],
                "value_propositions_used": ["24/7 customer support", "Instant responses", "Personalized interactions"],
                "confidence_score": "Low",
                "generated_by": "fallback_template",
            }


def main():
    """CLI interface for testing OpenRouter email generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate intelligent emails with OpenRouter")
    parser.add_argument("--business-name", required=True, help="Target business name")
    parser.add_argument("--domain", required=True, help="Business domain")
    parser.add_argument("--industry", required=True, help="Business industry")
    parser.add_argument("--agent-name", required=True, help="Voice agent name")

    args = parser.parse_args()

    try:
        # Initialize client
        client = OpenRouterClient()

        # Create contexts
        business = BusinessContext(
            name=args.business_name,
            domain=args.domain,
            industry=args.industry
        )

        agent = AgentContext(
            agent_name=args.agent_name,
            personality="professional",
            tone_keywords=["helpful", "knowledgeable", "responsive"],
            conversation_style="helpful",
            industry=args.industry,
            system_prompt="You are a helpful assistant",
            namespace=f"kb:{args.domain}"
        )

        sender = {
            "name": "AI Solutions Specialist",
            "title": "AI Solutions Specialist",
            "company": "VoiceGenius AI",
            "email": "hello@voicegenius.ai",
            "phone": "(555) 123-4567"
        }

        # Generate email
        template = client.generate_email_template(business, agent, sender)

        print("Generated Email Template:")
        print(f"Subject: {template['subject']}")
        print("\nBody:")
        print(template['body'])
        print(f"\nConfidence: {template.get('confidence_score', 'Unknown')}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
