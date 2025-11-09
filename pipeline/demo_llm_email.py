#!/usr/bin/env python3
"""
Demo script showing LLM-powered email generation.

This script demonstrates how the new OpenRouter integration creates
intelligent, personalized cold outreach emails based on business data.

Usage:
    python pipeline/demo_llm_email.py
"""

from pipeline.openrouter_client import OpenRouterClient, BusinessContext, AgentContext


def demo_llm_email_generation():
    """Demonstrate LLM-powered email generation."""

    print("🤖 Demo: LLM-Powered Email Generation")
    print("=" * 50)

    # Note: This demo uses mock data since it requires API keys
    # In production, set OPENROUTER_API_KEY environment variable

    print("\n📊 Creating business context...")

    # Example business context
    business = BusinessContext(
        name="Bright Smile Dental",
        domain="brightsmiledental.com",
        industry="dentists",
        email="info@brightsmiledental.com",
        location="Chicago, IL",
        services_content="""
        We provide comprehensive dental care including preventive dentistry,
        cosmetic procedures, restorative treatments, and emergency care.
        Our services include teeth cleanings, fillings, root canals,
        dental implants, teeth whitening, and orthodontic treatments.
        """,
        about_content="""
        Bright Smile Dental has been serving the Chicago community for over 15 years.
        We are a family-owned practice committed to providing exceptional dental care
        in a comfortable, welcoming environment. Our experienced team uses the latest
        technology to ensure the best possible outcomes for our patients.
        """,
        team_content="""
        Dr. Sarah Johnson - Lead Dentist with 18 years experience
        Dr. Michael Chen - Prosthodontist specializing in dental implants
        Lisa Rodriguez - Registered Dental Hygienist
        """,
        blog_content="""
        Recent articles about the importance of preventive care,
        advances in cosmetic dentistry, and tips for maintaining oral health.
        """
    )

    print(f"✅ Business: {business.name}")
    print(f"✅ Industry: {business.industry}")
    print(f"✅ Services: {business.services_content[:100]}...")

    print("\n🎭 Creating agent context...")

    # Example agent context
    agent = AgentContext(
        agent_name="Bright Smile Assistant",
        personality="reassuring",
        tone_keywords=["caring", "experienced", "gentle", "professional", "patient-focused"],
        conversation_style="reassuring",
        industry="dentists",
        system_prompt="""
        You are Bright Smile Dental's AI assistant. You help patients with appointment scheduling,
        answer questions about services, provide information about procedures, and offer guidance
        on dental care. Always be reassuring, professional, and focus on patient comfort and care.
        """,
        namespace="kb:brightsmiledental.com",
        demo_url="https://app.voicegenius.ai/demo/bright-smile-assistant"
    )

    print(f"✅ Agent: {agent.agent_name}")
    print(f"✅ Personality: {agent.personality}")
    print(f"✅ Tone: {', '.join(agent.tone_keywords)}")

    print("\n📧 Setting up sender information...")

    # Sender information
    sender_info = {
        "name": "Dr. AI Solutions",
        "title": "AI Healthcare Specialist",
        "company": "VoiceGenius AI",
        "email": "drai@voicegenius.ai",
        "phone": "(555) 123-4567"
    }

    print(f"✅ From: {sender_info['name']} ({sender_info['email']})")

    print("\n🚀 Generating intelligent email...")

    # Note: In a real scenario, you would initialize with actual API key
    # client = OpenRouterClient()
    # template = client.generate_email_template(business, agent, sender_info)

    # For demo purposes, show what the LLM prompt would look like
    print("\n📝 LLM Prompt Preview:")
    print("-" * 30)

    prompt_preview = f"""
TARGET BUSINESS: {business.name} ({business.industry})

SERVICES: {business.services_content[:200]}...

AGENT PROFILE: {agent.personality} assistant with {agent.conversation_style} communication style

KEY GOALS:
1. Demonstrate understanding of dental practice challenges
2. Highlight how AI assistant solves patient scheduling and inquiry pain points
3. Showcase personalized, reassuring communication style
4. Include clear call-to-action for demo

VALUE PROPS TO EMPHASIZE:
• 24/7 patient inquiry handling
• Instant appointment scheduling
• Reassuring, professional responses
• Deep knowledge of dental services
• Reduced administrative burden
"""

    print(prompt_preview.strip())

    print("\n🎯 Expected LLM Output:")
    print("-" * 30)

    mock_email = """
Subject: Transform Patient Care at Bright Smile Dental with AI

Hi Dr. Johnson,

I noticed Bright Smile Dental's excellent reputation in Chicago's dental community and wanted to share an opportunity that could enhance your already outstanding patient care.

Managing patient inquiries, appointment scheduling, and providing consistent information about your comprehensive services (from preventive care to cosmetic procedures) can be time-intensive. What if you could provide instant, reassuring responses 24/7 while your team focuses on what they do best?

🤖 Meet Your New Patient Care Assistant

We've created a specialized AI assistant trained on Bright Smile Dental's services, team expertise, and commitment to patient comfort. It can:

• Answer questions about your preventive, cosmetic, and restorative services
• Help patients schedule appointments instantly
• Provide information about emergency care and your experienced team's credentials
• Offer guidance on dental procedures with your reassuring, professional tone
• Handle routine inquiries so your staff can focus on patient care

The assistant reflects Bright Smile Dental's caring approach - always professional, gentle, and focused on patient comfort.

**Experience it yourself:** Click here to try a live demo
[demo.voicegenius.ai/bright-smile-assistant]

Would you be open to a 10-minute call to see how this could work for Bright Smile Dental? I'm available Thursday afternoon or Friday morning.

Best regards,
Dr. AI Solutions
AI Healthcare Specialist
VoiceGenius AI
drai@voicegenius.ai
(555) 123-4567
"""

    print(mock_email.strip())

    print("\n📊 Email Analysis:")
    print("-" * 30)
    print("✅ Personalized to dental industry")
    print("✅ References specific services (preventive, cosmetic, restorative)")
    print("✅ Addresses pain points (inquiry management, scheduling)")
    print("✅ Matches agent personality (reassuring, professional)")
    print("✅ Includes clear call-to-action")
    print("✅ Professional formatting")

    print("\n🔑 Key Improvements Over Static Templates:")
    print("-" * 30)
    print("• Dynamic understanding of business services")
    print("• Industry-specific pain point identification")
    print("• Agent personality integration")
    print("• Contextual value proposition generation")
    print("• Real-time business intelligence incorporation")

    print("\n🎉 Demo Complete!")
    print("\nTo use in production:")
    print("1. Set OPENROUTER_API_KEY environment variable")
    print("2. Run: python pipeline/auto_outreach.py --industry dentists --location 'Chicago, IL'")
    print("3. Enjoy intelligent, personalized emails!")


if __name__ == "__main__":
    demo_llm_email_generation()
