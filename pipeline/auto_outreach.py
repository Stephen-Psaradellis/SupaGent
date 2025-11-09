"""
Growth Automation Pipeline - Complete Lead Gen Flywheel

Orchestrates the entire growth automation process:
1. Generate leads from target verticals
2. Scrape and vectorize business data
3. Create personalized voice agents
4. Compose cold outreach emails
5. Send emails with tracking

Usage:
    python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL"

This creates a complete lead generation flywheel built on your voice assistant technology.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from pipeline.lead_generation import LeadGenerator, Lead
from pipeline.business_intelligence import BusinessIntelligenceLoader
from pipeline.voice_agent_generator import VoiceAgentGenerator
from pipeline.email_composer import EmailComposer
from pipeline.email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrowthAutomationPipeline:
    """Complete growth automation pipeline orchestrator."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the growth automation pipeline.

        Args:
            config_path: Path to pipeline configuration file
        """
        self.config = self._load_config(config_path)

        # Initialize components
        self.lead_generator = LeadGenerator(self.config.get("leads_dir", "pipeline/leads"))
        self.business_loader = BusinessIntelligenceLoader(self.config.get("business_data_dir", "pipeline/business_data"))
        self.agent_generator = VoiceAgentGenerator(
            agents_dir=self.config.get("agents_dir", "pipeline/agents"),
            config_path=self.config.get("agent_templates", "pipeline/config/agent_templates.json"),
            use_llm=self.config.get("use_llm_agent_prompts", True)
        )
        self.email_composer = EmailComposer(
            templates_dir=self.config.get("email_templates", "pipeline/config/email_templates"),
            use_llm=self.config.get("use_llm_email_generation", True)
        )
        self.email_sender = EmailSender(
            self.config.get("email_provider", "resend"),
            self.config.get("emails_dir", "pipeline/emails")
        )

        logger.info("🚀 Growth Automation Pipeline initialized")

    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load pipeline configuration."""
        config = {
            "leads_dir": "pipeline/leads",
            "business_data_dir": "pipeline/business_data",
            "agents_dir": "pipeline/agents",
            "emails_dir": "pipeline/emails",
            "email_provider": "resend",
            "max_leads": 10,
            "max_pages_per_business": 50,
            "create_elevenlabs_agents": True,
            "send_emails": False,  # Safety default - require explicit opt-in
            "batch_size": 10,
            "delay_seconds": 60,
        }

        if config_path and Path(config_path).exists():
            try:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                logger.info(f"📄 Loaded config from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return config

    def run_full_pipeline(
        self,
        industry: str,
        location: str,
        max_leads: Optional[int] = None,
        send_emails: Optional[bool] = None
    ) -> dict:
        """Run the complete growth automation pipeline.

        Args:
            industry: Target industry (e.g., "dentists")
            location: Target location (e.g., "Chicago, IL")
            max_leads: Maximum leads to generate
            send_emails: Whether to send emails (overrides config)

        Returns:
            Pipeline execution results
        """
        results = {
            "industry": industry,
            "location": location,
            "leads_generated": 0,
            "businesses_processed": 0,
            "agents_created": 0,
            "emails_composed": 0,
            "emails_sent": 0,
            "errors": [],
        }

        max_leads = max_leads or self.config["max_leads"]
        send_emails = send_emails if send_emails is not None else self.config["send_emails"]

        logger.info(f"🎯 Starting growth automation for {industry} in {location}")

        try:
            # Step 1: Generate leads
            logger.info("🔍 Step 1: Generating leads...")
            leads = self.lead_generator.generate_leads(
                industry=industry,
                location=location,
                limit=max_leads
            )
            results["leads_generated"] = len(leads)
            logger.info(f"✅ Generated {len(leads)} leads")

            if not leads:
                logger.warning("⚠️ No leads generated, ending pipeline")
                return results

            # Step 2: Process each business
            processed_domains = []
            agent_count = 0
            email_count = 0

            for i, lead in enumerate(leads, 1):
                logger.info(f"🏢 Step 2: Processing business {i}/{len(leads)}: {lead.name}")

                try:
                    # Check if business has email (required for outreach)
                    if not lead.email:
                        logger.warning(f"⚠️ Skipping {lead.name} - no email found")
                        continue

                    # 2a: Scrape and vectorize business data
                    logger.info(f"   📊 Scraping and vectorizing {lead.domain}...")
                    success = self.business_loader.process_business(
                        lead.domain,
                        self.config["max_pages_per_business"]
                    )

                    if not success:
                        logger.warning(f"   ❌ Failed to process business data for {lead.domain}")
                        results["errors"].append(f"Business processing failed: {lead.domain}")
                        continue

                    # 2b: Generate voice agent
                    logger.info(f"   🤖 Generating voice agent for {lead.name}...")
                    agent_config = self.agent_generator.generate_agent_for_business(
                        domain=lead.domain,
                        business_name=lead.name,
                        industry=lead.industry or industry,
                        create_elevenlabs=self.config["create_elevenlabs_agents"]
                    )

                    if agent_config:
                        agent_count += 1
                        logger.info(f"   ✅ Created agent: {agent_config.agent_name}")
                    else:
                        logger.warning(f"   ⚠️ Failed to create agent for {lead.domain}")
                        results["errors"].append(f"Agent creation failed: {lead.domain}")

                    # 2c: Compose email
                    logger.info(f"   📧 Composing email for {lead.name}...")
                    email_template = self.email_composer.compose_email_for_lead(lead.domain)

                    if email_template:
                        email_count += 1
                        logger.info(f"   ✅ Composed email with subject: {email_template.subject}")
                    else:
                        logger.warning(f"   ⚠️ Failed to compose email for {lead.domain}")
                        results["errors"].append(f"Email composition failed: {lead.domain}")
                        continue

                    processed_domains.append(lead.domain)

                except Exception as e:
                    logger.error(f"   ❌ Error processing {lead.name}: {e}")
                    results["errors"].append(f"Business processing error for {lead.domain}: {str(e)}")
                    continue

            results["businesses_processed"] = len(processed_domains)
            results["agents_created"] = agent_count
            results["emails_composed"] = email_count

            # Step 3: Send emails if enabled
            if send_emails and processed_domains:
                logger.info("📤 Step 3: Sending emails...")

                if not send_emails:
                    logger.warning("⚠️ Email sending disabled by default. Use --send-emails to enable.")
                    logger.info("💡 To enable: python auto_outreach.py --send-emails ...")
                else:
                    email_results = self.email_sender.send_bulk_emails(
                        processed_domains,
                        self.config["batch_size"],
                        self.config["delay_seconds"]
                    )

                    sent_count = sum(1 for success in email_results.values() if success)
                    results["emails_sent"] = sent_count
                    logger.info(f"✅ Sent {sent_count}/{len(processed_domains)} emails")

                    if sent_count < len(processed_domains):
                        failed_domains = [d for d, success in email_results.items() if not success]
                        results["errors"].extend([f"Email send failed: {d}" for d in failed_domains])

            # Final summary
            logger.info("🎉 Pipeline execution complete!")
            logger.info(f"   📊 Leads generated: {results['leads_generated']}")
            logger.info(f"   🏢 Businesses processed: {results['businesses_processed']}")
            logger.info(f"   🤖 Agents created: {results['agents_created']}")
            logger.info(f"   📧 Emails composed: {results['emails_composed']}")
            logger.info(f"   📤 Emails sent: {results['emails_sent']}")

            if results["errors"]:
                logger.warning(f"   ⚠️ Errors encountered: {len(results['errors'])}")
                for error in results["errors"][:5]:  # Show first 5 errors
                    logger.warning(f"     - {error}")
                if len(results["errors"]) > 5:
                    logger.warning(f"     ... and {len(results['errors']) - 5} more")

            return results

        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            results["errors"].append(f"Pipeline failure: {str(e)}")
            return results

    def run_lead_generation_only(
        self,
        industry: str,
        location: str,
        max_leads: Optional[int] = None
    ) -> List[Lead]:
        """Run only the lead generation step.

        Args:
            industry: Target industry
            location: Target location
            max_leads: Maximum leads to generate

        Returns:
            List of generated leads
        """
        max_leads = max_leads or self.config["max_leads"]
        return self.lead_generator.generate_leads(industry, location, max_leads)

    def run_business_processing_only(self, domains: List[str]) -> dict:
        """Run only business processing steps (scraping, agents, emails).

        Args:
            domains: List of business domains to process

        Returns:
            Processing results
        """
        results = {
            "domains_processed": 0,
            "agents_created": 0,
            "emails_composed": 0,
            "errors": []
        }

        for domain in domains:
            try:
                logger.info(f"🏢 Processing {domain}...")

                # Scrape and vectorize
                success = self.business_loader.process_business(domain, self.config["max_pages_per_business"])
                if not success:
                    results["errors"].append(f"Scraping failed: {domain}")
                    continue

                # Generate agent
                agent_config = self.agent_generator.generate_agent_for_business(
                    domain=domain,
                    business_name=domain.replace(".", " ").title(),  # Placeholder name
                    industry="general",
                    create_elevenlabs=self.config["create_elevenlabs_agents"]
                )

                if agent_config:
                    results["agents_created"] += 1

                # Compose email
                email_template = self.email_composer.compose_email_for_lead(domain)
                if email_template:
                    results["emails_composed"] += 1

                results["domains_processed"] += 1

            except Exception as e:
                results["errors"].append(f"Processing failed for {domain}: {str(e)}")

        return results


def main():
    """CLI interface for the growth automation pipeline."""
    parser = argparse.ArgumentParser(
        description="Growth Automation Pipeline - Complete Lead Gen Flywheel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate leads only
  python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL" --leads-only

  # Full pipeline (no email sending)
  python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL"

  # Full pipeline with email sending (CAUTION: actually sends emails!)
  python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL" --send-emails

  # Process specific domains
  python pipeline/auto_outreach.py --domains-file domains.txt --process-only
        """
    )

    parser.add_argument("--industry", help="Target industry (e.g., 'dentists')")
    parser.add_argument("--location", help="Target location (e.g., 'Chicago, IL')")
    parser.add_argument("--max-leads", type=int, default=10, help="Maximum leads to generate")
    parser.add_argument("--leads-only", action="store_true", help="Generate leads only")
    parser.add_argument("--process-only", action="store_true", help="Process domains only (no lead gen)")
    parser.add_argument("--domains-file", help="File containing domains to process")
    parser.add_argument("--send-emails", action="store_true", help="Actually send emails (CAUTION!)")
    parser.add_argument("--config", help="Pipeline configuration file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if not args.leads_only and not args.process_only:
        if not args.industry or not args.location:
            parser.error("Must specify --industry and --location for full pipeline, or use --leads-only or --process-only")

    if args.process_only and not args.domains_file:
        parser.error("--process-only requires --domains-file")

    try:
        pipeline = GrowthAutomationPipeline(args.config)

        if args.leads_only:
            # Lead generation only
            leads = pipeline.run_lead_generation_only(args.industry, args.location, args.max_leads)
            print(f"Generated {len(leads)} leads:")
            for lead in leads:
                print(f"- {lead.name} ({lead.domain}) - {lead.email or 'No email'}")

        elif args.process_only:
            # Business processing only
            try:
                with open(args.domains_file, 'r', encoding='utf-8') as f:
                    domains = [line.strip() for line in f if line.strip()]

                results = pipeline.run_business_processing_only(domains)
                print(f"Processed {results['domains_processed']} domains")
                print(f"Created {results['agents_created']} agents")
                print(f"Composed {results['emails_composed']} emails")

                if results['errors']:
                    print(f"Errors: {len(results['errors'])}")
                    for error in results['errors'][:3]:
                        print(f"- {error}")

            except Exception as e:
                print(f"Failed to process domains: {e}")
                sys.exit(1)

        else:
            # Full pipeline
            if args.send_emails:
                print("⚠️  WARNING: --send-emails enabled. This will actually send emails!")
                confirm = input("Are you sure? Type 'yes' to continue: ")
                if confirm.lower() != 'yes':
                    print("Aborted.")
                    sys.exit(0)

            results = pipeline.run_full_pipeline(
                industry=args.industry,
                location=args.location,
                max_leads=args.max_leads,
                send_emails=args.send_emails
            )

            print("\n🎉 Pipeline Complete!")
            print(f"Leads Generated: {results['leads_generated']}")
            print(f"Businesses Processed: {results['businesses_processed']}")
            print(f"Voice Agents Created: {results['agents_created']}")
            print(f"Emails Composed: {results['emails_composed']}")
            print(f"Emails Sent: {results['emails_sent']}")

            if results['errors']:
                print(f"\n⚠️  Errors ({len(results['errors'])}):")
                for error in results['errors'][:5]:
                    print(f"- {error}")
                if len(results['errors']) > 5:
                    print(f"... and {len(results['errors']) - 5} more")

    except KeyboardInterrupt:
        print("\n⏹️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
