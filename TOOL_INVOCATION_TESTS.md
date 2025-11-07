# Tool Invocation Tests

## Overview

This document describes the 5 tool invocation tests designed to verify that the `search_knowledge_base` MCP tool is correctly invoked by the ElevenLabs Agent.

## Important Note: API Limitation

⚠️ **The ElevenLabs API has a limitation**: It does not allow `tool_call_parameters` (tool evaluation) to be used together with `success_condition`, `success_examples`, and `failure_examples` (message evaluation). However, the API also requires these fields for all tests.

This creates a contradiction that prevents creating true tool invocation tests via the API. The tests are designed as tool invocation tests but may need to be created manually in the ElevenLabs dashboard with the correct configuration.

## The 5 Tool Invocation Tests

These tests are designed to verify tool invocation for the `search_knowledge_base` tool:

### 1. Tool Invocation Test 1 - Password Reset
- **Query**: "How do I reset my password?"
- **Expected Tool**: `search_knowledge_base`
- **Purpose**: Verify tool is invoked for password-related queries

### 2. Tool Invocation Test 2 - Account Recovery
- **Query**: "I need to recover my account"
- **Expected Tool**: `search_knowledge_base`
- **Purpose**: Verify tool is invoked for account recovery queries

### 3. Tool Invocation Test 3 - Troubleshooting
- **Query**: "I'm having trouble logging in"
- **Expected Tool**: `search_knowledge_base`
- **Purpose**: Verify tool is invoked for troubleshooting queries

### 4. Tool Invocation Test 4 - Policy Query
- **Query**: "What is your refund policy?"
- **Expected Tool**: `search_knowledge_base`
- **Purpose**: Verify tool is invoked for policy-related queries

### 5. Tool Invocation Test 5 - Support Contact
- **Query**: "How do I contact customer support?"
- **Expected Tool**: `search_knowledge_base`
- **Purpose**: Verify tool is invoked for support contact queries

## Creating the Tests

### Via CLI (May Fail Due to API Limitation)

```bash
python -m tools.create_elevenlabs_tests --suite tool-invocation
```

### Manual Creation in Dashboard

Due to the API limitation, you may need to create these tests manually in the ElevenLabs dashboard:

1. Go to: `https://elevenlabs.io/app/agents/{YOUR_AGENT_ID}/tests`
2. Click "Create Test"
3. For each test:
   - Set **Type** to `tool` (not `llm`)
   - Add the chat history (user message)
   - Set **Tool Call Parameters**:
     - Tool: `search_knowledge_base`
     - Verify absence: `false`
   - **Do NOT** set success_condition, success_examples, or failure_examples
   - Save the test

## Available Tools

The MCP server exposes one tool:

- **`search_knowledge_base`**: Searches the customer support knowledge base
  - Parameters:
    - `query` (required): The search query string
    - `k` (optional): Number of results to return (default: 4, max: 10)

## Test Verification

These tests verify that:
1. The agent recognizes when to use the tool
2. The tool is invoked with appropriate queries
3. The tool call parameters are correct

## Workaround

If the API continues to reject tool invocation tests, you can:
1. Create the tests manually in the dashboard as described above
2. Use the comprehensive test suite which verifies tool usage through response content
3. Monitor tool usage through the ElevenLabs dashboard analytics
