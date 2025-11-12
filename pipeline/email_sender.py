"""
Outbound Email Sender for Growth Automation Pipeline.

Sends personalized cold outreach emails with embedded voice agents using
ElasticEmail transactional email API. Includes comprehensive tracking for
opens, clicks, and engagement metrics.

Features:
- ElasticEmail provider for reliable email delivery
- Open and click tracking
- Bounce and complaint handling
- Rate limiting and deliverability best practices
- Status tracking and reporting
- Compliance with email regulations
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
import re
import hashlib
import hmac
import base64
from html import unescape

from pipeline.lead_tracker import LeadTracker
from pipeline.lead_generation import Lead
from pipeline.email_composer import EmailComposer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailStatus:
    """Email delivery status tracking."""

    domain: str
    recipient_email: str
    message_id: Optional[str]
    status: str  # 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained'
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "domain": self.domain,
            "recipient_email": self.recipient_email,
            "message_id": self.message_id,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "error_message": self.error_message,
        }


class EmailSender:
    """Sends outbound emails with tracking via ElasticEmail API."""

    def __init__(
        self,
        emails_dir: str = "pipeline/emails",
        leads_dir: str = "pipeline/leads"
    ):
        """Initialize email sender.

        Args:
            emails_dir: Directory containing email templates
            leads_dir: Directory containing leads
        """
        # Resolve paths relative to project root (parent of pipeline directory)
        # If __file__ is pipeline/email_sender.py, then parent.parent is project root
        project_root = Path(__file__).parent.parent

        if not Path(emails_dir).is_absolute():
            self.emails_dir = project_root / emails_dir
        else:
            self.emails_dir = Path(emails_dir)

        self.config = self._load_config()
        self.session = requests.Session()

        # Initialize lead tracker
        self.lead_tracker = LeadTracker(leads_dir)

        # Initialize email composer for personalized HTML generation
        try:
            self.email_composer = EmailComposer(
                templates_dir=self.emails_dir / "templates",
                business_data_dir="pipeline/business_data"
            )
            logger.info("📧 Initialized email composer for personalized HTML generation")
        except Exception as e:
            logger.warning(f"Failed to initialize email composer: {e}")
            self.email_composer = None

    def _load_config(self) -> Dict:
        """Load email configuration from environment variables only.
        
        Environment variables:
            ELASTICEMAIL_API_KEY: ElasticEmail API key (required)
            FROM_EMAIL: Sender email address (default: stephen.psaradellis@shortforge.dev)
            FROM_NAME: Sender name (default: Stephen Psaradellis)
        """
        api_key = os.getenv("ELASTICEMAIL_API_KEY")
        if not api_key:
            logger.warning("⚠️ ELASTICEMAIL_API_KEY not set in environment variables")
        
        config = {
            "api_key": api_key,
            "from_email": os.getenv("FROM_EMAIL", "stephen.psaradellis@shortforge.dev"),
            "from_name": os.getenv("FROM_NAME", "Stephen Psaradellis")
        }

        return config

    def send_email_to_lead(self, lead: Lead, track_status: bool = True, use_personalized_html: bool = True) -> bool:
        """Send email to a specific lead.

        Args:
            lead: Lead object to send email to
            track_status: Whether to track delivery status
            use_personalized_html: Whether to use personalized HTML generation

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Check if lead has already been contacted
            if lead.email_outreach_status != "not_contacted":
                logger.warning(f"⚠️ Lead {lead.domain} has already been contacted (status: {lead.email_outreach_status})")
                return False

            # Check suppression before composing/sending
            if self._is_suppressed(lead.email):
                logger.warning(f"🛑 Skipping suppressed recipient: {lead.email}")
                return False

            # Try personalized HTML generation first
            if use_personalized_html and self.email_composer:
                try:
                    # Load lead data and business content
                    lead_data = lead.to_dict() if hasattr(lead, 'to_dict') else {
                        "name": lead.name,
                        "email": lead.email,
                        "location": lead.location,
                        "industry": lead.industry,
                        "domain": lead.domain
                    }

                    # Load business content
                    business_content = self._load_business_content(lead.domain)

                    # Generate personalized HTML
                    # Get agent_id from environment variable
                    voice_agent_id = os.getenv("ELEVENLABS_AGENT_ID")
                    html_content = self.email_composer.compose_personalized_html_email(
                        business_name=lead.name or lead.domain,
                        domain=lead.domain,
                        industry=lead.industry or "general",
                        lead_data=lead_data,
                        business_content=business_content,
                        voice_agent_id=voice_agent_id
                    )

                    # Create email data structure for personalized HTML
                    email_data = {
                        "recipient_email": lead.email,
                        "business_name": lead.name or lead.domain,
                        "subject": f"AI Voice Agent Demo for {lead.name or lead.domain}",
                        "body": "",  # Will be replaced with HTML
                        "html_body": html_content,
                        "domain": lead.domain
                    }

                    logger.info(f"🎨 Generated personalized HTML email for {lead.name or lead.domain}")

                except Exception as e:
                    logger.warning(f"Failed to generate personalized HTML, falling back to template: {e}")
                    use_personalized_html = False

            # Fall back to traditional template loading
            if not use_personalized_html:
                # Load email template
                template = self._load_email_template(lead.domain)
                if not template:
                    logger.error(f"❌ No email template found for {lead.domain}")
                    return False
                email_data = template

            # Validate recipient email
            if not email_data.get("recipient_email"):
                logger.error(f"❌ No recipient email for {lead.domain}")
                return False

            logger.info(f"📤 Sending email to {email_data['recipient_email']} for {email_data['business_name']}")

            # Send via ElasticEmail
            result = self._send_via_elasticemail(email_data)

            if result:
                message_id = result.get("message_id") or result.get("id")

                # Track status if requested
                if track_status and message_id:
                    # Update lead status
                    template_name = "personalized_html" if use_personalized_html else email_data.get("template_used", "default")
                    self.lead_tracker.mark_lead_contacted(lead.domain, message_id, template_name)

                    # Also save to email status file for backward compatibility
                    status = EmailStatus(
                        domain=lead.domain,
                        recipient_email=email_data["recipient_email"],
                        message_id=message_id,
                        status="sent",
                        sent_at=datetime.now()
                    )
                    self._save_email_status(status)

                logger.info(f"✅ Email sent successfully to {email_data['business_name']}")
                return True
            else:
                logger.error(f"❌ Failed to send email to {email_data['business_name']}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending email for {lead.domain}: {e}")
            return False

    def send_email(self, domain: str, track_status: bool = True) -> bool:
        """Send email for a specific domain (legacy method).

        Args:
            domain: Business domain
            track_status: Whether to track delivery status

        Returns:
            True if sent successfully, False otherwise
        """
        # Get lead for this domain
        lead = self.lead_tracker.get_lead_by_domain(domain)
        if not lead:
            logger.error(f"❌ No lead found for domain {domain}")
            return False

        return self.send_email_to_lead(lead, track_status)

    def _send_via_elasticemail(self, template: Dict) -> Optional[Dict]:
        """Send email via ElasticEmail API.

        Args:
            template: Email template data

        Returns:
            Response data if successful, None otherwise
        """
        api_key = self.config["api_key"]
        if not api_key:
            logger.error("❌ ElasticEmail API key not configured")
            return None

        url = "https://api.elasticemail.com/v4/emails"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": api_key
        }

        # Build email data in v4 format matching ElasticEmail API specification
        # Prepare HTML (prefer provided html_body, else convert from text)
        html_content = template.get("html_body") or self._convert_text_to_html(template["body"])

        # Compute unsubscribe URL and inject into HTML if placeholder exists
        recipient_email = template["recipient_email"]
        base_unsub_url = os.getenv("UNSUB_BASE_URL", "https://shortforge.dev/unsub")
        secret = os.getenv("UNSUB_SIGNING_SECRET", "change-me")
        unsubscribe_sig = self._sign_unsubscribe(recipient_email, secret)
        unsubscribe_url = f"{base_unsub_url}?e={recipient_email}&sig={unsubscribe_sig}"
        if "{{unsubscribe_url}}" in html_content:
            html_content = html_content.replace("{{unsubscribe_url}}", unsubscribe_url)

        # Always include a plain-text alternative
        plain_text = self._html_to_text(html_content)
        body_content = [
            {
                "ContentType": "HTML",
                "Content": html_content,
                "Charset": "utf-8"
            },
            {
                "ContentType": "PlainText",
                "Content": plain_text,
                "Charset": "utf-8"
            }
        ]

        # Build payload matching ElasticEmail v4 API format exactly
        # Note: Field order matches the API documentation example
        email_data = {
            "Recipients": [
                {
                    "Email": recipient_email
                }
            ],
            "Content": {
                "Body": body_content,
                "From": f"{self.config['from_name']} <{self.config['from_email']}>",
                "Subject": template["subject"],
                "ReplyTo": os.getenv("REPLY_TO_EMAIL", self.config["from_email"]),
                "Headers": {
                    "List-Unsubscribe": f"<{unsubscribe_url}>, <mailto:unsubscribe@shortforge.dev?subject=unsubscribe>",
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"
                }
            }
        }
        
        # Validate required fields
        if not email_data["Recipients"] or not email_data["Recipients"][0].get("Email"):
            logger.error("Missing recipient email")
            return None
        if not email_data["Content"].get("From"):
            logger.error("Missing From field")
            return None
        if not email_data["Content"].get("Subject"):
            logger.error("Missing Subject field")
            return None
        if not email_data["Content"].get("Body") or not email_data["Content"]["Body"]:
            logger.error("Missing Body content")
            return None

        # Log the payload for debugging (ensure proper JSON serialization)
        payload_json = json.dumps(email_data, indent=2, ensure_ascii=False)
        logger.info(f"📤 ElasticEmail payload:\n{payload_json}")
        
        # Also log a minimal version to compare
        minimal_payload = {
            "Recipients": [{"Email": template["recipient_email"]}],
            "Content": {
                "Body": [{"ContentType": "HTML", "Content": "test", "Charset": "utf-8"}],
                "From": f"{self.config['from_name']} <{self.config['from_email']}>",
                "Subject": template["subject"]
            }
        }
        logger.debug(f"Minimal test payload: {json.dumps(minimal_payload, indent=2)}")

        try:
            # Send the request - ensure JSON is properly serialized
            # Using json= parameter automatically sets Content-Type and serializes
            response = self.session.post(
                url, 
                headers=headers, 
                json=email_data,  # requests will serialize this to JSON
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                # v4 API may return transactionid or TransactionID in the response
                message_id = result.get("transactionid") or result.get("TransactionID") or result.get("MessageID")
                if message_id:
                    return {"message_id": message_id}
                else:
                    logger.error(f"ElasticEmail API error: Missing transaction ID in response: {result}")
                    return None
            else:
                # Log full error details
                logger.error(f"ElasticEmail API error: {response.status_code}")
                logger.error(f"Response headers: {dict(response.headers)}")
                logger.error(f"Response body: {response.text}")
                logger.error(f"Request payload that was sent:\n{payload_json}")
                return None

        except Exception as e:
            logger.error(f"ElasticEmail API request failed: {e}")
            return None

    def _html_to_text(self, html: str) -> str:
        """Convert HTML content to a readable plain-text alternative.

        This avoids spam filters penalizing HTML-only emails and improves accessibility.
        """
        # Remove script/style
        cleaned = re.sub(r"(?is)<(script|style)[^>]*>.*?</\\1>", "", html or "")
        # Line breaks for <br> and paragraph endings
        cleaned = re.sub(r"(?is)<br\\s*/?>", "\n", cleaned)
        cleaned = re.sub(r"(?is)</p>", "\n\n", cleaned)
        # Strip all tags
        cleaned = re.sub(r"(?is)<[^>]+>", "", cleaned)
        # Unescape entities
        cleaned = unescape(cleaned)
        # Collapse excessive blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _sign_unsubscribe(self, email: str, secret: str) -> str:
        """Create a URL-safe HMAC signature for unsubscribe links."""
        digest = hmac.new(secret.encode("utf-8"), email.encode("utf-8"), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    def _is_suppressed(self, email: Optional[str]) -> bool:
        """Return True if email is present in local suppression list."""
        if not email:
            return False
        suppress_file = self.emails_dir / "suppressions.jsonl"
        if not suppress_file.exists():
            return False
        try:
            with open(suppress_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get("email") == email:
                            return True
                    except Exception:
                        continue
        except Exception:
            return False
        return False


    def _convert_text_to_html(self, text: str) -> str:
        """Convert plain text email to HTML format.

        Args:
            text: Plain text email body

        Returns:
            HTML formatted email
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

    def _load_email_template(self, domain: str) -> Optional[Dict]:
        """Load email template for a domain.

        Args:
            domain: Business domain

        Returns:
            Email template data or None
        """
        template_file = self.emails_dir / f"{domain.replace('.', '_')}.json"

        if not template_file.exists():
            return None

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load email template for {domain}: {e}")
            return None

    def _load_business_content(self, domain: str) -> Dict[str, str]:
        """Load business content summary for personalization.

        Args:
            domain: Business domain

        Returns:
            Content summary by type
        """
        from pathlib import Path
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
                    # Summarize content (take first meaningful chunks)
                    combined_content = " ".join([item["content"][:300] for item in items[:2]])
                    summaries[content_type] = combined_content

            return summaries

        except Exception as e:
            logger.error(f"Failed to load business content for {domain}: {e}")
            return {}

    def _save_email_status(self, status: EmailStatus) -> None:
        """Save email status to tracking file.

        Args:
            status: Email status to save
        """
        status_dir = self.emails_dir / "status"
        status_dir.mkdir(parents=True, exist_ok=True)

        status_file = status_dir / "email_status.jsonl"

        with open(status_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(status.to_dict()) + '\n')

        logger.info(f"📊 Saved email status for {status.domain}: {status.status}")

    def send_bulk_emails(
        self,
        domains: List[str],
        batch_size: int = 10,
        delay_seconds: int = 60
    ) -> Dict[str, bool]:
        """Send emails to multiple domains with rate limiting.

        Args:
            domains: List of business domains
            batch_size: Emails per batch
            delay_seconds: Delay between batches

        Returns:
            Dictionary mapping domain to success status
        """
        results = {}

        for i in range(0, len(domains), batch_size):
            batch = domains[i:i + batch_size]
            logger.info(f"📤 Sending batch {i//batch_size + 1} of {len(batch)} emails")

            for domain in batch:
                success = self.send_email(domain)
                results[domain] = success

                # Small delay between individual emails
                time.sleep(2)

            # Delay between batches (except for last batch)
            if i + batch_size < len(domains):
                logger.info(f"⏱️ Waiting {delay_seconds} seconds before next batch...")
                time.sleep(delay_seconds)

        return results

    def send_bulk_emails_to_leads(
        self,
        leads: List[Lead],
        batch_size: int = 10,
        delay_seconds: int = 60
    ) -> Dict[str, bool]:
        """Send emails to multiple leads with rate limiting.

        Args:
            leads: List of Lead objects to send emails to
            batch_size: Emails per batch
            delay_seconds: Delay between batches

        Returns:
            Dictionary mapping domain to success status
        """
        results = {}

        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]
            logger.info(f"📤 Sending batch {i//batch_size + 1} of {len(batch)} emails")

            for lead in batch:
                success = self.send_email_to_lead(lead)
                results[lead.domain] = success

                # Small delay between individual emails
                time.sleep(2)

            # Delay between batches (except for last batch)
            if i + batch_size < len(leads):
                logger.info(f"⏱️ Waiting {delay_seconds} seconds before next batch...")
                time.sleep(delay_seconds)

        return results

    def get_email_status(self, domain: str) -> Optional[EmailStatus]:
        """Get current email status for a domain.

        Args:
            domain: Business domain

        Returns:
            Latest email status or None
        """
        status_file = self.emails_dir / "status" / "email_status.jsonl"

        if not status_file.exists():
            return None

        latest_status = None
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                for line in f:
                    status_data = json.loads(line.strip())
                    if status_data["domain"] == domain:
                        # Convert back to EmailStatus
                        status_data["sent_at"] = datetime.fromisoformat(status_data["sent_at"]) if status_data["sent_at"] else None
                        status_data["delivered_at"] = datetime.fromisoformat(status_data["delivered_at"]) if status_data["delivered_at"] else None
                        status_data["opened_at"] = datetime.fromisoformat(status_data["opened_at"]) if status_data["opened_at"] else None
                        status_data["clicked_at"] = datetime.fromisoformat(status_data["clicked_at"]) if status_data["clicked_at"] else None
                        latest_status = EmailStatus(**status_data)

        except Exception as e:
            logger.error(f"Failed to read email status for {domain}: {e}")

        return latest_status


def main():
    """CLI interface for email sending."""
    import argparse

    parser = argparse.ArgumentParser(description="Send outbound emails via ElasticEmail")
    parser.add_argument("--domain", help="Specific domain to send to")
    parser.add_argument("--domains-file", help="File containing list of domains")
    parser.add_argument("--batch-size", type=int, default=10, help="Emails per batch")
    parser.add_argument("--delay", type=int, default=60, help="Delay between batches (seconds)")
    parser.add_argument("--emails-dir", default="pipeline/emails", help="Emails directory")

    args = parser.parse_args()

    sender = EmailSender(args.emails_dir)

    if args.domain:
        # Send single email
        success = sender.send_email(args.domain)
        print(f"Email {'sent successfully' if success else 'failed'} for {args.domain}")
    elif args.domains_file:
        # Send bulk emails
        try:
            with open(args.domains_file, 'r', encoding='utf-8') as f:
                domains = [line.strip() for line in f if line.strip()]

            results = sender.send_bulk_emails(domains, args.batch_size, args.delay)

            successful = sum(1 for success in results.values() if success)
            print(f"Sent {successful}/{len(domains)} emails successfully")

        except Exception as e:
            print(f"Failed to send bulk emails: {e}")
            exit(1)
    else:
        parser.error("Must specify either --domain or --domains-file")


if __name__ == "__main__":
    main()
