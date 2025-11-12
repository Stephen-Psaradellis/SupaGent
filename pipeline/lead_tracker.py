"""
Lead Email Outreach Tracker for Growth Automation Pipeline.

Tracks email outreach status for leads, prevents duplicate emails, and provides
comprehensive reporting on outreach effectiveness.

Features:
- Lead email outreach status tracking
- Duplicate email prevention
- Outreach metrics and analytics
- Integration with email sender status updates
- Lead lifecycle management
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from pipeline.lead_generation import Lead

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OutreachMetrics:
    """Aggregated outreach metrics for reporting."""

    total_leads: int = 0
    contacted_leads: int = 0
    responded_leads: int = 0
    converted_leads: int = 0
    bounced_emails: int = 0
    complained_emails: int = 0
    unsubscribed_emails: int = 0
    response_rate: float = 0.0
    conversion_rate: float = 0.0
    bounce_rate: float = 0.0

    def calculate_rates(self) -> None:
        """Calculate derived rates from raw metrics."""
        if self.contacted_leads > 0:
            self.response_rate = self.responded_leads / self.contacted_leads
            self.conversion_rate = self.converted_leads / self.contacted_leads
            self.bounce_rate = self.bounced_emails / self.contacted_leads


class LeadTracker:
    """Manages lead email outreach tracking and prevents duplicate emails."""

    def __init__(self, leads_dir: str = "pipeline/leads"):
        """Initialize lead tracker.

        Args:
            leads_dir: Directory containing lead files
        """
        self.leads_dir = Path(leads_dir)
        self.leads_dir.mkdir(parents=True, exist_ok=True)

        # Cache for faster lookups
        self._leads_cache: Dict[str, Lead] = {}
        self._last_cache_update = None

    def get_lead_by_domain(self, domain: str) -> Optional[Lead]:
        """Get lead by domain, loading from files if needed.

        Args:
            domain: Business domain

        Returns:
            Lead object if found, None otherwise
        """
        # Check cache first
        if domain in self._leads_cache:
            return self._leads_cache[domain]

        # Search through lead files
        for json_file in self.leads_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    lead_data_list = json.load(f)

                for lead_data in lead_data_list:
                    if lead_data.get("domain") == domain:
                        lead = Lead.from_dict(lead_data)
                        self._leads_cache[domain] = lead
                        return lead
            except Exception:
                continue

        return None

    def update_lead_outreach_status(
        self,
        domain: str,
        status: str,
        message_id: Optional[str] = None,
        template_used: Optional[str] = None,
        bounced: bool = False,
        complained: bool = False,
        unsubscribed: bool = False
    ) -> bool:
        """Update outreach status for a lead.

        Args:
            domain: Business domain
            status: New outreach status ('not_contacted', 'contacted', 'responded', 'converted')
            message_id: Email message ID if applicable
            template_used: Email template name used
            bounced: Whether email bounced
            complained: Whether recipient complained
            unsubscribed: Whether recipient unsubscribed

        Returns:
            True if update successful, False otherwise
        """
        lead = self.get_lead_by_domain(domain)
        if not lead:
            logger.warning(f"Lead not found for domain: {domain}")
            return False

        # Update status
        old_status = lead.email_outreach_status
        lead.email_outreach_status = status

        # Update timestamp for status changes
        if status != old_status:
            if status == "contacted" and not lead.email_outreach_date:
                lead.email_outreach_date = datetime.now()
            elif status in ["responded", "converted"]:
                # These would typically be updated manually or via CRM integration
                pass

        # Update email tracking fields
        if message_id:
            lead.email_message_id = message_id
        if template_used:
            lead.email_template_used = template_used

        # Update negative indicators
        if bounced:
            lead.email_bounced = True
        if complained:
            lead.email_complained = True
        if unsubscribed:
            lead.email_unsubscribed = True

        # Save updated lead
        success = self._save_lead_to_file(lead)
        if success:
            # Update cache
            self._leads_cache[domain] = lead
            logger.info(f"✅ Updated outreach status for {domain}: {old_status} → {status}")
        else:
            logger.error(f"❌ Failed to save updated lead for {domain}")

        return success

    def mark_lead_contacted(
        self,
        domain: str,
        message_id: Optional[str] = None,
        template_used: Optional[str] = None
    ) -> bool:
        """Mark a lead as contacted via email.

        Args:
            domain: Business domain
            message_id: Email message ID
            template_used: Email template used

        Returns:
            True if successful, False otherwise
        """
        return self.update_lead_outreach_status(
            domain=domain,
            status="contacted",
            message_id=message_id,
            template_used=template_used
        )

    def increment_follow_up_count(self, domain: str) -> bool:
        """Increment follow-up count for a lead.

        Args:
            domain: Business domain

        Returns:
            True if successful, False otherwise
        """
        lead = self.get_lead_by_domain(domain)
        if not lead:
            return False

        lead.email_follow_up_count += 1
        lead.email_last_follow_up = datetime.now()

        success = self._save_lead_to_file(lead)
        if success:
            self._leads_cache[domain] = lead

        return success

    def get_leads_by_outreach_status(self, status: str) -> List[Lead]:
        """Get all leads with a specific outreach status.

        Args:
            status: Outreach status to filter by

        Returns:
            List of leads with the specified status
        """
        all_leads = self._load_all_leads()
        return [lead for lead in all_leads if lead.email_outreach_status == status]

    def get_eligible_leads_for_outreach(
        self,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        exclude_bounced: bool = True,
        exclude_complained: bool = True,
        exclude_unsubscribed: bool = True,
        max_age_days: Optional[int] = None
    ) -> List[Lead]:
        """Get leads eligible for email outreach.

        Args:
            industry: Filter by industry
            location: Filter by location
            exclude_bounced: Exclude bounced email leads
            exclude_complained: Exclude complained leads
            exclude_unsubscribed: Exclude unsubscribed leads
            max_age_days: Only include leads contacted within this many days (None for all)

        Returns:
            List of eligible leads
        """
        all_leads = self._load_all_leads()
        eligible_leads = []

        for lead in all_leads:
            # Must have email
            if not lead.email:
                continue

            # Filter by industry/location if specified
            if industry and lead.industry and industry.lower() not in lead.industry.lower():
                continue
            if location and lead.location and location.lower() not in lead.location.lower():
                continue

            # Exclude based on negative indicators
            if exclude_bounced and lead.email_bounced:
                continue
            if exclude_complained and lead.email_complained:
                continue
            if exclude_unsubscribed and lead.email_unsubscribed:
                continue

            # Filter by outreach status - only contact leads that haven't been contacted yet
            if lead.email_outreach_status != "not_contacted":
                continue

            # Filter by age if specified
            if max_age_days and lead.email_outreach_date:
                days_since_contact = (datetime.now() - lead.email_outreach_date).days
                if days_since_contact > max_age_days:
                    continue

            eligible_leads.append(lead)

        return eligible_leads

    def get_outreach_metrics(
        self,
        industry: Optional[str] = None,
        location: Optional[str] = None
    ) -> OutreachMetrics:
        """Calculate outreach metrics.

        Args:
            industry: Filter by industry
            location: Filter by location

        Returns:
            OutreachMetrics object with calculated metrics
        """
        all_leads = self._load_all_leads()

        # Filter leads if specified
        if industry or location:
            filtered_leads = []
            for lead in all_leads:
                if industry and lead.industry and industry.lower() not in lead.industry.lower():
                    continue
                if location and lead.location and location.lower() not in lead.location.lower():
                    continue
                filtered_leads.append(lead)
            all_leads = filtered_leads

        metrics = OutreachMetrics(total_leads=len(all_leads))

        for lead in all_leads:
            if lead.email_outreach_status == "contacted":
                metrics.contacted_leads += 1
            elif lead.email_outreach_status == "responded":
                metrics.contacted_leads += 1
                metrics.responded_leads += 1
            elif lead.email_outreach_status == "converted":
                metrics.contacted_leads += 1
                metrics.responded_leads += 1
                metrics.converted_leads += 1

            if lead.email_bounced:
                metrics.bounced_emails += 1
            if lead.email_complained:
                metrics.complained_emails += 1
            if lead.email_unsubscribed:
                metrics.unsubscribed_emails += 1

        metrics.calculate_rates()
        return metrics

    def _load_all_leads(self) -> List[Lead]:
        """Load all leads from the leads directory.

        Returns:
            List of all leads
        """
        leads = []

        for json_file in self.leads_dir.rglob("*.json"):
            # Skip config files
            if "config" in str(json_file):
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    lead_data_list = json.load(f)

                for lead_data in lead_data_list:
                    lead = Lead.from_dict(lead_data)
                    leads.append(lead)
                    # Update cache
                    self._leads_cache[lead.domain] = lead

            except Exception as e:
                logger.warning(f"Failed to load leads from {json_file}: {e}")
                continue

        return leads

    def _save_lead_to_file(self, lead: Lead) -> bool:
        """Save a lead back to its source file.

        Args:
            lead: Lead to save

        Returns:
            True if successful, False otherwise
        """
        # Find the file containing this lead
        for json_file in self.leads_dir.rglob("*.json"):
            if "config" in str(json_file):
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    lead_data_list = json.load(f)

                # Find and update the lead
                for i, lead_data in enumerate(lead_data_list):
                    if lead_data.get("domain") == lead.domain:
                        lead_data_list[i] = lead.to_dict()

                        # Write back to file
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(lead_data_list, f, indent=2, ensure_ascii=False)

                        return True

            except Exception as e:
                logger.warning(f"Failed to update lead in {json_file}: {e}")
                continue

        logger.warning(f"Could not find source file for lead: {lead.domain}")
        return False

    def export_outreach_report(self, output_file: str) -> None:
        """Export comprehensive outreach report.

        Args:
            output_file: Path to output file
        """
        all_leads = self._load_all_leads()
        metrics = self.get_outreach_metrics()

        report = {
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_leads": metrics.total_leads,
                "contacted_leads": metrics.contacted_leads,
                "responded_leads": metrics.responded_leads,
                "converted_leads": metrics.converted_leads,
                "bounced_emails": metrics.bounced_emails,
                "complained_emails": metrics.complained_emails,
                "unsubscribed_emails": metrics.unsubscribed_emails,
                "response_rate": f"{metrics.response_rate:.2%}",
                "conversion_rate": f"{metrics.conversion_rate:.2%}",
                "bounce_rate": f"{metrics.bounce_rate:.2%}",
            },
            "leads_by_status": {
                "not_contacted": len([l for l in all_leads if l.email_outreach_status == "not_contacted"]),
                "contacted": len([l for l in all_leads if l.email_outreach_status == "contacted"]),
                "responded": len([l for l in all_leads if l.email_outreach_status == "responded"]),
                "converted": len([l for l in all_leads if l.email_outreach_status == "converted"]),
            },
            "recent_activity": [
                {
                    "domain": lead.domain,
                    "name": lead.name,
                    "status": lead.email_outreach_status,
                    "outreach_date": lead.email_outreach_date.isoformat() if lead.email_outreach_date else None,
                    "follow_ups": lead.email_follow_up_count,
                }
                for lead in sorted(
                    [l for l in all_leads if l.email_outreach_date],
                    key=lambda x: x.email_outreach_date,
                    reverse=True
                )[:10]  # Last 10 contacted
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Exported outreach report to {output_file}")


def main():
    """CLI interface for lead tracking."""
    import argparse

    parser = argparse.ArgumentParser(description="Lead Email Outreach Tracker")
    parser.add_argument("--leads-dir", default="pipeline/leads", help="Leads directory")
    parser.add_argument("--report", help="Export outreach report to file")
    parser.add_argument("--metrics", action="store_true", help="Show outreach metrics")
    parser.add_argument("--status", choices=["not_contacted", "contacted", "responded", "converted"],
                       help="Show leads with specific status")

    args = parser.parse_args()

    tracker = LeadTracker(args.leads_dir)

    if args.report:
        tracker.export_outreach_report(args.report)
        print(f"Report exported to {args.report}")

    if args.metrics:
        metrics = tracker.get_outreach_metrics()
        print("\n📊 Outreach Metrics:")
        print(f"Total Leads: {metrics.total_leads}")
        print(f"Contacted: {metrics.contacted_leads}")
        print(f"Responded: {metrics.responded_leads}")
        print(f"Converted: {metrics.converted_leads}")
        print(".2%"
              ".2%"
              ".2%")

    if args.status:
        leads = tracker.get_leads_by_outreach_status(args.status)
        print(f"\n📋 Leads with status '{args.status}':")
        for lead in leads[:10]:  # Show first 10
            print(f"  - {lead.name} ({lead.domain})")
        if len(leads) > 10:
            print(f"  ... and {len(leads) - 10} more")


if __name__ == "__main__":
    main()
