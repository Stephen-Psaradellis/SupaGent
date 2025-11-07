# Domain Configurations

This directory contains domain-specific configurations for the support agent. Each domain configuration defines:

- **Company/Product Information**: Company name, product name, industry
- **Agent Personality**: Agent name, support type
- **Test Scenarios**: Domain-specific test cases for ElevenLabs
- **Evaluation Questions**: Questions and expected answers for evaluation
- **Prompt Customizations**: Additional prompt sections (optional)

## Available Domains

- **gitlab.json**: GitLab technical support configuration
- **mcdonalds.json**: McDonald's customer service configuration

## Switching Domains

To switch to a different domain:

```bash
# Switch to McDonald's domain
python -m tools.switch_domain mcdonalds

# Switch and update ElevenLabs agent prompt
python -m tools.switch_domain mcdonalds --update-agent

# Switch, update agent, and regenerate tests
python -m tools.switch_domain mcdonalds --update-agent --regenerate-tests

# List all available domains
python -m tools.switch_domain --list
```

## Creating a New Domain

### Option 1: Generate with OpenAI (Recommended)

The easiest way to create a new domain is to use OpenAI to automatically generate all configurations:

```bash
# Set your OpenAI API key in Doppler
doppler secrets set OPENAI_API_KEY=your_api_key_here

# Generate a new domain
python -m tools.switch_domain mycompany --generate \
  --company "My Company" \
  --product "My Product" \
  --industry "technology" \
  --support-type "technical support"

# Generate with custom number of scenarios/questions
python -m tools.switch_domain mycompany --generate \
  --company "My Company" \
  --product "My Product" \
  --num-test-scenarios 15 \
  --num-eval-questions 20
```

This will automatically:
- Generate realistic test scenarios based on your domain
- Create evaluation questions with expected keywords
- Save the configuration to `domains/mycompany.json`
- Optionally switch to the new domain immediately

### Option 2: Manual Creation

1. Create a new JSON file in this directory (e.g., `mycompany.json`):

```json
{
  "domain_id": "mycompany",
  "company_name": "My Company",
  "product_name": "My Product",
  "agent_name": "Alex",
  "support_type": "customer support",
  "industry": "technology",
  "test_scenarios": [
    {
      "name": "Test Scenario Name",
      "messages": [
        {"role": "user", "content": "Customer question here"}
      ],
      "expected_tool_calls": ["knowledgebase"],
      "expected_keywords": ["keyword1", "keyword2"]
    }
  ],
  "eval_questions": [
    {
      "question": "Customer question?",
      "expected_substring": "expected answer keyword"
    }
  ],
  "prompt_customizations": {}
}
```

2. Switch to the new domain:

```bash
python -m tools.switch_domain mycompany --update-agent --regenerate-tests
```

## Domain Configuration Fields

- **domain_id**: Unique identifier (lowercase, no spaces)
- **company_name**: Full company name
- **product_name**: Product or service name
- **agent_name**: Name of the support agent
- **support_type**: Type of support (e.g., "technical support", "customer service")
- **industry**: Industry sector
- **test_scenarios**: Array of test scenario objects
- **eval_questions**: Array of evaluation question objects
- **prompt_customizations**: Optional prompt overrides (future use)

## Environment Variable

The domain can also be set via environment variable:

```bash
export DOMAIN_ID=mcdonalds
```

Or in `.env` file:

```
DOMAIN_ID=mcdonalds
```

## OpenAI Generation

When using OpenAI to generate domains, the service will:

1. **Generate Test Scenarios**: Creates realistic customer support scenarios covering:
   - Common support issues (account access, password reset, troubleshooting)
   - Product/service questions
   - Policy and procedure questions
   - Technical issues (if applicable)
   - Payment/billing questions (if applicable)

2. **Generate Evaluation Questions**: Creates questions with expected keywords that should appear in good answers.

3. **Customize Prompts**: Adapts prompts based on company, product, and industry context.

**Requirements:**
- `OPENAI_API_KEY` must be set in Doppler
- `openai>=1.0.0` package must be installed

**Cost:** Uses `gpt-4o-mini` by default (cost-efficient). Each domain generation typically costs $0.01-0.05 depending on the number of scenarios/questions requested.
