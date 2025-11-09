#!/usr/bin/env python3
"""
Demo script showing LLM-generated ElevenLabs system prompts.

This script demonstrates how the OpenRouter integration creates
ElevenLabs-optimized system prompts using official documentation guidance.

Usage:
    python pipeline/demo_llm_agent_prompt.py
"""

from pipeline.openrouter_client import OpenRouterClient, BusinessContext, AgentContext


def demo_llm_system_prompt_generation():
    """Demonstrate LLM system prompt generation with ElevenLabs guidance."""

    print("🎭 Demo: LLM System Prompt Generation with ElevenLabs Guidance")
    print("=" * 70)

    # Note: This demo uses mock data since it requires API keys
    # In production, set OPENROUTER_API_KEY environment variable

    print("\n🏢 Creating business context...")

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

    # Example agent context (this would normally be generated)
    agent = AgentContext(
        agent_name="Bright Smile Assistant",
        personality="reassuring",
        tone_keywords=["caring", "experienced", "gentle", "professional", "patient-focused"],
        conversation_style="reassuring",
        industry="dentists",
        system_prompt="Basic prompt - will be enhanced by LLM",
        namespace="kb:brightsmiledental.com",
        demo_url="https://app.voicegenius.ai/demo/bright-smile-assistant"
    )

    print(f"✅ Agent: {agent.agent_name}")
    print(f"✅ Personality: {agent.personality}")
    print(f"✅ Tone: {', '.join(agent.tone_keywords)}")

    print("\n🤖 Generating ElevenLabs-optimized system prompt...")

    # Note: In a real scenario, you would initialize with actual API key
    # client = OpenRouterClient()
    # system_prompt = client.generate_agent_system_prompt(business, agent)

    print("\n📋 ElevenLabs Documentation Integration:")
    print("-" * 50)
    print("✅ Role Definition - Clear business context")
    print("✅ Communication Guidelines - Personality & tone")
    print("✅ Response Best Practices - Voice-optimized structure")
    print("✅ Boundaries & Escalation - Professional limitations")
    print("✅ Response Format - Spoken delivery optimization")

    print("\n📝 Expected LLM-Generated System Prompt:")
    print("-" * 50)

    mock_system_prompt = """
# Bright Smile Dental AI Assistant

## Role
You are Bright Smile Dental's official AI assistant, a knowledgeable representative specializing in dentistry. You provide accurate, helpful information about Bright Smile Dental's services and expertise.

## Business Context
About Bright Smile Dental: Bright Smile Dental has been serving the Chicago community for over 15 years. We are a family-owned practice committed to providing exceptional dental care in a comfortable, welcoming environment. Our experienced team uses the latest technology to ensure the best possible outcomes for our patients.

Services: We provide comprehensive dental care including preventive dentistry, cosmetic procedures, restorative treatments, and emergency care. Our services include teeth cleanings, fillings, root canals, dental implants, teeth whitening, and orthodontic treatments.

Team: Dr. Sarah Johnson - Lead Dentist with 18 years experience, Dr. Michael Chen - Prosthodontist specializing in dental implants, Lisa Rodriguez - Registered Dental Hygienist

## Communication Style
- **Personality**: Reassuring
- **Tone**: Caring, experienced, gentle, professional, patient-focused
- **Approach**: Professional and reassuring, empathetic toward dental anxiety

## Guidelines for Interaction
1. **Be Helpful & Accurate**: Provide clear, factual information based on Bright Smile Dental's actual services and capabilities
2. **Stay In Character**: Always represent Bright Smile Dental positively and professionally
3. **Use Natural Language**: Respond conversationally, as if speaking to a patient in the waiting room
4. **Be Concise but Complete**: Give comprehensive answers without being verbose
5. **Show Empathy**: Acknowledge dental concerns and anxiety appropriately, especially for procedures

## Response Best Practices
- Start with acknowledgment of the patient's question or concern
- Provide direct, actionable information about appointments or services
- Use the patient's name if provided during conversation
- End with an offer to help further or provide next steps
- For complex dental issues, suggest speaking with a dentist

## Boundaries & Escalation
- Only provide information that Bright Smile Dental can actually deliver
- If unsure about specific treatments or pricing, acknowledge limitations and offer to connect with a team member
- Never make promises about treatment outcomes or guarantee results
- For urgent dental issues, always recommend immediate professional care

## Response Format
- Keep responses under 2 minutes when spoken (about 250-300 words)
- Use simple, clear language avoiding complex dental terminology unless necessary
- Structure responses with clear beginning, middle, and end
- Include specific next steps or call-to-action when appropriate
- Use empathetic transitions between topics

Remember: You are the voice of Bright Smile Dental. Every interaction should reinforce trust, demonstrate dental expertise, and help patients feel comfortable and well-informed about their care.
"""

    print(mock_system_prompt.strip())

    print("\n🎯 Key ElevenLabs Optimizations:")
    print("-" * 50)
    print("✅ Voice-First Design: Written for spoken delivery")
    print("✅ Natural Conversation: Human-like interaction style")
    print("✅ Response Length: Under 2 minutes when spoken")
    print("✅ Clear Structure: Organized sections and guidelines")
    print("✅ Empathy & Helpfulness: Patient-focused communication")
    print("✅ Professional Boundaries: Appropriate escalation paths")
    print("✅ Brand Consistency: Maintains dental practice voice")

    print("\n📊 Comparison with Basic Templates:")
    print("-" * 50)
    print("❌ Basic: Generic, text-focused prompts")
    print("✅ LLM: Voice-optimized, business-specific, documentation-guided")
    print()
    print("❌ Basic: Simple personality descriptions")
    print("✅ LLM: Comprehensive communication guidelines with examples")
    print()
    print("❌ Basic: Generic boundaries")
    print("✅ LLM: Industry-specific escalation and limitation handling")

    print("\n🚀 Benefits of LLM-Generated Prompts:")
    print("-" * 50)
    print("• Contextually aware of specific business services")
    print("• Follows official ElevenLabs documentation standards")
    print("• Optimized for voice agent performance")
    print("• Includes industry-specific best practices")
    print("• Dynamically adapts to business content")

    print("\n🎉 Demo Complete!")
    print("\nTo use in production:")
    print("1. Set OPENROUTER_API_KEY environment variable")
    print("2. Run: python pipeline/auto_outreach.py --industry dentists --location 'Chicago, IL'")
    print("3. Get professionally optimized ElevenLabs system prompts!")


if __name__ == "__main__":
    demo_llm_system_prompt_generation()
