"""
Apollo.io Search Connector for Contact Management.

This connector implements a specific workflow for discovering and managing contacts
using Apollo.io's API endpoints. The workflow follows these steps:

1. Search for people using mixed_people/search with specific filters
2. Check existing contacts to avoid duplication using search-for-contacts
3. Enrich new people using bulk-people-enrichment
4. Add enriched people to contacts using bulk-create-contacts

The connector uses the following API endpoints:
- POST https://api.apollo.io/api/v1/mixed_people/search
- POST https://api.apollo.io/api/v1/contacts/search (to check existing contacts)
- POST https://api.apollo.io/api/v1/people/bulk_enrich (bulk enrichment)
- POST https://api.apollo.io/api/v1/contacts/bulk_create (bulk create contacts)

Required configuration:
- APOLLOIO_API_KEY environment variable or config setting
- Industry parameter for search filtering
- Location parameter (currently hardcoded to Chicago as per requirements)
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from core.http_client import get_http_client
from core.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class ApolloContact:
    """Represents a contact in Apollo.io system."""

    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    title: Optional[str] = None
    organization_name: Optional[str] = None
    organization_website: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone_numbers: Optional[List[Dict[str, Any]]] = None
    location: Optional[str] = None
    industry: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> ApolloContact:
        """Create ApolloContact from API response data."""
        return cls(
            id=data.get("id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            name=data.get("name"),
            email=data.get("email"),
            title=data.get("title"),
            organization_name=data.get("organization", {}).get("name") if data.get("organization") else None,
            organization_website=data.get("organization", {}).get("website_url") if data.get("organization") else None,
            linkedin_url=data.get("linkedin_url"),
            phone_numbers=data.get("phone_numbers", []),
            location=data.get("city") or data.get("state"),
            industry=data.get("organization", {}).get("industry") if data.get("organization") else None,
        )


@dataclass
class ApolloSearchFilters:
    """Search filters for Apollo.io people search."""

    job_titles: List[str]
    industry_keywords: str
    location: str
    per_page: int
    page: int

    def to_payload(self) -> Dict[str, Any]:
        """Convert filters to API payload format."""
        return {
            "person_titles": self.job_titles,
            "q_keywords": self.industry_keywords,
            "organization_locations": [self.location],
            "page": self.page,
            "per_page": self.per_page,
        }


class ApolloConnector:
    """
    Apollo.io connector for contact search and management.

    This connector implements the complete workflow:
    1. Search for people with specific job titles in target industry/location
    2. Check existing contacts to avoid duplication
    3. Bulk enrich new people with additional data
    4. Bulk create contacts in Apollo.io
    """

    BASE_URL = "https://api.apollo.io/api/v1"
    SEARCH_URL = f"{BASE_URL}/mixed_people/search"
    CONTACTS_SEARCH_URL = f"{BASE_URL}/contacts/search"
    BULK_ENRICH_URL = f"{BASE_URL}/people/bulk_match"
    BULK_CREATE_CONTACTS_URL = f"{BASE_URL}/contacts/bulk_create"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Apollo connector.

        Args:
            api_key: Apollo.io API key. If not provided, will attempt to get from
                    APOLLOIO_API_KEY environment variable or config.
        """
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            raise ValueError("Apollo API key is required. Set APOLLOIO_API_KEY environment variable.")

        self.http_client = get_http_client(timeout=30.0)

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        import os
        api_key = os.getenv("APOLLOIO_API_KEY")
        if not api_key:
            try:
                config = get_config()
                api_key = getattr(config, "apollo_api_key", None)
            except Exception:
                pass
        return api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

    async def search_people(
        self,
        industry: str,
        location: str = "Chicago",
        job_titles: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[ApolloContact]:
        """
        Search for people using Apollo.io mixed_people/search endpoint.

        Args:
            industry: Industry keywords to search for
            location: Location to search in (default: Chicago)
            job_titles: List of job titles to filter by. If None, uses default titles.
            limit: Maximum number of results to return

        Returns:
            List of ApolloContact objects (may include people without emails)
        """
        if job_titles is None:
            job_titles = ["owner", "director", "general manager", "partner"]

        filters = ApolloSearchFilters(
            job_titles=job_titles,
            industry_keywords=industry,
            location=location,
            page=1,
            per_page=100  # Always use max page size to minimize API calls
        )

        contacts = []
        total_raw_results = 0

        while len(contacts) < limit:
            payload = filters.to_payload()

            logger.info(f"Searching Apollo for people with filters: {payload}")

            try:
                response = self.http_client.post(
                    self.SEARCH_URL,
                    json=payload,
                    headers=self._get_headers(),
                )
                response.raise_for_status()

                data = response.json()
                people = data.get("people", [])

                if not people:
                    logger.info(f"No people found on page {filters.page}, stopping")
                    break

                total_raw_results += len(people)
                logger.info(f"Found {len(people)} people in page {filters.page}")

                for person_data in people:
                    contact = ApolloContact.from_api_response(person_data)
                    contacts.append(contact)

                    if len(contacts) >= limit:
                        logger.info(f"Reached limit of {limit} contacts, stopping pagination")
                        break

                # Check if there are more pages
                pagination = data.get("pagination", {})
                current_page = pagination.get("page", filters.page)
                total_pages = pagination.get("total_pages", 1)
                total_entries = pagination.get("total_entries", 0)

                # Check if we've reached the last page or hit our limit
                if current_page >= total_pages:
                    break

                if len(contacts) >= limit:
                    break

                filters.page += 1

            except Exception as e:
                logger.error(f"Error searching Apollo people: {e}")
                break

        logger.info(f"Total people found: {len(contacts)} (from {total_raw_results} raw results)")
        return contacts[:limit]

    async def search_existing_contacts(
        self,
        emails: List[str],
        limit: int = 1000,
    ) -> Dict[str, ApolloContact]:
        """
        Search for existing contacts in Apollo.io to avoid duplication.

        Args:
            emails: List of email addresses to check
            limit: Maximum contacts to search for

        Returns:
            Dictionary mapping email addresses to existing ApolloContact objects
        """
        if not emails:
            return {}

        existing_contacts = {}

        # Apollo allows searching by email, but we need to do this in batches
        # since there might be limits on the number of emails per request
        batch_size = 50  # Conservative batch size

        for i in range(0, len(emails), batch_size):
            email_batch = emails[i : i + batch_size]

            payload = {
                "q_emails": email_batch,
            }

            try:
                logger.info(f"Checking for existing contacts batch {i//batch_size + 1}: {len(email_batch)} emails")

                response = self.http_client.post(
                    self.CONTACTS_SEARCH_URL,
                    json=payload,
                    headers=self._get_headers(),
                )
                response.raise_for_status()

                data = response.json()
                contacts = data.get("contacts", [])

                for contact_data in contacts:
                    contact = ApolloContact.from_api_response(contact_data)
                    if contact.email:
                        existing_contacts[contact.email.lower()] = contact

                logger.info(f"Found {len(contacts)} existing contacts in this batch")

            except Exception as e:
                logger.error(f"Error searching existing contacts batch {i//batch_size + 1}: {e}")
                continue

        logger.info(f"Total existing contacts found: {len(existing_contacts)}")
        return existing_contacts

    async def bulk_enrich_people(
        self,
        contacts: List[ApolloContact],
    ) -> List[ApolloContact]:
        """
        Bulk enrich people with additional data using Apollo's bulk people enrichment.
        Handles batching since the API only allows up to 10 people per request.

        Args:
            contacts: List of ApolloContact objects to enrich

        Returns:
            List of enriched ApolloContact objects
        """
        if not contacts:
            return []

        # Prepare details for bulk enrichment
        valid_contacts = []
        for contact in contacts:
            detail = {}

            # Add identifying information - the API prefers specific identifiers over IDs
            # Don't include placeholder emails
            if contact.email and not contact.email.startswith("email_not_unlocked"):
                detail["email"] = contact.email
            if contact.first_name:
                detail["first_name"] = contact.first_name
            if contact.last_name:
                detail["last_name"] = contact.last_name
            if contact.organization_name:
                detail["organization_name"] = contact.organization_name
            if contact.organization_website:
                detail["website"] = contact.organization_website
            if contact.title:
                detail["title"] = contact.title

            # Only include if we have meaningful identifying information
            # Require at least name + organization or email
            has_email = bool(contact.email and not contact.email.startswith("email_not_unlocked"))
            has_name = bool(contact.first_name or contact.last_name)
            has_org = bool(contact.organization_name or contact.organization_website)

            if has_email or (has_name and has_org):
                # Store the detail with the contact for batching
                contact._enrich_detail = detail
                valid_contacts.append(contact)
            else:
                logger.debug(f"Skipping contact with insufficient identifying info: {contact.first_name} {contact.last_name} at {contact.organization_name}")

        if not valid_contacts:
            logger.warning("No valid contacts to enrich")
            return contacts

        # Process in batches of 10 (API limit)
        batch_size = 10
        all_enriched_contacts = []

        for i in range(0, len(valid_contacts), batch_size):
            batch_contacts = valid_contacts[i:i + batch_size]
            batch_details = [contact._enrich_detail for contact in batch_contacts]

            payload = {
                "details": batch_details,
                "reveal_personal_emails": True,
            }

            logger.debug(f"Bulk enriching batch {i//batch_size + 1} with {len(batch_details)} people")

            try:
                response = self.http_client.post(
                    self.BULK_ENRICH_URL,
                    json=payload,
                    headers=self._get_headers(),
                )
                response.raise_for_status()

                data = response.json()
                matches = data.get("matches", [])

                logger.debug(f"Batch {i//batch_size + 1} response summary: {data.get('total_requested_enrichments')} requested, {data.get('unique_enriched_records')} enriched")

                enriched_count = 0
                for match_data in matches:
                    if match_data is not None:  # Skip null matches
                        contact = ApolloContact.from_api_response(match_data)
                        all_enriched_contacts.append(contact)
                        enriched_count += 1

                logger.debug(f"Batch {i//batch_size + 1} processed {enriched_count} enriched people")

                logger.debug(f"Successfully enriched batch {i//batch_size + 1} ({enriched_count} people)")

            except Exception as e:
                logger.error(f"Error bulk enriching batch {i//batch_size + 1}: {e}")
                # Try to get more details from the response
                try:
                    if hasattr(e, 'response') and e.response:
                        logger.error(f"Response status: {e.response.status_code}")
                        logger.error(f"Response body: {e.response.text[:500]}")
                except:
                    pass
                # For failed batches, return the original contacts
                all_enriched_contacts.extend(batch_contacts)

        logger.info(f"Successfully enriched {len(all_enriched_contacts)} people in {len(valid_contacts)//batch_size + 1} batches")
        return all_enriched_contacts

    async def bulk_create_contacts(
        self,
        contacts: List[ApolloContact],
    ) -> List[Dict[str, Any]]:
        """
        Bulk create contacts in Apollo.io.

        Args:
            contacts: List of ApolloContact objects to create

        Returns:
            List of creation results (success/failure status for each contact)
        """
        if not contacts:
            return []

        # Prepare contacts for bulk creation
        contact_payloads = []
        for contact in contacts:
            contact_data = {
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "title": contact.title,
                "organization_name": contact.organization_name,
                "organization_website": contact.organization_website,
                "linkedin_url": contact.linkedin_url,
                "location": contact.location,
            }

            # Remove None values
            contact_data = {k: v for k, v in contact_data.items() if v is not None}
            contact_payloads.append(contact_data)

        payload = {
            "contacts": contact_payloads,
        }

        try:
            logger.info(f"Bulk creating {len(contact_payloads)} contacts")

            response = self.http_client.post(
                self.BULK_CREATE_CONTACTS_URL,
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()

            data = response.json()
            results = data.get("created_contacts", [])

            logger.debug(f"Bulk create response contains {len(results)} created contacts")
            logger.info(f"Successfully created contacts. Results: {len(results)}")
            return results

        except Exception as e:
            logger.error(f"Error bulk creating contacts: {e}")
            return []

    async def execute_workflow(
        self,
        industry: str,
        location: str = "Chicago",
        job_titles: Optional[List[str]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Execute the complete Apollo.io contact management workflow.

        1. Search for people with specified filters
        2. Check existing contacts to avoid duplication
        3. Bulk enrich new people
        4. Bulk create contacts

        Args:
            industry: Industry keywords to search for
            location: Location to search in
            job_titles: Job titles to filter by (optional, uses defaults if None)
            limit: Maximum number of people to process

        Returns:
            Dictionary with workflow results including stats and created contacts
        """
        logger.info(f"Starting Apollo.io workflow for {industry} in {location}")

        start_time = datetime.now()

        # Step 1: Search for people
        logger.info("Step 1: Searching for people...")
        found_people = await self.search_people(industry, location, job_titles, limit)

        if not found_people:
            return {
                "success": False,
                "message": "No people found matching criteria",
                "stats": {"people_found": 0, "existing_contacts": 0, "enriched": 0, "created": 0},
                "created_contacts": [],
            }

        # Extract emails for deduplication check
        emails = [p.email for p in found_people if p.email]
        emails = list(set(emails))  # Remove duplicates

        # Step 2: Check existing contacts
        logger.info(f"Step 2: Checking {len(emails)} existing contacts...")
        existing_contacts = await self.search_existing_contacts(emails)

        # Filter out people who already exist as contacts
        new_people = []
        for person in found_people:
            if person.email and person.email.lower() in existing_contacts:
                logger.debug(f"Skipping existing contact: {person.email}")
                continue
            new_people.append(person)

        if not new_people:
            return {
                "success": True,
                "message": "All found people already exist as contacts",
                "stats": {
                    "people_found": len(found_people),
                    "existing_contacts": len(existing_contacts),
                    "enriched": 0,
                    "created": 0,
                },
                "created_contacts": [],
            }

        # Step 3: Bulk enrich new people
        logger.info(f"Step 3: Bulk enriching {len(new_people)} new people...")
        enriched_contacts = await self.bulk_enrich_people(new_people)

        # Step 4: Bulk create contacts
        logger.info(f"Step 4: Bulk creating {len(enriched_contacts)} contacts...")
        creation_results = await self.bulk_create_contacts(enriched_contacts)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        stats = {
            "people_found": len(found_people),
            "existing_contacts": len(existing_contacts),
            "new_people": len(new_people),
            "enriched": len(enriched_contacts),
            "created": len(creation_results),
            "duration_seconds": duration,
        }

        logger.info(f"Workflow completed in {duration:.2f}s. Stats: {stats}")

        return {
            "success": True,
            "message": f"Successfully processed {len(enriched_contacts)} contacts",
            "stats": stats,
            "created_contacts": creation_results,
            "existing_contacts_found": list(existing_contacts.keys()),
        }


# Synchronous wrapper for easier use
def search_and_create_contacts(
    industry: str,
    location: str = "Chicago",
    job_titles: Optional[List[str]] = None,
    limit: int = 100,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchronous wrapper for the Apollo.io contact workflow.

    Args:
        industry: Industry keywords to search for
        location: Location to search in
        job_titles: Job titles to filter by (optional)
        limit: Maximum number of people to process
        api_key: Apollo API key (optional, will use env/config if not provided)

    Returns:
        Workflow results dictionary
    """
    connector = ApolloConnector(api_key=api_key)
    return asyncio.run(
        connector.execute_workflow(industry, location, job_titles, limit)
    )


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python apollo.py <industry>")
        print("Example: python apollo.py 'software development'")
        sys.exit(1)

    industry = sys.argv[1]
    result = search_and_create_contacts(industry=industry, limit=50)

    print("\nWorkflow Results:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    print("\nStats:")
    for key, value in result['stats'].items():
        print(f"  {key}: {value}")

    if result.get('created_contacts'):
        print(f"\nCreated {len(result['created_contacts'])} contacts")
