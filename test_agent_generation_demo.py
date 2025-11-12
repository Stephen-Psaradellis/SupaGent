#!/usr/bin/env python3
"""
Demonstration script showing voice agent generation with mock business data.

This script showcases the VoiceAgentGenerator's capabilities using realistic
mock data for different types of businesses, demonstrating:
- Content analysis and personality extraction
- System prompt generation
- Full agent configuration creation
- ElevenLabs integration (mocked)
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from pipeline.voice_agent_generator import VoiceAgentGenerator, AgentConfig


def create_mock_business_data():
    """Create mock business data for testing different scenarios."""
    return {
        "dentist": {
            "name": "Bright Smile Dental",
            "domain": "brightsmiledental.com",
            "industry": "dentistry",
            "content": {
                "services": """
                We offer comprehensive dental care including preventive dentistry,
                cosmetic dentistry, restorative procedures, and emergency dental services.
                Our experienced team provides gentle, professional care in a comfortable
                environment. We specialize in teeth whitening, dental implants, root canals,
                and orthodontic treatments. Patient comfort and trust are our top priorities.
                """,
                "about": """
                Bright Smile Dental has been serving our community for over 15 years.
                Our mission is to provide exceptional dental care with compassion and expertise.
                We believe every patient deserves a healthy, confident smile. Our state-of-the-art
                facility combines advanced technology with a caring approach to make your
                dental visits as comfortable as possible.
                """,
                "team": """
                Dr. Sarah Johnson leads our practice with 20+ years of experience.
                Our hygienists are certified professionals dedicated to preventive care.
                We invest in ongoing education to stay current with the latest dental techniques.
                """,
                "blog": """
                Regular dental check-ups are essential for maintaining oral health.
                We recommend visiting every 6 months for professional cleaning and examination.
                Early detection of dental issues can prevent more serious problems.
                """
            }
        },
        "restaurant": {
            "name": "Bella Vista Italian Kitchen",
            "domain": "bellavista.com",
            "industry": "restaurant",
            "content": {
                "services": """
                Welcome to Bella Vista! We're excited to serve you authentic Italian cuisine
                made with fresh, local ingredients. Our menu features traditional pasta dishes,
                wood-fired pizzas, and homemade desserts. We cater to special events and offer
                takeout and delivery services. Our warm, welcoming atmosphere makes every
                meal memorable. Please join us for lunch or dinner!
                """,
                "about": """
                Bella Vista has been a family favorite for over 10 years. We pride ourselves
                on using only the finest ingredients and traditional Italian cooking methods.
                Our chefs bring authentic recipes from Italy, creating dishes that transport
                you to the heart of Tuscany. We love making our guests feel like part of the family.
                """,
                "team": """
                Our passionate team includes chefs with years of experience in Italian cuisine.
                We're here to make your dining experience exceptional. Whether you need menu
                recommendations or dietary accommodations, we're happy to help!
                """,
                "blog": """
                Try our new seasonal specials featuring fresh, local ingredients.
                We accommodate gluten-free, vegetarian, and vegan preferences.
                Our wine list features selections from Italian vineyards.
                """
            }
        },
        "hvac": {
            "name": "Comfort First HVAC",
            "domain": "comfortfirsthvac.com",
            "industry": "hvac",
            "content": {
                "services": """
                Comfort First HVAC provides reliable heating, ventilation, and air conditioning
                services for residential and commercial properties. We offer 24/7 emergency
                repairs, preventive maintenance, system installations, and energy-efficient
                upgrades. Our certified technicians are experienced and trustworthy.
                We guarantee quality work and customer satisfaction.
                """,
                "about": """
                For over 25 years, Comfort First HVAC has been the trusted name in heating
                and cooling services. We understand that when your HVAC system fails, you need
                fast, reliable service. Our commitment to excellence and integrity has made us
                the go-to choice for homeowners and businesses in our community.
                """,
                "team": """
                Our certified technicians have extensive training and experience.
                We invest in ongoing education to stay current with the latest technology.
                Safety and professionalism are our top priorities.
                """,
                "blog": """
                Regular HVAC maintenance can extend system life and reduce energy costs.
                Schedule your annual tune-up to ensure optimal performance.
                We offer emergency service 24/7 for your peace of mind.
                """
            }
        },
        "consulting": {
            "name": "Strategic Solutions Consulting",
            "domain": "strategicsolutions.com",
            "industry": "consulting",
            "content": {
                "services": """
                Strategic Solutions Consulting provides expert business consulting services
                including strategic planning, operational efficiency, digital transformation,
                and leadership development. Our experienced consultants deliver measurable
                results through data-driven approaches and proven methodologies.
                We partner with clients to achieve sustainable growth and competitive advantage.
                """,
                "about": """
                With over 50 successful projects, Strategic Solutions Consulting has established
                itself as a trusted advisor to growing businesses. Our expertise spans multiple
                industries, and our consultants bring deep knowledge and practical experience
                to every engagement. We believe in building long-term partnerships with our clients.
                """,
                "team": """
                Our team includes certified consultants with advanced degrees and industry certifications.
                We maintain the highest professional standards and adhere to strict confidentiality
                protocols. Our diverse expertise allows us to tackle complex business challenges.
                """,
                "blog": """
                Digital transformation is essential for business growth in today's marketplace.
                Effective leadership development drives organizational success.
                Data-driven decision making leads to better business outcomes.
                """
            }
        }
    }


def demonstrate_personality_analysis():
    """Demonstrate content analysis and personality extraction."""
    print("🧠 Personality Analysis Demonstration")
    print("=" * 50)

    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = VoiceAgentGenerator(
            agents_dir=os.path.join(temp_dir, "agents"),
            use_llm=False
        )

        business_data = create_mock_business_data()

        for business_type, data in business_data.items():
            print(f"\n📊 Analyzing {data['name']} ({business_type}):")

            # Analyze content
            industry_config = generator.templates["default"]["industry_defaults"].get(
                data["industry"], generator.templates["default"]["industry_defaults"]["general"]
            )

            personality, tone_keywords, conversation_style = generator._analyze_business_content(
                data["content"], industry_config
            )

            print(f"   Personality: {personality.title()}")
            print(f"   Tone Keywords: {', '.join(tone_keywords)}")
            print(f"   Conversation Style: {conversation_style.title()}")


def demonstrate_prompt_generation():
    """Demonstrate system prompt generation with different personalities."""
    print("\n\n📝 System Prompt Generation Demonstration")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        generator = VoiceAgentGenerator(
            agents_dir=os.path.join(temp_dir, "agents"),
            use_llm=False
        )

        # Test different personality types
        test_cases = [
            ("Professional Expert", "consulting", "expert", ["authoritative", "knowledgeable"]),
            ("Friendly Welcoming", "restaurant", "friendly", ["approachable", "enthusiastic"]),
            ("Reliable Trustworthy", "hvac", "reliable", ["responsive", "experienced"]),
        ]

        for case_name, industry, personality, tone_keywords in test_cases:
            print(f"\n🎭 {case_name} Prompt:")

            content_summary = {
                "services": f"Professional {industry} services with expertise and reliability.",
                "about": f"Trusted {industry} business with years of experience.",
                "team": f"Experienced {industry} professionals dedicated to quality."
            }

            prompt = generator._generate_system_prompt(
                business_name=f"Test {industry.title()} Business",
                industry=industry,
                content_summary=content_summary,
                personality=personality,
                tone_keywords=tone_keywords
            )

            # Show first 300 characters
            print(f"   {prompt[:300]}...")
            print(f"   Total length: {len(prompt)} characters")


def demonstrate_full_agent_creation():
    """Demonstrate complete agent creation pipeline."""
    print("\n\n🚀 Full Agent Creation Pipeline Demonstration")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock ElevenLabs to avoid API calls
        with patch('pipeline.voice_agent_generator.get_config') as mock_get_config, \
             patch('elevenlabs.client.ElevenLabs') as mock_elevenlabs_class:

            # Setup mocks
            mock_config = Mock()
            mock_config.elevenlabs_api_key = "test_key"
            mock_get_config.return_value = mock_config

            mock_client = Mock()
            mock_agent = Mock()
            mock_agent.id = "agent_123"
            mock_agent.voice_id = "voice_456"
            mock_client.agents.create.return_value = mock_agent
            mock_elevenlabs_class.return_value = mock_client

            generator = VoiceAgentGenerator(
                agents_dir=os.path.join(temp_dir, "agents"),
                business_data_dir=os.path.join(temp_dir, "business_data"),
                use_llm=False
            )

            business_data = create_mock_business_data()

            for business_type, data in business_data.items():
                print(f"\n🏢 Creating agent for {data['name']}:")
                print(f"   Industry: {data['industry']}")
                print(f"   Domain: {data['domain']}")

                # Create business data file
                business_dir = Path(temp_dir) / "business_data" / data['domain'].replace(".", "_")
                business_dir.mkdir(parents=True, exist_ok=True)

                content_file = business_dir / "content.json"
                with open(content_file, 'w') as f:
                    json.dump(data["content"], f, indent=2)

                # Generate agent
                config = generator.generate_agent_for_business(
                    domain=data["domain"],
                    business_name=data["name"],
                    industry=data["industry"],
                    create_elevenlabs=True
                )

                if config:
                    print("   ✅ Agent created successfully!")
                    print(f"   Agent Name: {config.agent_name}")
                    print(f"   Personality: {config.personality.title()}")
                    print(f"   ElevenLabs Agent ID: {config.voice_id}")
                    print(f"   System Prompt Length: {len(config.system_prompt)} characters")

                    # Show config file location
                    config_file = Path(temp_dir) / "agents" / data['domain'].replace(".", "_") / "agent_request.json"
                    print(f"   Config saved to: {config_file}")
                else:
                    print("   ❌ Agent creation failed")

                print()


def demonstrate_cli_usage():
    """Show example CLI commands."""
    print("\n\n💻 CLI Usage Examples")
    print("=" * 30)

    examples = [
        "python pipeline/voice_agent_generator.py --domain example.com --business-name 'Example Business' --industry general",
        "python pipeline/voice_agent_generator.py --domain brightsmiledental.com --business-name 'Bright Smile Dental' --industry dentistry --create-elevenlabs",
        "python pipeline/voice_agent_generator.py --domain bellavista.com --business-name 'Bella Vista Italian' --industry restaurant",
    ]

    for example in examples:
        print(f"$ {example}")

    print("\n📁 Generated configurations are saved to: pipeline/agents/[domain]/agent_request.json")


def main():
    """Run all demonstrations."""
    print("🎤 Voice Agent Generation Demo with Mock Data")
    print("=" * 55)
    print("This demo showcases the VoiceAgentGenerator's capabilities")
    print("using realistic mock business data.\n")

    try:
        demonstrate_personality_analysis()
        demonstrate_prompt_generation()
        demonstrate_full_agent_creation()
        demonstrate_cli_usage()

        print("\n\n🎉 Demo completed successfully!")
        print("\nThe VoiceAgentGenerator can:")
        print("• 🤖 Analyze business content to extract personality and tone")
        print("• 📝 Generate optimized system prompts for voice agents")
        print("• 🎭 Create industry-specific agent configurations")
        print("• 🔧 Integrate with ElevenLabs for voice agent creation")
        print("• 💾 Save configurations for deployment and management")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
