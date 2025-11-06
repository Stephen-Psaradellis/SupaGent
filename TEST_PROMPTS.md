# Test Prompts for Voice Agent - Vector Store Connectivity

Use these natural language prompts with your ElevenLabs Voice Agent to test if it can successfully call the MCP tool and access your vector store.

## Basic Knowledge Base Queries

These prompts should trigger the agent to search the knowledge base:

### Password & Account Management
- "How do I reset my password?"
- "I forgot my password, what should I do?"
- "Can you help me change my account password?"
- "What's the process for password recovery?"

### General Support Questions
- "How do I contact customer support?"
- "What are your business hours?"
- "How can I update my account information?"
- "Where can I find my order history?"

### Product/Service Questions
- "What features are available in your product?"
- "How do I upgrade my subscription?"
- "What payment methods do you accept?"
- "Can you explain your refund policy?"

### Troubleshooting
- "I'm having trouble logging in, what should I do?"
- "My account is locked, how do I unlock it?"
- "I can't access my account, help me troubleshoot"
- "Something isn't working, what are common solutions?"

## Advanced Test Prompts

### Multi-step Queries
- "I need to reset my password and then update my email address. Can you walk me through both processes?"
- "What's the difference between password reset and account recovery?"
- "If I forget both my password and email, what are my options?"

### Contextual Follow-ups
- First: "How do I reset my password?"
- Follow-up: "What if I don't have access to my email?"
- Follow-up: "Can you provide more details about that process?"

### Specific Document Searches
- "Show me the documentation about password policies"
- "What does the user guide say about account settings?"
- "Find information about security best practices"

## Verification Prompts

Use these to check if the agent is actually using the tool:

### Direct Tool Requests
- "Can you search the knowledge base for information about passwords?"
- "Please look up the answer to my question in your documentation"
- "Search your database for information about account recovery"
- "Check your knowledge base for troubleshooting steps"

### Meta Queries
- "What sources did you use to answer that question?"
- "Can you cite where you found that information?"
- "What documentation did you reference?"

## Expected Behavior

When the agent successfully uses the MCP tool, you should:

1. **Hear the agent mention searching or looking up information**
   - "Let me search our knowledge base..."
   - "I'll look that up for you..."
   - "Checking our documentation..."

2. **Get specific, source-backed answers**
   - Answers should reference specific documents or titles
   - Should include relevant details from your vector store

3. **See tool calls in logs** (if available)
   - Check server logs for `/tools/search_knowledge_base` or `/mcp` endpoint calls
   - Monitor `/test/full_chain` to see if queries are being processed

## Testing Checklist

- [ ] Agent responds to basic knowledge base queries
- [ ] Agent mentions searching/looking up information
- [ ] Answers include specific details from your documentation
- [ ] Follow-up questions work correctly
- [ ] Agent can handle queries about different topics
- [ ] Server logs show tool endpoint calls
- [ ] `/test/full_chain` shows successful results

## Troubleshooting

If the agent doesn't seem to be using the tool:

1. **Check MCP Server Configuration**
   - Visit `http://localhost:8000/config/eleven`
   - Verify `mcp_server.status` is "configured"
   - Check for any errors

2. **Verify Vector Store Has Data**
   - Visit `http://localhost:8000/test/vector_store?query=password`
   - Should return results if data is ingested

3. **Test MCP Endpoint Directly**
   - Visit `http://localhost:8000/test/mcp_endpoint`
   - Should return tool definitions

4. **Check Agent Settings in ElevenLabs Dashboard**
   - Ensure the MCP server is connected to your agent
   - Verify tool approval settings allow automatic tool calls

## Sample Conversation Flow

**User:** "How do I reset my password?"

**Expected Agent Response:**
- "Let me search our knowledge base for information about password reset..."
- [Agent calls MCP tool]
- "According to our documentation, to reset your password you need to..."
- "You can find more details in our Password Reset guide."

**User:** "What if I don't have access to my email?"

**Expected Agent Response:**
- "Let me look up alternative methods for account recovery..."
- [Agent calls MCP tool again]
- "If you don't have access to your email, you can..."

