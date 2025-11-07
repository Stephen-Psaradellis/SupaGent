# Test Execution Troubleshooting

## Expected Test Execution Times

- **Normal execution**: 2-5 minutes for 15 tests
- **Tool invocation tests**: ~30 seconds each
- **LLM/comprehensive tests**: ~1-2 minutes each

## If Tests Take 15-20+ Minutes

This is **abnormal** and indicates a potential issue:

### Common Causes

1. **Tests are stuck/hanging**
   - Tool calls timing out
   - Agent waiting for responses that never come
   - Network connectivity issues

2. **Agent configuration problems**
   - MCP server not accessible
   - Tool endpoints returning errors
   - Agent doesn't have proper tool access

3. **API/Platform issues**
   - ElevenLabs platform delays
   - Rate limiting
   - Service degradation

### How to Check Status

**Best method: Use the ElevenLabs Dashboard**
```
https://elevenlabs.io/app/agents/{YOUR_AGENT_ID}/tests
```

In the dashboard you can:
- See real-time test execution status
- View which tests passed/failed
- See detailed error messages
- Cancel stuck tests

### Troubleshooting Steps

1. **Check Dashboard First**
   - Navigate to the tests page
   - Look for any tests marked as "running" for extended periods
   - Check for error messages

2. **Verify Agent Configuration**
   ```bash
   curl http://localhost:8000/config/eleven
   ```
   - Ensure MCP server is configured
   - Verify tool endpoints are accessible

3. **Test Tool Endpoints Manually**
   ```bash
   curl -X POST http://localhost:8000/tools/search_knowledge_base \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "k": 1}'
   ```

4. **Run a Single Test**
   - Instead of running all 15 tests, try running just 1-2 tests
   - This helps isolate if the issue is with specific tests or all tests

5. **Check Agent Logs**
   - If deployed, check application logs for errors
   - Look for tool call failures or timeouts

### If Tests Are Stuck

1. **Cancel in Dashboard**: Cancel the stuck test run
2. **Verify Tool Access**: Ensure agent has MCP server access
3. **Check Endpoints**: Verify all tool endpoints are responding
4. **Re-run Smaller Set**: Try running 2-3 tests instead of all 15

### Normal Test Flow

1. Test submitted → Status: "pending"
2. Test starts → Status: "running" 
3. Agent processes query → Tool calls made
4. Results evaluated → Status: "passed" or "failed"
5. **Total time: 1-3 minutes per test**

If a test stays in "running" for >5 minutes, it's likely stuck.

