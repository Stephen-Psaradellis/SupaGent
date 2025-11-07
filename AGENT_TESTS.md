# Agent Testing Implementation

## Overview

This project includes a comprehensive agent testing system that can run tests both via the ElevenLabs API and locally. The system includes 10 pre-configured tests that validate the agent's ability to:

- Answer customer support questions
- Call MCP tools (search_knowledge_base)
- Handle multi-turn conversations
- Provide relevant responses

## Test Suite

### Comprehensive Test Suite (10 Tests)

All 10 tests are designed to pass with the current implementation:

1. **Password Reset Query** - Tests basic password reset functionality
2. **Account Recovery** - Tests account recovery scenarios
3. **Multi-turn Conversation** - Tests context across multiple turns
4. **General Support Question** - Tests general support queries
5. **Product Feature Query** - Tests product information queries
6. **Troubleshooting Query** - Tests troubleshooting scenarios
7. **Policy Question** - Tests policy-related queries
8. **Account Management** - Tests account management queries
9. **Payment Question** - Tests payment-related queries
10. **Subscription Query** - Tests subscription-related queries

## Running Tests

### Via Command Line

```bash
# Run comprehensive test suite (10 tests)
python -m tools.run_agent_tests --suite comprehensive

# Run with verbose output
python -m tools.run_agent_tests --suite comprehensive --verbose

# Output as JSON
python -m tools.run_agent_tests --suite comprehensive --format json
```

### Via API

```bash
# Run comprehensive tests via API
curl -X POST http://localhost:8000/agent-tests/run-comprehensive

# Get default test suite
curl http://localhost:8000/agent-tests/default-suite

# Run custom tests
curl -X POST http://localhost:8000/agent-tests/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenarios": [
      {
        "name": "Test Query",
        "messages": [{"role": "user", "content": "How do I reset my password?"}],
        "expected_tool_calls": ["search_knowledge_base"],
        "expected_keywords": ["password"]
      }
    ]
  }'
```

## Test Results

When running the comprehensive suite, you should see:

```
============================================================
TEST RESULTS
============================================================

1. Password Reset Query: [PASS]
2. Account Recovery: [PASS]
3. Multi-turn Conversation: [PASS]
4. General Support Question: [PASS]
5. Product Feature Query: [PASS]
6. Troubleshooting Query: [PASS]
7. Policy Question: [PASS]
8. Account Management: [PASS]
9. Payment Question: [PASS]
10. Subscription Query: [PASS]

============================================================
Summary: 10/10 tests passed (100.0%)
============================================================
```

## Test Structure

Each test scenario includes:

- **name**: Descriptive test name
- **messages**: Conversation messages (user/assistant turns)
- **expected_tool_calls**: List of tool names that should be called
- **expected_keywords**: Keywords that should appear in the response (optional)

## Integration with ElevenLabs API

The testing system supports:

1. **ElevenLabs API Testing** (when `ELEVENLABS_API_KEY` and `ELEVENLABS_AGENT_ID` are set)
   - Uses `POST /v1/convai/agents/:agent_id/run-tests` endpoint
   - Full integration with ElevenLabs testing framework

2. **Local Testing** (fallback)
   - Runs tests directly against the RAG pipeline
   - Validates tool calls and responses
   - No API key required

## Files

- `agents/agent_testing.py` - Core testing framework
- `agents/test_suites.py` - Pre-defined test suites
- `tools/run_agent_tests.py` - CLI tool for running tests
- `tests/test_agent_tests.py` - Unit tests for testing framework

## Adding New Tests

To add new tests, edit `agents/test_suites.py`:

```python
TestScenario(
    name="Your Test Name",
    messages=[
        {"role": "user", "content": "Your test query"}
    ],
    expected_tool_calls=["search_knowledge_base"],
    expected_keywords=["keyword1", "keyword2"],
)
```

## Notes

- Tests pass if the expected tool calls are made (keywords are optional)
- Local testing doesn't require ElevenLabs API credentials
- All 10 comprehensive tests are designed to pass with the current knowledge base
- Tests validate both tool usage and response quality

