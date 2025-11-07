# Domain Configuration System

The Voice Agent now supports easy reconfiguration for different support domains (e.g., GitLab, McDonald's). This allows you to quickly switch the agent's purpose, tests, and evaluations without code changes.

## Quick Start

### Switch to a Different Domain

```bash
# Switch to McDonald's
python -m tools.switch_domain mcdonalds

# Switch and update ElevenLabs agent
python -m tools.switch_domain mcdonalds --update-agent

# Switch, update agent, and regenerate tests
python -m tools.switch_domain mcdonalds --update-agent --regenerate-tests
```

### List Available Domains

```bash
python -m tools.switch_domain --list
```

## What Gets Updated

When you switch domains, the following are automatically updated:

1. **System Prompt**: Agent personality, company name, and support type
2. **Evaluation Questions**: `dataset/eval.jsonl` is regenerated with domain-specific questions
3. **Test Scenarios**: Test suites use domain-specific scenarios
4. **Environment Configuration**: `.env` file is updated with `DOMAIN_ID`

Optionally (with flags):
- **ElevenLabs Agent Prompt**: Updates the agent's system prompt in ElevenLabs dashboard
- **Test Suites**: Regenerates test suites in ElevenLabs dashboard

## Architecture

### Domain Configuration Files

Domain configurations are stored in `domains/*.json` files. Each file contains:

- **Company/Product Info**: Company name, product name, industry
- **Agent Settings**: Agent name, support type
- **Test Scenarios**: Domain-specific test cases
- **Evaluation Questions**: Questions and expected answers for evaluation

### Code Integration

The domain configuration is integrated into:

1. **`core/domain_config.py`**: Domain configuration management
2. **`agents/system_prompt.py`**: Dynamic prompt generation based on domain
3. **`agents/test_suites.py`**: Domain-specific test scenario generation
4. **`eval/evaluate.py`**: Domain-specific evaluation questions
5. **`tools/switch_domain.py`**: Domain switching tool

## Creating a New Domain

### Option 1: Generate with OpenAI (Recommended)

The easiest way to create a new domain is to use OpenAI to automatically generate test scenarios and evaluation questions:

```bash
# Generate a new domain configuration
python -m tools.switch_domain mycompany --generate \
  --company "My Company" \
  --product "My Product" \
  --industry "technology" \
  --support-type "technical support"

# Generate and immediately switch to it
python -m tools.switch_domain mycompany --generate \
  --company "My Company" \
  --product "My Product" \
  --update-agent \
  --regenerate-tests
```

**Requirements:**
- Set `OPENAI_API_KEY` in Doppler: `doppler secrets set OPENAI_API_KEY=your_key`
- Install OpenAI package: `pip install openai>=1.0.0`

The generator will automatically create:
- 10 test scenarios (customizable with `--num-test-scenarios`)
- 10 evaluation questions (customizable with `--num-eval-questions`)
- Domain-specific prompts and configurations

### Option 2: Manual Creation

1. Create a JSON file in `domains/` directory:

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
      "name": "Password Reset",
      "messages": [
        {"role": "user", "content": "How do I reset my password?"}
      ],
      "expected_tool_calls": ["knowledgebase"],
      "expected_keywords": ["password", "reset"]
    }
  ],
  "eval_questions": [
    {
      "question": "How do I reset my password?",
      "expected_substring": "password"
    }
  ]
}
```

2. Switch to the new domain:

```bash
python -m tools.switch_domain mycompany --update-agent --regenerate-tests
```

## Environment Variables

The domain can be set via environment variable:

```bash
export DOMAIN_ID=mcdonalds
```

Or in `.env` file:

```
DOMAIN_ID=mcdonalds
```

## Example: Switching from GitLab to McDonald's

```bash
# 1. Switch domain
python -m tools.switch_domain mcdonalds

# 2. Update dataset (if needed)
python -m tools.ingest --dir dataset

# 3. Update ElevenLabs agent
python -m tools.switch_domain mcdonalds --update-agent

# 4. Regenerate tests
python -m tools.switch_domain mcdonalds --regenerate-tests
```

## Pre-configured Domains

- **gitlab**: GitLab technical support
- **mcdonalds**: McDonald's customer service

See `domains/README.md` for more details.

