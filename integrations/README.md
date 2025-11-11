# Integrations

This directory contains integration adapters for external services and APIs.

## Apollo.io Connector

The Apollo.io connector provides a complete workflow for discovering, enriching, and managing contacts using Apollo.io's API.

### Features

- **People Search**: Search for people using specific job titles, industry keywords, and location filters
- **Deduplication**: Check existing contacts to avoid creating duplicates
- **Bulk Enrichment**: Enrich person data with additional information
- **Bulk Contact Creation**: Add enriched contacts to your Apollo.io database

### Quick Start

```python
from integrations import ApolloConnector

# Initialize the connector
connector = ApolloConnector(api_key="your_api_key_here")

# Or set APOLLO_API_KEY environment variable and use:
connector = ApolloConnector()

# Execute the complete workflow
result = await connector.execute_workflow(
    industry="software development",
    location="Chicago",
    limit=50
)

print(f"Found {result['stats']['people_found']} people")
print(f"Created {result['stats']['created']} contacts")
```

### Synchronous Usage

For simpler use cases, you can use the synchronous wrapper:

```python
from integrations import search_and_create_contacts

result = search_and_create_contacts(
    industry="real estate",
    location="Chicago",
    limit=100
)
```

### API Endpoints Used

The connector implements the following Apollo.io API endpoints:

1. **POST** `https://api.apollo.io/api/v1/mixed_people/search`
   - Searches for people with specific filters

2. **POST** `https://api.apollo.io/api/v1/contacts/search`
   - Checks for existing contacts to avoid duplication

3. **POST** `https://api.apollo.io/api/v1/people/bulk_enrich`
   - Enriches people with additional data

4. **POST** `https://api.apollo.io/api/v1/contacts/bulk_create`
   - Creates new contacts in bulk

### Configuration

Set your Apollo.io API key using one of these methods:

1. **Environment Variable**:
   ```bash
   export APOLLO_API_KEY="your_api_key_here"
   ```

2. **Direct Parameter**:
   ```python
   connector = ApolloConnector(api_key="your_api_key_here")
   ```

### Default Search Filters

The connector uses these default filters for people search:

- **Job Titles**: `['owner', 'director', 'general manager', 'partner']`
- **Location**: `'Chicago'` (customizable)
- **Industry**: Based on provided keywords

You can customize job titles when calling the workflow:

```python
result = await connector.execute_workflow(
    industry="healthcare",
    location="Chicago",
    job_titles=["CEO", "CFO", "CTO", "CMO"]
)
```

### Response Format

The workflow returns a comprehensive result dictionary:

```python
{
    "success": True,
    "message": "Successfully processed 25 contacts",
    "stats": {
        "people_found": 30,
        "existing_contacts": 5,
        "new_people": 25,
        "enriched": 25,
        "created": 25,
        "duration_seconds": 45.67
    },
    "created_contacts": [...],  # List of created contact details
    "existing_contacts_found": [...]  # List of emails that already existed
}
```

### Error Handling

The connector includes comprehensive error handling:

- Network timeouts and retries
- Invalid API responses
- Missing API keys
- Rate limiting (inherited from httpx client)

All errors are logged and appropriate fallback behavior is implemented.

### Testing

Run the test suite:

```bash
python -m pytest tests/test_apollo_connector.py
```

### CLI Usage

You can also run the connector from command line:

```bash
python integrations/apollo.py "software development"
```

This will search for contacts in the software development industry in Chicago and display results.
