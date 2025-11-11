"""
Comprehensive Tests for Growth Automation Pipeline.

Tests cover:
- Lead generation and deduplication
- Web scraping and content extraction
- Vector store namespace isolation
- Voice agent configuration generation
- Email template composition
- Email sending simulation
- End-to-end pipeline integration
"""

import asyncio
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from pipeline.lead_generation import (
    GooglePlacesConnector,
    HTTPResult,
    Lead,
    LeadGenerator,
    LeadPipelineContext,
    LeadPipelineSettings,
    LeadQuery,
)
from pipeline.business_intelligence import BusinessIntelligenceLoader
from pipeline.voice_agent_generator import VoiceAgentGenerator, AgentConfig
from pipeline.email_composer import EmailComposer
from pipeline.email_sender import EmailSender, EmailStatus
from pipeline.auto_outreach import GrowthAutomationPipeline
from pipeline.openrouter_client import OpenRouterClient, BusinessContext, AgentContext


class TestLeadGeneration(unittest.TestCase):
    """Test lead generation engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = LeadGenerator(self.temp_dir)
        # Disable real connectors/enrichers to keep tests deterministic.
        self.generator.sources = {}
        self.generator.enrichers = {}
        self.generator.filter.min_score = 0.0

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_lead_deduplication(self):
        """Test that duplicate leads are properly deduplicated."""
        # Create leads with same domain but different sources
        leads = [
            Lead("Test Dental", "testdental.com", "Chicago, IL", "dentists", "info@testdental.com", source="google_maps"),
            Lead("Test Dental", "testdental.com", "Chicago, IL", "dentists", "info@testdental.com", source="yelp"),
        ]

        # Save leads
        self.generator._save_leads(leads, "dentists", "Chicago, IL")

        duplicate_lead = Lead(
            "Test Dental",
            "testdental.com",
            "Chicago, IL",
            "dentists",
            "info@testdental.com",
            source="stub",
        )

        class StubConnector:
            name = "stub"

            async def fetch(self, query, context):
                return [duplicate_lead]

            def is_configured(self, settings):
                return True

        self.generator.sources = {"stub": StubConnector()}

        # Generate leads again - should be deduplicated
        new_leads = self.generator.generate_leads("dentists", "Chicago, IL", limit=10, sources=["stub"])

        # Should not include the existing lead
        matching_leads = [l for l in new_leads if l.domain == "testdental.com"]
        self.assertEqual(len(matching_leads), 0)

    def test_lead_hash_generation(self):
        """Test lead hash generation for deduplication."""
        lead1 = Lead("Test", "example.com", email="test@example.com")
        lead2 = Lead("Test", "example.com", email="test@example.com")
        lead3 = Lead("Test", "example.com", email="different@example.com")

        hash1 = lead1.get_hash()
        hash2 = lead2.get_hash()
        hash3 = lead3.get_hash()

        self.assertEqual(hash1, hash2)  # Same lead
        self.assertNotEqual(hash1, hash3)  # Different email

    def test_google_places_connector_parses_results(self):
        """Ensure Google Places connector normalizes API results."""

        settings = LeadPipelineSettings.from_env(
            leads_dir=Path(self.temp_dir),
            cache_path=Path(self.temp_dir) / "cache.sqlite3",
            google_places_api_key="dummy-key",
        )

        connector = GooglePlacesConnector()

        class StubHTTP:
            """Stub HTTP client returning canned responses."""

            async def get(self, url, **kwargs):
                if "textsearch" in url:
                    return HTTPResult(
                        url=url,
                        status_code=200,
                        headers={},
                        json={
                            "results": [
                                {
                                    "place_id": "abc123",
                                    "name": "Test Dental",
                                    "formatted_address": "123 Main St",
                                    "types": ["dentist"],
                                }
                            ]
                        },
                    )
                return HTTPResult(
                    url=url,
                    status_code=200,
                    headers={},
                    json={
                        "result": {
                            "name": "Test Dental",
                            "website": "https://example.com",
                            "formatted_address": "123 Main St",
                            "formatted_phone_number": "+1-312-555-1000",
                            "url": "https://maps.google.com/?cid=abc123",
                            "business_status": "OPERATIONAL",
                        }
                    },
                )

        context = LeadPipelineContext(
            settings=settings,
            cache=self.generator.cache,
            http=StubHTTP(),
        )
        query = LeadQuery(industry="dentists", location="Chicago, IL", limit=5)
        leads = asyncio.run(connector.fetch(query, context))

        self.assertIsInstance(leads, list)
        self.assertTrue(leads)
        lead = leads[0]
        self.assertIsInstance(lead, Lead)
        self.assertEqual(lead.domain, "example.com")
        self.assertEqual(lead.source, connector.name)


class TestBusinessIntelligence(unittest.TestCase):
    """Test business intelligence loader."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = BusinessIntelligenceLoader(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pipeline.business_intelligence.requests.Session')
    def test_website_scraping(self, mock_session):
        """Test website scraping functionality."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.text = """
        <html>
        <head><title>Test Company</title></head>
        <body>
        <h1>About Us</h1>
        <p>We are a test company providing excellent services.</p>
        <h2>Services</h2>
        <p>We offer consulting and development services.</p>
        </body>
        </html>
        """
        mock_session.return_value.get.return_value = mock_response

        content = self.loader._scrape_website("https://example.com", 10)

        self.assertIsInstance(content, list)
        self.assertTrue(len(content) > 0)
        self.assertEqual(content[0].title, "Test Company")
        self.assertIn("test company", content[0].content.lower())

    def test_content_categorization(self):
        """Test content categorization by type."""
        content = [
            Mock(url="/about", title="About Us", content="We are a company", content_type="general"),
            Mock(url="/services", title="Our Services", content="We provide services", content_type="general"),
            Mock(url="/team", title="Our Team", content="Meet our experts", content_type="general"),
        ]

        categorized = self.loader._categorize_content(content)

        self.assertIn("about", categorized)
        self.assertIn("services", categorized)
        self.assertIn("team", categorized)
        self.assertIn("general", categorized)

    @patch('pipeline.business_intelligence.VectorStore')
    def test_vectorization_namespace_isolation(self, mock_vector_store):
        """Test that vectorization uses isolated namespaces."""
        mock_store_instance = Mock()
        mock_vector_store.return_value = mock_store_instance

        content = {
            "about": [Mock(url="https://example.com/about", title="About", content="About content", metadata={})],
            "services": [Mock(url="https://example.com/services", title="Services", content="Services content", metadata={})],
        }

        self.loader.vectorize_business_data("example.com", content)

        # Verify namespace is included in metadata
        call_args = mock_store_instance.add_documents.call_args
        documents = call_args[0][0]

        for doc in documents:
            self.assertEqual(doc["metadata"]["namespace"], "kb:example.com")


class TestVoiceAgentGeneration(unittest.TestCase):
    """Test voice agent generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = VoiceAgentGenerator(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_agent_config_generation(self):
        """Test agent configuration generation."""
        content_summary = {
            "about": "We are a professional dental practice with 10 years of experience.",
            "services": "We offer cleanings, fillings, and cosmetic dentistry.",
            "team": "Our team consists of experienced dentists and hygienists."
        }

        config = self.generator.generate_agent_config(
            domain="example.com",
            business_name="Example Dental",
            industry="dentists",
            content_summary=content_summary
        )

        self.assertIsInstance(config, AgentConfig)
        self.assertEqual(config.domain, "example.com")
        self.assertEqual(config.agent_name, "Example Dental Assistant")
        self.assertIn("Example Dental", config.system_prompt)
        self.assertEqual(config.namespace, "kb:example.com")

    def test_content_analysis(self):
        """Test content analysis for personality determination."""
        industry_config = {"personality": "professional", "tone_keywords": ["reliable"]}

        # Test friendly content
        friendly_content = {
            "about": "Welcome to our friendly practice! We're happy to help.",
            "services": "We love providing excellent care to our patients."
        }

        personality, keywords, style = self.generator._analyze_business_content(friendly_content, industry_config)

        # Should detect friendly tone
        self.assertIn("approachable", keywords)

    def test_system_prompt_generation(self):
        """Test system prompt generation."""
        prompt = self.generator._generate_system_prompt(
            business_name="Test Company",
            industry="dentists",
            content_summary={"services": "We provide dental care"},
            personality="professional",
            tone_keywords=["caring", "experienced"]
        )

        self.assertIn("Test Company", prompt)
        self.assertIn("dentists", prompt)
        self.assertIn("caring", prompt)
        self.assertIn("experienced", prompt)


class TestEmailComposer(unittest.TestCase):
    """Test email template composition."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.composer = EmailComposer()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_email_template_generation(self):
        """Test email template generation."""
        template = self.composer.compose_email(
            business_name="Test Dental",
            domain="testdental.com",
            industry="dentists",
            recipient_email="owner@testdental.com",
            recipient_name="Dr. Smith",
            voice_agent_url="https://app.com/agent/testdental_com"
        )

        self.assertIsInstance(template, object)  # Will be EmailTemplate
        self.assertIn("Test Dental", template.subject)
        self.assertIn("Dr. Smith", template.body)
        self.assertIn("testdental.com", template.body)

    def test_subject_line_generation(self):
        """Test subject line generation for different industries."""
        subject = self.composer._generate_subject("Test Dental", "dentists")

        self.assertIsInstance(subject, str)
        self.assertTrue(len(subject) > 10)

    def test_value_proposition_extraction(self):
        """Test value proposition extraction."""
        industry_config = {
            "value_props": [
                "• Answer questions about services",
                "• Help schedule appointments"
            ]
        }

        value_prop = self.composer._extract_value_proposition(industry_config, {})

        self.assertIn("services", value_prop)
        self.assertIn("appointments", value_prop)


class TestEmailSender(unittest.TestCase):
    """Test email sending functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sender = EmailSender(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pipeline.email_sender.requests.Session')
    def test_elasticemail_sending(self, mock_session):
        """Test ElasticEmail sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"transactionid": "test_transaction_id"}
        mock_session.return_value.post.return_value = mock_response

        template = {
            "recipient_email": "test@example.com",
            "subject": "Test Subject",
            "body": "Test body content",
            "domain": "example.com"
        }

        result = self.sender._send_via_elasticemail(template)

        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "test_transaction_id")

    def test_html_conversion(self):
        """Test plain text to HTML conversion."""
        text = "Line 1\nLine 2\n\nParagraph"
        html = self.sender._convert_text_to_html(text)

        self.assertIn("<html>", html)
        self.assertIn("<br>", html)
        self.assertIn("Line 1", html)
        self.assertIn("Line 2", html)

    def test_email_status_tracking(self):
        """Test email status tracking."""
        from datetime import datetime

        status = EmailStatus(
            domain="example.com",
            recipient_email="test@example.com",
            message_id="msg_123",
            status="sent",
            sent_at=datetime.now()
        )

        self.sender._save_email_status(status)

        # Verify status was saved
        status_file = Path(self.temp_dir) / "status" / "email_status.jsonl"
        self.assertTrue(status_file.exists())

        with open(status_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)

            saved_status = json.loads(lines[0])
            self.assertEqual(saved_status["domain"], "example.com")
            self.assertEqual(saved_status["status"], "sent")


class TestOpenRouterClient(unittest.TestCase):
    """Test OpenRouter client for LLM email generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pipeline.openrouter_client.requests.Session')
    def test_openrouter_initialization(self, mock_session):
        """Test OpenRouter client initialization."""
        # Mock environment variable
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'}):
            client = OpenRouterClient()
            self.assertIsNotNone(client.config.api_key)
            self.assertEqual(client.config.model, "mistralai/mistral-7b-instruct:free")

    def test_business_context_creation(self):
        """Test business context creation."""
        business = BusinessContext(
            name="Test Dental",
            domain="testdental.com",
            industry="dentists",
            email="info@testdental.com",
            services_content="We provide dental cleanings and fillings",
            about_content="Family-owned dental practice since 2000"
        )

        self.assertEqual(business.name, "Test Dental")
        self.assertEqual(business.industry, "dentists")
        self.assertIn("dental cleanings", business.services_content)

    def test_agent_context_creation(self):
        """Test agent context creation."""
        agent = AgentContext(
            agent_name="Test Assistant",
            personality="professional",
            tone_keywords=["helpful", "knowledgeable"],
            conversation_style="helpful",
            industry="dentists",
            system_prompt="You are a dental assistant",
            namespace="kb:testdental.com"
        )

        self.assertEqual(agent.agent_name, "Test Assistant")
        self.assertEqual(agent.personality, "professional")
        self.assertIn("helpful", agent.tone_keywords)

    @patch('pipeline.openrouter_client.requests.Session')
    def test_email_generation_prompt_building(self, mock_session):
        """Test email generation prompt building."""
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'}):
            client = OpenRouterClient()

            business = BusinessContext(
                name="Test Dental",
                domain="testdental.com",
                industry="dentists"
            )

            agent = AgentContext(
                agent_name="Test Assistant",
                personality="professional",
                tone_keywords=["helpful"],
                conversation_style="helpful",
                industry="dentists",
                system_prompt="Test prompt",
                namespace="kb:testdental.com"
            )

            sender = {"name": "Test Sender", "email": "test@email.com"}

            prompt = client._build_email_generation_prompt(business, agent, sender, {})

            self.assertIn("Test Dental", prompt)
            self.assertIn("dentists", prompt)
            self.assertIn("Test Sender", prompt)
            self.assertIn("professional", prompt)


class TestLLMEmailComposer(unittest.TestCase):
    """Test LLM-powered email composition."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.composer = EmailComposer(use_llm=False)  # Use template fallback for testing

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_agent_context_loading(self):
        """Test loading agent context from configuration."""
        # Create mock agent config file
        agent_dir = Path(self.temp_dir) / "agents" / "testdomain_com"
        agent_dir.mkdir(parents=True, exist_ok=True)

        agent_config = {
            "agent_name": "Test Assistant",
            "personality": "professional",
            "tone_keywords": ["helpful", "knowledgeable"],
            "conversation_style": "helpful",
            "industry": "dentists",
            "system_prompt": "You are a helpful assistant",
            "namespace": "kb:testdomain.com"
        }

        with open(agent_dir / "agent.json", 'w') as f:
            json.dump(agent_config, f)

        # Test loading
        composer_with_mock = EmailComposer(use_llm=False)
        agent_context = composer_with_mock._load_agent_context(
            "testdomain.com", "Test Business", "dentists"
        )

        self.assertEqual(agent_context.agent_name, "Test Assistant")
        self.assertEqual(agent_context.personality, "professional")
        self.assertIn("helpful", agent_context.tone_keywords)

    @patch('pipeline.email_composer.OpenRouterClient')
    def test_llm_email_composition(self, mock_openrouter):
        """Test LLM email composition."""
        # Mock OpenRouter client
        mock_client = Mock()
        mock_client.generate_email_template.return_value = {
            "subject": "AI-Powered Customer Service for Test Business",
            "body": "Hi there,\n\nWe offer AI solutions for your business.\n\nBest,\nAI Team",
            "recipient_email": "test@email.com",
            "business_name": "Test Business",
            "domain": "test.com",
            "industry": "general",
            "key_personalizations": ["Business name", "Industry"],
            "value_propositions_used": ["24/7 support", "Personalized service"],
            "confidence_score": "High",
            "generated_by": "mistral_medium_openrouter"
        }
        mock_openrouter.return_value = mock_client

        composer = EmailComposer(use_llm=True)

        template = composer.compose_email(
            business_name="Test Business",
            domain="test.com",
            industry="general",
            recipient_email="test@email.com"
        )

        self.assertIsNotNone(template)
        self.assertEqual(template.subject, "AI-Powered Customer Service for Test Business")
        self.assertIn("AI solutions", template.body)
        self.assertIn("mistral_medium_openrouter", template.personalization_notes[2])


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        # Mock config to avoid real API calls
        config = {
            "leads_dir": f"{self.temp_dir}/leads",
            "business_data_dir": f"{self.temp_dir}/business_data",
            "agents_dir": f"{self.temp_dir}/agents",
            "emails_dir": f"{self.temp_dir}/emails",
            "create_elevenlabs_agents": False,  # Disable real API calls
            "send_emails": False,  # Disable real email sending
            "use_llm_email_generation": False,  # Disable LLM for testing
        }
        self.pipeline = GrowthAutomationPipeline()
        self.pipeline.config.update(config)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('pipeline.lead_generation.LeadGenerator.generate_leads')
    @patch('pipeline.business_intelligence.BusinessIntelligenceLoader.process_business')
    @patch('pipeline.voice_agent_generator.VoiceAgentGenerator.generate_agent_for_business')
    @patch('pipeline.email_composer.EmailComposer.compose_email_for_lead')
    def test_full_pipeline_execution(self, mock_compose, mock_agent, mock_process, mock_leads):
        """Test full pipeline execution with mocked components."""
        # Mock lead generation
        mock_leads.return_value = [
            Lead("Test Dental", "testdental.com", "Chicago, IL", "dentists", "info@testdental.com")
        ]

        # Mock business processing
        mock_process.return_value = True

        # Mock agent generation
        mock_agent.return_value = AgentConfig(
            domain="testdental.com",
            agent_name="Test Dental Assistant",
            system_prompt="Test prompt"
        )

        # Mock email composition
        mock_template = Mock()
        mock_template.subject = "Test Subject"
        mock_compose.return_value = mock_template

        results = self.pipeline.run_full_pipeline("dentists", "Chicago, IL", max_leads=5)

        self.assertEqual(results["leads_generated"], 1)
        self.assertEqual(results["businesses_processed"], 1)
        self.assertEqual(results["agents_created"], 1)
        self.assertEqual(results["emails_composed"], 1)

    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        # Test with invalid inputs
        results = self.pipeline.run_full_pipeline("", "", max_leads=0)

        # Should handle gracefully
        self.assertIsInstance(results, dict)
        self.assertIn("errors", results)


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""

    def test_config_loading(self):
        """Test configuration loading."""
        config = {
            "email_provider": "mailgun",
            "max_leads": 20,
            "send_emails": False
        }

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_path = f.name

        try:
            pipeline = GrowthAutomationPipeline(config_path)

            self.assertEqual(pipeline.config["email_provider"], "mailgun")
            self.assertEqual(pipeline.config["max_leads"], 20)
            self.assertFalse(pipeline.config["send_emails"])

        finally:
            os.unlink(config_path)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
