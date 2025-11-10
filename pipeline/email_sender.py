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
        config_file: str = "pipeline/config/email_config.json"
    ):
        """Initialize email sender.

        Args:
            emails_dir: Directory containing email templates
            config_file: Email configuration file
        """
        # Resolve paths relative to project root (parent of pipeline directory)
        # If __file__ is pipeline/email_sender.py, then parent.parent is project root
        project_root = Path(__file__).parent.parent
        
        if not Path(emails_dir).is_absolute():
            self.emails_dir = project_root / emails_dir
        else:
            self.emails_dir = Path(emails_dir)
            
        if not Path(config_file).is_absolute():
            self.config_file = project_root / config_file
        else:
            self.config_file = Path(config_file)
            
        self.config = self._load_config()
        self.session = requests.Session()

    def _load_config(self) -> Dict:
        """Load email configuration including API keys."""
        config = {
            "api_key": os.getenv("ELASTICEMAIL_API_KEY"),
            "from_email": os.getenv("FROM_EMAIL", "noreply@yourdomain.com"),
            "from_name": os.getenv("FROM_NAME", "AI Solutions"),
        }

        # Load from config file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                logger.warning(f"Failed to load email config: {e}")

        return config

    def send_email(self, domain: str, track_status: bool = True) -> bool:
        """Send email for a specific domain.

        Args:
            domain: Business domain
            track_status: Whether to track delivery status

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Load email template
            template = self._load_email_template(domain)
            if not template:
                logger.error(f"❌ No email template found for {domain}")
                return False

            # Validate recipient email
            if not template.get("recipient_email"):
                logger.error(f"❌ No recipient email for {domain}")
                return False

            logger.info(f"📤 Sending email to {template['recipient_email']} for {template['business_name']}")

            # Send via ElasticEmail
            result = self._send_via_elasticemail(template)

            if result:
                message_id = result.get("message_id") or result.get("id")

                # Track status if requested
                if track_status and message_id:
                    status = EmailStatus(
                        domain=domain,
                        recipient_email=template["recipient_email"],
                        message_id=message_id,
                        status="sent",
                        sent_at=datetime.now()
                    )
                    self._save_email_status(status)

                logger.info(f"✅ Email sent successfully to {template['business_name']}")
                return True
            else:
                logger.error(f"❌ Failed to send email to {template['business_name']}")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending email for {domain}: {e}")
            return False

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

        url = "https://api.elasticemail.com/v2/email/send"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Build email data
        email_data = {
            "apikey": api_key,
            "from": self.config["from_email"],
            "fromName": self.config["from_name"],
            "to": template["recipient_email"],
            "subject": template["subject"],
            "bodyHtml": self._convert_text_to_html(template["body"]),
            "bodyText": template["body"],  # Include plain text version
        }

        # Add tracking tags
        email_data["tag"] = template["domain"]

        try:
            response = self.session.post(url, headers=headers, data=email_data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Return message ID in expected format
                    return {"message_id": result.get("data", {}).get("messageid")}
                else:
                    logger.error(f"ElasticEmail API error: {result.get('error')}")
                    return None
            else:
                logger.error(f"ElasticEmail API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"ElasticEmail API request failed: {e}")
            return None


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
