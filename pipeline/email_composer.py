"""
Email Template Composer for Growth Automation Pipeline.

Creates personalized cold outreach emails with embedded voice agents.
Generates compelling subject lines, personalized content, and clear CTAs
that showcase the value proposition for each business.

Features:
- Personalized email templates based on industry and business data
- Embedded voice agent interactions (audio links, demo CTAs)
- Dynamic subject line generation
- Value proposition highlighting based on scraped content
- Professional formatting and compliance
- HTML template personalization using LLM intelligence
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .openrouter_client import OpenRouterClient, BusinessContext, AgentContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailTemplate:
    """Cold outreach email template with embedded voice agent."""

    subject: str
    body: str
    recipient_email: str
    recipient_name: Optional[str]
    business_name: str
    domain: str
    industry: str
    voice_agent_url: Optional[str] = None
    cta_text: str = "Try Our AI Assistant"
    personalization_notes: List[str] = None

    def __post_init__(self):
        if self.personalization_notes is None:
            self.personalization_notes = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "subject": self.subject,
            "body": self.body,
            "recipient_email": self.recipient_email,
            "recipient_name": self.recipient_name,
            "business_name": self.business_name,
            "domain": self.domain,
            "industry": self.industry,
            "voice_agent_url": self.voice_agent_url,
            "cta_text": self.cta_text,
            "personalization_notes": self.personalization_notes,
        }


@dataclass
class PersonalizedHTMLTemplate:
    """Personalized HTML email template with dynamic content."""

    hero_title: str
    hero_subtitle: str
    company_name: str
    demo_conversation: List[Dict[str, str]]
    features: List[Dict[str, str]]
    pricing_title: str
    pricing_subtitle: str
    urgency_title: str
    urgency_text: str
    voice_agent_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "hero_title": self.hero_title,
            "hero_subtitle": self.hero_subtitle,
            "company_name": self.company_name,
            "demo_conversation": self.demo_conversation,
            "features": self.features,
            "pricing_title": self.pricing_title,
            "pricing_subtitle": self.pricing_subtitle,
            "urgency_title": self.urgency_title,
            "urgency_text": self.urgency_text,
            "voice_agent_id": self.voice_agent_id,
        }


class HTMLTemplateGenerator:
    """Generates personalized HTML email templates using LLM intelligence."""

    def __init__(
        self,
        html_template_path: str = "pipeline/emails/templates/shortforge_email_cta.html",
        openrouter_config: Optional[str] = None
    ):
        """Initialize HTML template generator.

        Args:
            html_template_path: Path to base HTML template
            openrouter_config: Path to OpenRouter configuration file
        """
        self.html_template_path = Path(html_template_path)
        self.llm_client = None

        # Initialize OpenRouter client
        try:
            self.llm_client = OpenRouterClient(openrouter_config)
            logger.info("🤖 Initialized OpenRouter client for HTML template personalization")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter client: {e}")

        # Load base template
        self.base_template = self._load_base_template()

    def _load_base_template(self) -> str:
        """Load the base HTML template."""
        if not self.html_template_path.exists():
            raise FileNotFoundError(f"HTML template not found: {self.html_template_path}")

        with open(self.html_template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_personalized_content(
        self,
        business_name: str,
        domain: str,
        industry: str,
        lead_data: Dict,
        business_content: Optional[Dict[str, str]] = None
    ) -> PersonalizedHTMLTemplate:
        """Generate personalized content for HTML template using LLM.

        Args:
            business_name: Name of the business
            domain: Business domain
            industry: Business industry
            lead_data: Lead data dictionary
            business_content: Business content summary

        Returns:
            Personalized HTML template data
        """
        if not self.llm_client:
            logger.warning("No LLM client available, using default content")
            return self._get_default_content(business_name, domain, industry)

        # Create business context
        business_context = BusinessContext(
            name=business_name,
            domain=domain,
            industry=industry,
            location=lead_data.get("location"),
            email=lead_data.get("email"),
            services_content=business_content.get("services") if business_content else None,
            about_content=business_content.get("about") if business_content else None,
            team_content=business_content.get("team") if business_content else None,
            blog_content=business_content.get("blog") if business_content else None,
        )

        # Generate personalized content using LLM
        prompt = self._build_personalization_prompt(business_context, lead_data)

        try:
            response = self.llm_client._call_openrouter(prompt)
            content = self._parse_llm_response(response)
            return PersonalizedHTMLTemplate(**content)

        except Exception as e:
            logger.error(f"Failed to generate personalized content: {e}")
            return self._get_default_content(business_name, domain, industry)

    def _build_personalization_prompt(self, business_context: BusinessContext, lead_data: Dict) -> str:
        """Build the LLM prompt for content personalization."""
        return f"""You are creating personalized marketing content for ShortForge Consultancy's AI Voice Agent demo email.

Target Business Details:
- Business Name: {business_context.name}
- Industry: {business_context.industry}
- Domain: {business_context.domain}
- Location: {business_context.location or 'Unknown'}
- Email: {business_context.email or 'Unknown'}

Business Intelligence Available:
- Services: {business_context.services_content[:500] if business_context.services_content else 'Not available'}
- About: {business_context.about_content[:500] if business_context.about_content else 'Not available'}
- Team: {business_context.team_content[:500] if business_context.team_content else 'Not available'}

Your task is to create personalized, compelling content that:
1. Shows deep understanding of their business and pain points
2. Demonstrates how AI voice agents solve their specific challenges
3. Maintains the same structure and tone as the original content
4. Makes the content feel custom-built for their business

Generate content for these sections:

1. HERO_TITLE: A compelling headline (keep format similar to "See How AI Can Run Your Business")

2. HERO_SUBTITLE: A personalized subtitle explaining how AI agents help their specific business (2-3 sentences)

3. DEMO_CONVERSATION: A realistic conversation between "Forge" and a potential customer, showing how the AI understands their business. Include:
   - Forge greeting and introduction
   - Customer question about their specific industry/service
   - Forge's knowledgeable response showing business understanding
   - Forge offering more help

4. FEATURES: 3 key features personalized for their industry, each with title and description

5. PRICING_TITLE: Pricing headline (keep similar format)

6. PRICING_SUBTITLE: Personalized subtitle about their specific business needs

7. URGENCY_TEXT: Urgency message personalized for their industry

Return the content as a JSON object with these exact keys:
{{
    "hero_title": "string",
    "hero_subtitle": "string",
    "company_name": "{business_context.name}",
    "demo_conversation": [
        {{"speaker": "Forge", "message": "string"}},
        {{"speaker": "User", "message": "string"}},
        {{"speaker": "Forge", "message": "string"}},
        {{"speaker": "Forge", "message": "string"}}
    ],
    "features": [
        {{"title": "string", "description": "string"}},
        {{"title": "string", "description": "string"}},
        {{"title": "string", "description": "string"}}
    ],
    "pricing_title": "string",
    "pricing_subtitle": "string",
    "urgency_title": "string",
    "urgency_text": "string"
}}

Make it sound professional, show industry expertise, and create urgency to try the demo."""

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse the LLM response into structured data."""
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in LLM response, using default content")
                return self._get_default_content("", "", "")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return self._get_default_content("", "", "")

    def _get_default_content(self, business_name: str, domain: str, industry: str) -> PersonalizedHTMLTemplate:
        """Get default content when LLM generation fails."""
        agent_id = os.getenv("ELEVENLABS_AGENT_ID", "")
        return PersonalizedHTMLTemplate(
            hero_title="See How AI Can Run Your Business",
            hero_subtitle="Your clients, leads, and internal ops don't need to wait for a human anymore. Our AI Voice Agents can qualify leads, schedule meetings, handle customer support, and trigger backend workflows — automatically.",
            company_name=business_name or "Your Company",
            demo_conversation=[
                {"speaker": "Forge", "message": "Hey there, I'm Forge — your AI automation specialist."},
                {"speaker": "User", "message": "Can you show me how you automate lead follow-ups?"},
                {"speaker": "Forge", "message": "Absolutely. We can integrate with your CRM and send follow-ups instantly after a new inquiry."},
                {"speaker": "Forge", "message": "Ask me anything about automating your business."}
            ],
            features=[
                {"title": "AI Agents That Work Like Staff", "description": "Deploy autonomous voice and workflow agents that can talk, schedule, and execute your processes."},
                {"title": "Integrates With Your Stack", "description": "Connect to tools like Notion, Slack, Google Workspace, HubSpot, or custom APIs seamlessly."},
                {"title": "Custom-Built For You", "description": "Each system is tuned to your internal processes — not a generic chatbot."}
            ],
            pricing_title="Start Automating Without the Overhead",
            pricing_subtitle="We design and deploy your first production-ready AI agent within two weeks.",
            urgency_title="Early Access Offer — Limited Seats",
            urgency_text="We're onboarding only 10 new clients this quarter to ensure quality. Get started now and your first AI agent setup is included free.",
            voice_agent_id=agent_id
        )

    def generate_html_email(
        self,
        personalized_content: PersonalizedHTMLTemplate
    ) -> str:
        """Generate the final HTML email with personalized content.

        Args:
            personalized_content: The personalized content to insert

        Returns:
            Complete HTML email string
        """
        html = self.base_template

        # Replace placeholders with personalized content
        replacements = {
            "{{hero_title}}": personalized_content.hero_title,
            "{{hero_subtitle}}": personalized_content.hero_subtitle,
            "{{company_name}}": personalized_content.company_name,
            "{{pricing_title}}": personalized_content.pricing_title,
            "{{pricing_subtitle}}": personalized_content.pricing_subtitle,
            "{{urgency_title}}": personalized_content.urgency_title,
            "{{urgency_text}}": personalized_content.urgency_text,
            "{{voice_agent_id}}": personalized_content.voice_agent_id or "",
        }

        # Apply basic replacements
        for placeholder, content in replacements.items():
            html = html.replace(placeholder, content)

        # Handle dynamic conversation
        conversation_html = ""
        for msg in personalized_content.demo_conversation:
            conversation_html += f'        <div>&gt; {msg["speaker"]}: "{msg["message"]}"</div>\n'

        html = html.replace("        <!-- DYNAMIC_CONVERSATION_PLACEHOLDER -->", conversation_html.strip())

        # Handle dynamic features
        features_html = ""
        for feature in personalized_content.features:
            features_html += f'''      <div class="feature-item">
        <h3 class="feature-title">{feature["title"]}</h3>
        <p class="feature-desc">{feature["description"]}</p>
      </div>
'''

        html = html.replace("      <!-- DYNAMIC_FEATURES_PLACEHOLDER -->", features_html.strip())

        return html


class EmailComposer:
    """Composes personalized cold outreach emails with voice agents using LLM intelligence."""

    def __init__(
        self,
        templates_dir: str = "pipeline/config/email_templates",
        use_llm: bool = True,
        openrouter_config: Optional[str] = None,
        business_data_dir: str = "pipeline/business_data"
    ):
        """Initialize email composer.

        Args:
            templates_dir: Directory containing email templates (fallback)
            use_llm: Whether to use LLM for intelligent generation
            openrouter_config: Path to OpenRouter configuration file
            business_data_dir: Directory containing business intelligence data
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.business_data_dir = Path(business_data_dir)
        self.use_llm = use_llm

        # Initialize OpenRouter client for intelligent generation
        if use_llm:
            try:
                self.llm_client = OpenRouterClient(openrouter_config)
                logger.info("🤖 Initialized OpenRouter client for intelligent email generation")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenRouter client: {e}. Falling back to templates.")
                self.use_llm = False
                self.llm_client = None

        # Initialize HTML template generator
        try:
            self.html_generator = HTMLTemplateGenerator(
                html_template_path="pipeline/emails/templates/shortforge_email_cta.html",
                openrouter_config=openrouter_config
            )
            logger.info("📧 Initialized HTML template generator")
        except Exception as e:
            logger.warning(f"Failed to initialize HTML template generator: {e}")
            self.html_generator = None

        # Load fallback templates
        if not use_llm:
            self.templates = self._load_templates()
            logger.info("📝 Using template-based email generation")

    def _load_templates(self) -> Dict[str, Dict]:
        """Load email templates for different industries."""
        templates_file = self.templates_dir / "templates.json"

        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load email templates: {e}")

        # Default templates
        return {
            "default": {
                "subject_templates": [
                    "AI-Powered Customer Service for {business_name}",
                    "Transform Your {industry} Business with Voice AI",
                    "{business_name} + AI: Better Customer Experience",
                    "Meet Your New AI Receptionist - Powered by {business_name}'s Expertise",
                ],
                "body_template": """
Hi {recipient_name},

I hope this email finds you well. My name is {sender_name} and I'm reaching out because I believe there's an opportunity to enhance how {business_name} connects with customers.

As a leader in {industry}, you likely receive numerous inquiries daily about your services, scheduling, and general questions. What if you could provide instant, accurate responses 24/7 while your team focuses on what they do best?

🎤 **Try Our AI Voice Assistant**

We've created a custom AI assistant trained specifically on {business_name}'s services, expertise, and unique value proposition. It can:

{value_proposition}

**Live Demo:** Click here to experience the assistant yourself
{voice_agent_url}

This isn't a generic chatbot - it's built from your website content, service descriptions, and industry knowledge to provide genuinely helpful responses that align with your brand.

Would you be open to a quick 5-minute call to see how this could work for {business_name}? I'm available {availability} or we can schedule for a time that works better.

Best regards,
{sender_name}
{sender_title}
{sender_company}
{sender_phone}
{sender_email}
""",
                "industry_specific": {
                    "dentists": {
                        "value_props": [
                            "• Answer questions about services, hours, and insurance",
                            "• Help patients schedule appointments instantly",
                            "• Provide information about emergency care and procedures",
                            "• Share details about your team's expertise and credentials"
                        ],
                        "pain_points": ["patient scheduling", "after-hours inquiries", "service questions"]
                    },
                    "law_firms": {
                        "value_props": [
                            "• Answer basic legal questions and service information",
                            "• Help potential clients understand your practice areas",
                            "• Provide intake form information and next steps",
                            "• Share attorney availability and consultation details"
                        ],
                        "pain_points": ["client intake", "service inquiries", "consultation scheduling"]
                    },
                    "hvac": {
                        "value_props": [
                            "• Answer questions about service areas and availability",
                            "• Help customers schedule maintenance and repairs",
                            "• Provide emergency service information",
                            "• Share details about your warranty and service guarantees"
                        ],
                        "pain_points": ["emergency calls", "service scheduling", "customer inquiries"]
                    }
                }
            }
        }

    def compose_email(
        self,
        business_name: str,
        domain: str,
        industry: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        voice_agent_url: Optional[str] = None,
        content_summary: Optional[Dict[str, str]] = None
    ) -> EmailTemplate:
        """Compose personalized email for a business lead.

        Args:
            business_name: Name of the target business
            domain: Business domain
            industry: Business industry
            recipient_email: Recipient email address
            recipient_name: Recipient name (if known)
            voice_agent_url: URL to the voice agent demo
            content_summary: Summary of business content

        Returns:
            Composed email template
        """
        logger.info(f"📧 Composing email for {business_name} ({recipient_email})")

        if self.use_llm and self.llm_client:
            # Use intelligent LLM-based generation
            return self._compose_email_with_llm(
                business_name, domain, industry, recipient_email,
                recipient_name, voice_agent_url, content_summary
            )
        else:
            # Fall back to template-based generation
            return self._compose_email_with_templates(
                business_name, domain, industry, recipient_email,
                recipient_name, voice_agent_url, content_summary
            )

    def _compose_email_with_llm(
        self,
        business_name: str,
        domain: str,
        industry: str,
        recipient_email: str,
        recipient_name: Optional[str],
        voice_agent_url: Optional[str],
        content_summary: Optional[Dict[str, str]]
    ) -> EmailTemplate:
        """Compose email using LLM intelligence.

        Args:
            Same as compose_email method.

        Returns:
            LLM-generated email template
        """
        # Create business context
        business_context = BusinessContext(
            name=business_name,
            domain=domain,
            industry=industry,
            email=recipient_email,
            location=None,  # Would be extracted from lead data
            services_content=content_summary.get("services") if content_summary else None,
            about_content=content_summary.get("about") if content_summary else None,
            team_content=content_summary.get("team") if content_summary else None,
            blog_content=content_summary.get("blog") if content_summary else None,
        )

        # Load agent context
        agent_context = self._load_agent_context(domain, business_name, industry)

        # Set up sender information
        sender_info = {
            "name": os.getenv("SENDER_NAME", "AI Solutions Specialist"),
            "title": os.getenv("SENDER_TITLE", "AI Solutions Specialist"),
            "company": os.getenv("SENDER_COMPANY", "VoiceGenius AI"),
            "email": os.getenv("SENDER_EMAIL", "hello@voicegenius.ai"),
            "phone": os.getenv("SENDER_PHONE", "(555) 123-4567"),
        }

        # Generate email with LLM

        llm_template = self.llm_client.generate_email_template(
            business_context, agent_context, sender_info
        )

        # Convert to EmailTemplate format
        template = EmailTemplate(
            subject=llm_template["subject"],
            body=llm_template["body"],
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            business_name=business_name,
            domain=domain,
            industry=industry,
            voice_agent_url=voice_agent_url,
            personalization_notes=llm_template.get("key_personalizations", [])
        )

        # Add LLM metadata
        template.personalization_notes.extend([
            f"Generated by: {llm_template.get('generated_by', 'unknown')}",
            f"Confidence: {llm_template.get('confidence_score', 'unknown')}",
            f"Value Props: {', '.join(llm_template.get('value_propositions_used', []))}"
        ])

        logger.info(f"✅ Generated intelligent email with subject: {template.subject}")
        return template

    def _compose_email_with_templates(
        self,
        business_name: str,
        domain: str,
        industry: str,
        recipient_email: str,
        recipient_name: Optional[str],
        voice_agent_url: Optional[str],
        content_summary: Optional[Dict[str, str]]
    ) -> EmailTemplate:
        """Compose email using fallback templates.

        Args:
            Same as compose_email method.

        Returns:
            Template-based email template
        """
        # Generate subject line
        subject = self._generate_subject(business_name, industry)

        # Generate personalized body
        body = self._generate_body(
            business_name=business_name,
            domain=domain,
            industry=industry,
            recipient_name=recipient_name,
            voice_agent_url=voice_agent_url,
            content_summary=content_summary
        )

        # Extract personalization notes
        personalization_notes = self._extract_personalization_notes(content_summary or {})

        template = EmailTemplate(
            subject=subject,
            body=body,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            business_name=business_name,
            domain=domain,
            industry=industry,
            voice_agent_url=voice_agent_url,
            personalization_notes=personalization_notes
        )

        logger.info(f"✅ Composed template-based email with subject: {subject}")
        return template

    def _load_agent_context(self, domain: str, business_name: str, industry: str) -> AgentContext:
        """Load agent context for a business domain.

        Args:
            domain: Business domain
            business_name: Business name
            industry: Business industry

        Returns:
            AgentContext for the business
        """
        agent_file = Path("pipeline/agents") / domain.replace(".", "_") / "agent_request.json"

        if agent_file.exists():
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent_payload = json.load(f)

                conversation_config = agent_payload.get("conversation_config", {})
                agent_section = conversation_config.get("agent", {})
                prompt_section = agent_section.get("prompt", {})

                return AgentContext(
                    agent_name=agent_payload.get("name", f"{business_name} Assistant"),
                    personality="professional",
                    tone_keywords=["helpful", "knowledgeable", "responsive"],
                    conversation_style="helpful",
                    industry=industry,
                    system_prompt=prompt_section.get("prompt", "You are a helpful assistant for this business."),
                    namespace=f"kb:{domain}",
                    demo_url=f"https://your-app.com/voice-agent/{domain.replace('.', '_')}"
                )
            except Exception as e:
                logger.warning(f"Failed to load agent config for {domain}: {e}")

        # Return default agent context
        return AgentContext(
            agent_name=f"{business_name} Assistant",
            personality="professional",
            tone_keywords=["helpful", "knowledgeable", "responsive"],
            conversation_style="helpful",
            industry=industry,
            system_prompt="You are a helpful AI assistant for this business.",
            namespace=f"kb:{domain}",
            demo_url=f"https://your-app.com/voice-agent/{domain.replace('.', '_')}"
        )

    def _generate_subject(self, business_name: str, industry: str) -> str:
        """Generate compelling subject line for the email.

        Args:
            business_name: Target business name
            industry: Business industry

        Returns:
            Personalized subject line
        """
        templates = self.templates["default"]["subject_templates"]

        # Select template based on industry context
        industry_lower = industry.lower().replace(" ", "_")

        if industry_lower in ["dentists", "law_firms", "hvac"]:
            # Use more specific subject for known industries
            industry_specific_subjects = {
                "dentists": [
                    f"AI Patient Assistant for {business_name}",
                    f"24/7 Patient Support for {business_name}",
                    f"Transform Patient Experience at {business_name}"
                ],
                "law_firms": [
                    f"AI Client Intake for {business_name}",
                    f"Modern Client Service for {business_name}",
                    f"AI-Powered Legal Intake at {business_name}"
                ],
                "hvac": [
                    f"AI Service Assistant for {business_name}",
                    f"24/7 Customer Support for {business_name}",
                    f"Smart Service Scheduling for {business_name}"
                ]
            }
            templates = industry_specific_subjects.get(industry_lower, templates)

        # Select random template and fill in variables
        import random
        template = random.choice(templates)

        return template.format(business_name=business_name, industry=industry)

    def _generate_body(
        self,
        business_name: str,
        domain: str,
        industry: str,
        recipient_name: Optional[str],
        voice_agent_url: Optional[str],
        content_summary: Optional[Dict[str, str]]
    ) -> str:
        """Generate personalized email body.

        Args:
            business_name: Target business name
            domain: Business domain
            industry: Business industry
            recipient_name: Recipient name
            voice_agent_url: Voice agent demo URL
            content_summary: Business content summary

        Returns:
            Formatted email body
        """
        template = self.templates["default"]["body_template"]

        # Get industry-specific content
        industry_config = self.templates["default"]["industry_specific"].get(
            industry.lower().replace(" ", "_"),
            {}
        )

        # Extract value proposition
        value_proposition = self._extract_value_proposition(industry_config, content_summary)

        # Fill in template variables
        body = template.format(
            recipient_name=recipient_name or "there",
            sender_name=os.getenv("SENDER_NAME", "Alex Johnson"),
            business_name=business_name,
            industry=industry.lower(),
            value_proposition=value_proposition,
            voice_agent_url=voice_agent_url or "[Voice Agent Demo Link]",
            availability="next Tuesday at 2 PM",
            sender_title=os.getenv("SENDER_TITLE", "AI Solutions Specialist"),
            sender_company=os.getenv("SENDER_COMPANY", "VoiceGenius AI"),
            sender_phone=os.getenv("SENDER_PHONE", "(555) 123-4567"),
            sender_email=os.getenv("SENDER_EMAIL", "alex@voicegenius.ai")
        )

        return body.strip()

    def _extract_value_proposition(
        self,
        industry_config: Dict,
        content_summary: Optional[Dict[str, str]]
    ) -> str:
        """Extract value proposition bullets from industry config and content.

        Args:
            industry_config: Industry-specific configuration
            content_summary: Business content summary

        Returns:
            Formatted value proposition text
        """
        value_props = industry_config.get("value_props", [
            "• Provide instant responses to common questions",
            "• Handle basic inquiries while your team focuses on complex issues",
            "• Offer 24/7 availability for customer support",
            "• Deliver consistent, accurate information"
        ])

        # Personalize based on content if available
        if content_summary:
            services = content_summary.get("services", "").lower()

            # Add personalized value props based on content
            if "emergency" in services or "urgent" in services:
                value_props.append("• Handle emergency inquiries outside business hours")
            if "scheduling" in services or "appointment" in services:
                value_props.append("• Help customers schedule appointments instantly")
            if "pricing" in services or "cost" in services:
                value_props.append("• Provide clear pricing and service information")

        return "\n".join(value_props[:6])  # Limit to 6 points

    def _extract_personalization_notes(self, content_summary: Dict[str, str]) -> List[str]:
        """Extract notes about personalization for follow-up.

        Args:
            content_summary: Business content summary

        Returns:
            List of personalization notes
        """
        notes = []

        if content_summary.get("services"):
            notes.append("Email mentions specific services found on website")

        if content_summary.get("team"):
            notes.append("References team expertise and credentials")

        if content_summary.get("about"):
            notes.append("Includes company mission/values from About page")

        if not notes:
            notes.append("Standard template used - no specific content personalization")

        return notes

    def compose_personalized_html_email(
        self,
        business_name: str,
        domain: str,
        industry: str,
        lead_data: Dict,
        business_content: Optional[Dict[str, str]] = None,
        voice_agent_id: Optional[str] = None
    ) -> str:
        """Compose a personalized HTML email using LLM intelligence.

        Args:
            business_name: Name of the business
            domain: Business domain
            industry: Business industry
            lead_data: Lead data dictionary
            business_content: Business content summary
            voice_agent_id: ElevenLabs agent ID for the widget

        Returns:
            Complete HTML email string
        """
        if not self.html_generator:
            logger.warning("HTML generator not available, falling back to text template")
            text_template = self.compose_email(
                business_name=business_name,
                domain=domain,
                industry=industry,
                recipient_email=lead_data.get("email", ""),
                recipient_name=None,
                voice_agent_url=None,
                content_summary=business_content
            )
            return self._convert_text_to_html(text_template.body)

        logger.info(f"🎨 Generating personalized HTML email for {business_name}")

        # Generate personalized content
        personalized_content = self.html_generator.generate_personalized_content(
            business_name=business_name,
            domain=domain,
            industry=industry,
            lead_data=lead_data,
            business_content=business_content
        )

        # Set voice agent ID if provided, otherwise use environment variable
        if voice_agent_id:
            personalized_content.voice_agent_id = voice_agent_id
        else:
            personalized_content.voice_agent_id = os.getenv("ELEVENLABS_AGENT_ID", "")

        # Generate final HTML
        html_email = self.html_generator.generate_html_email(personalized_content)

        logger.info(f"✅ Generated personalized HTML email for {business_name}")
        return html_email

    def _convert_text_to_html(self, text: str) -> str:
        """Convert plain text email to basic HTML format.

        Args:
            text: Plain text email body

        Returns:
            Basic HTML formatted email
        """
        # Basic HTML conversion - preserve line breaks and add some styling
        html = text.replace('\n', '<br>')
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .cta {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        return html

    def save_email_template(self, template: EmailTemplate, emails_dir: str = "pipeline/emails") -> None:
        """Save email template to file.

        Args:
            template: Email template to save
            emails_dir: Directory to save emails
        """
        emails_path = Path(emails_dir)
        emails_path.mkdir(parents=True, exist_ok=True)

        # Create filename from domain
        filename = f"{template.domain.replace('.', '_')}.json"
        filepath = emails_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)

        # Also save as markdown for easy reading
        md_filename = f"{template.domain.replace('.', '_')}.md"
        md_filepath = emails_path / md_filename

        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Email to {template.business_name}\n\n")
            f.write(f"**Subject:** {template.subject}\n\n")
            f.write(f"**To:** {template.recipient_email}")
            if template.recipient_name:
                f.write(f" ({template.recipient_name})")
            f.write(f"\n\n**Industry:** {template.industry}\n\n")
            f.write("---\n\n")
            f.write(template.body)
            f.write("\n\n---\n\n")
            if template.personalization_notes:
                f.write("**Personalization Notes:**\n")
                for note in template.personalization_notes:
                    f.write(f"- {note}\n")

        logger.info(f"💾 Saved email template to {filepath}")

    def compose_email_for_lead(
        self,
        lead_domain: str,
        emails_dir: str = "pipeline/emails"
    ) -> Optional[EmailTemplate]:
        """Compose email for a lead by loading business data.

        Args:
            lead_domain: Domain of the lead business
            emails_dir: Directory to save emails

        Returns:
            Composed email template if successful
        """
        try:
            # Load lead data
            lead_data = self._load_lead_data(lead_domain)
            if not lead_data:
                logger.error(f"❌ No lead data found for {lead_domain}")
                return None

            # Load business content summary
            content_summary = self._load_business_content(lead_domain)

            # Generate voice agent URL (placeholder for now)
            voice_agent_url = f"https://your-app.com/voice-agent/{lead_domain.replace('.', '_')}"

            # Compose email
            template = self.compose_email(
                business_name=lead_data["name"],
                domain=lead_domain,
                industry=lead_data.get("industry", "general"),
                recipient_email=lead_data.get("email", ""),
                recipient_name=None,  # Could be extracted from LinkedIn later
                voice_agent_url=voice_agent_url,
                content_summary=content_summary
            )

            # Save template
            self.save_email_template(template, emails_dir)

            return template

        except Exception as e:
            logger.error(f"❌ Failed to compose email for {lead_domain}: {e}")
            return None

    def _load_lead_data(self, domain: str) -> Optional[Dict]:
        """Load lead data for a domain.

        Args:
            domain: Business domain

        Returns:
            Lead data dictionary or None
        """
        leads_dir = Path("pipeline/leads")
        domain_file = None

        # Find the most recent lead file for this domain
        for json_file in leads_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    lead_data = json.load(f)
                    if isinstance(lead_data, list):
                        for lead in lead_data:
                            if lead.get("domain") == domain:
                                return lead
                    elif isinstance(lead_data, dict) and lead_data.get("domain") == domain:
                        return lead_data
            except Exception:
                continue

        return None

    def _load_business_content(self, domain: str) -> Dict[str, str]:
        """Load business content summary for personalization.

        Args:
            domain: Business domain

        Returns:
            Content summary by type
        """
        data_dir = self.business_data_dir / domain.replace(".", "_")
        content_file = data_dir / "content.json"

        if not content_file.exists():
            return {}

        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content_data = json.load(f)

            summaries = {}
            for content_type, items in content_data.items():
                if items:
                    # Summarize content (take first meaningful chunks)
                    combined_content = " ".join([item["content"][:300] for item in items[:2]])
                    summaries[content_type] = combined_content

            return summaries

        except Exception as e:
            logger.error(f"Failed to load business content for {domain}: {e}")
            return {}


def test_personalized_html_generation():
    """Test personalized HTML email generation."""
    import json

    # Sample lead data
    lead_data = {
        "name": "Kaori Ema",
        "email": "smile@prdentalstudio.com",
        "location": "Chicago",
        "industry": "dentist",
        "domain": "prdentalstudio.com"
    }

    # Sample business content
    business_content = {
        "services": "We offer comprehensive dental services including cosmetic dentistry, restorative procedures, and preventive care. Our team specializes in advanced treatments and patient comfort.",
        "about": "Printers Row Dental Studio has been serving Chicago for over 20 years with a commitment to exceptional patient care and the latest dental technologies.",
        "team": "Dr. Kaori Ema leads our practice with expertise in cosmetic and general dentistry. Our skilled team provides personalized care in a comfortable environment."
    }

    composer = EmailComposer()

    print("🎨 Testing personalized HTML email generation...")
    html_email = composer.compose_personalized_html_email(
        business_name="Printers Row Dental Studio",
        domain="prdentalstudio.com",
        industry="dentist",
        lead_data=lead_data,
        business_content=business_content,
        voice_agent_id=os.getenv("ELEVENLABS_AGENT_ID")
    )

    # Save the generated HTML for inspection
    with open("test_personalized_email.html", "w", encoding="utf-8") as f:
        f.write(html_email)

    print("✅ Personalized HTML email generated and saved to test_personalized_email.html")
    print(f"📧 Email length: {len(html_email)} characters")

    # Check if placeholders were replaced
    placeholders = ["{{hero_title}}", "{{hero_subtitle}}", "{{company_name}}", "{{voice_agent_id}}"]
    missing_placeholders = [p for p in placeholders if p in html_email]

    if missing_placeholders:
        print(f"⚠️  Warning: Some placeholders not replaced: {missing_placeholders}")
    else:
        print("✅ All placeholders successfully replaced")

    return html_email


def main():
    """CLI interface for email composition."""
    import argparse

    parser = argparse.ArgumentParser(description="Compose personalized emails")
    parser.add_argument("--domain", help="Business domain")
    parser.add_argument("--emails-dir", default="pipeline/emails", help="Emails storage directory")
    parser.add_argument("--test-html", action="store_true", help="Test personalized HTML generation")

    args = parser.parse_args()

    if args.test_html:
        test_personalized_html_generation()
        return

    if not args.domain:
        parser.error("Must specify --domain or use --test-html")

    composer = EmailComposer()
    template = composer.compose_email_for_lead(args.domain, args.emails_dir)

    if template:
        print(f"Successfully composed email for {template.business_name}")
        print(f"Subject: {template.subject}")
        print(f"Recipient: {template.recipient_email}")
        print(f"Saved to: {args.emails_dir}/{template.domain.replace('.', '_')}.md")
    else:
        print("Failed to compose email")
        exit(1)


if __name__ == "__main__":
    main()
