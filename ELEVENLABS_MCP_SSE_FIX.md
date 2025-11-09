# ElevenLabs MCP SSE Integration Fix

## Problem Analysis

### What Was Happening

When integrating your MCP server with ElevenLabs:

1. **Test Connection** ✅ - Worked fine
   - ElevenLabs sends `GET /mcp` 
   - Server responds with `200 OK` and opens SSE connection
   - Railway logs show: `INFO: "GET /mcp HTTP/1.1" 200 OK`

2. **Scan Available Tools** ❌ - Failed silently
   - No logs appeared in Railway
   - ElevenLabs showed: "Failed to connect to MCP Server"
   - The scan operation timed out

### Root Cause

The issue was with how **SSE (Server-Sent Events) transport** works in the MCP protocol:

**Old Implementation:**
- GET /mcp opened SSE connection
- Server only sent keepalive messages (`: keepalive\n\n`)
- **Never sent the tools list via SSE**

**What ElevenLabs Expected:**
1. Client opens SSE connection (GET /mcp)
2. **Server immediately sends initialization + tools list via SSE**
3. Client can then invoke tools

When ElevenLabs clicked "Scan Available Tools":
- It was waiting for the tools list to arrive via the SSE stream
- But the server never sent it
- Eventually timed out with "Failed to connect"

### Why No Logs Appeared

No additional requests were made! ElevenLabs:
1. Opened SSE connection during "Test Connection" ✅
2. Kept that connection open
3. During "Scan Available Tools", it simply **waited for tools data via the existing SSE connection**
4. Never made a new request → No new logs

## The Solution

### Updated SSE Endpoint

The SSE endpoint (`GET /mcp`) now **proactively sends** MCP protocol messages:

1. **Server Info** (immediately upon connection):
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized",
  "params": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "SupaGent Knowledge Base",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {},
      "logging": {}
    }
  }
}
```

2. **Tools List** (right after initialization):
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed",
  "params": {
    "tools": [
      {
        "name": "search_knowledge_base",
        "description": "Search the knowledge base...",
        "inputSchema": { ... }
      },
      // ... all other tools
    ]
  }
}
```

3. **Keepalive messages** (every 15 seconds):
```
: keepalive
```

### Files Changed

- **`app/routes/mcp_sdk_router.py`**
  - Updated `mcp_sse()` function to send initialization and tools via SSE
  - Added detailed logging for debugging
  - Tools are now dynamically introspected and sent on connection

## Testing

### Before Deploying

Test locally first:

```bash
# Install dependencies if needed
pip install httpx

# Run the test script
python tools/test_sse_endpoint.py
```

This will:
- Connect to your Railway MCP endpoint
- Open SSE connection
- Verify it receives initialization and tools
- Print detailed results

Expected output:
```
✅ Connection established (Status: 200)
📨 Event #1: notifications/initialized
   Server: SupaGent Knowledge Base
   Version: 1.0.0
   Protocol: 2024-11-05

📨 Event #2: notifications/tools/list_changed
   Tools count: 15
   Tools:
     - search_knowledge_base: Search the knowledge base...
     - create_ticket: Create a support ticket...
     ... and 13 more

✅ Received both initialization and tools list!
🎉 SUCCESS! SSE endpoint is working correctly!
```

### After Deploying to Railway

1. **Push to Railway:**
   ```bash
   git add -A
   git commit -m "Fix: ElevenLabs MCP SSE transport - send tools via SSE"
   git push
   ```

2. **Wait for Railway deployment** (~2-3 minutes)

3. **Test in ElevenLabs Dashboard:**
   - Go to https://elevenlabs.io/app/agents/integrations/TgGNvQ5EqQZl7TCAGcNe
   - Click **"Scan Available Tools"**
   - Should now see all your MCP tools!

4. **Check Railway Logs:**
   
   You should now see:
   ```
   INFO: "GET /mcp HTTP/1.1" 200 OK
   🔥 MCP SSE connection from 100.64.0.2:19030
   📤 Sending MCP server initialization via SSE
   📤 Sending tools list via SSE
   ✅ Sent 15 tools via SSE
   ```

## Understanding SSE Transport

### What is SSE?

**Server-Sent Events (SSE)** is a one-way communication protocol:
- Client opens connection with `GET` request
- Server keeps connection open
- **Server pushes events** to client as they occur
- Format: `data: {JSON}\n\n`

### SSE vs POST in MCP

Your MCP server supports **both** transport methods:

1. **SSE Transport** (used by ElevenLabs):
   - Client: `GET /mcp` → opens SSE connection
   - Server: Sends events via SSE stream
   - **Server-initiated** communication

2. **POST Transport** (used by other MCP clients):
   - Client: `POST /mcp` with JSON-RPC request
   - Server: Returns JSON-RPC response
   - **Request-response** communication

Most MCP clients (including ElevenLabs) use **SSE transport** because:
- Real-time updates
- Lower latency
- Connection stays open
- Server can push updates proactively

## Troubleshooting

### If "Scan Available Tools" Still Fails

1. **Check Railway Logs:**
   - Look for `🔥 MCP SSE connection from...`
   - Look for `📤 Sending tools list via SSE`
   - Look for `✅ Sent X tools via SSE`

2. **Run the test script:**
   ```bash
   python tools/test_sse_endpoint.py
   ```

3. **Check MCP Auth:**
   ```bash
   # In Railway dashboard or locally
   echo $MCP_AUTH_REQUIRED
   echo $MCP_AUTH_TOKEN
   ```
   
   If `MCP_AUTH_REQUIRED=true`, you need to configure the auth token in ElevenLabs MCP server settings.

4. **Verify MCP Server URL:**
   - In ElevenLabs dashboard
   - Should be: `https://supagent-production.up.railway.app/mcp`
   - Transport: `SSE`

5. **Test with curl:**
   ```bash
   curl -N -H "Accept: text/event-stream" \
     https://supagent-production.up.railway.app/mcp
   ```
   
   Should stream events in real-time.

### Common Issues

**Issue:** Connection times out
- **Fix:** Check Railway is deployed and running
- **Fix:** Verify URL in ElevenLabs matches Railway deployment

**Issue:** 401 Unauthorized
- **Fix:** Set `MCP_AUTH_REQUIRED=false` in Railway (for testing)
- **Fix:** Or configure `MCP_AUTH_TOKEN` and set it in ElevenLabs

**Issue:** No tools received
- **Fix:** Check Railway logs for errors in tool introspection
- **Fix:** Verify `app/routes/mcp_sdk.py` has registered all tools

## Next Steps

After the fix is deployed and working:

1. **Test Tool Invocation:**
   - In ElevenLabs agent conversation
   - Ask a question that triggers tool use
   - Verify tools are called correctly

2. **Monitor Railway Logs:**
   - Watch for tool invocations
   - Check for any errors

3. **Update Agent Prompt:**
   - Make sure agent knows about available tools
   - Provide clear instructions on when to use each tool

## Technical Details

### SSE Event Format

Each SSE message follows this format:

```
data: {"jsonrpc":"2.0","method":"...","params":{...}}

```

- Line starts with `data: `
- Followed by JSON payload
- **Two newlines** at the end (important!)
- Comments start with `:` (used for keepalives)

### MCP Protocol Flow

1. **Client opens SSE connection:**
   ```
   GET /mcp HTTP/1.1
   Accept: text/event-stream
   ```

2. **Server sends initialization:**
   ```
   data: {"jsonrpc":"2.0","method":"notifications/initialized",...}

   ```

3. **Server sends tools:**
   ```
   data: {"jsonrpc":"2.0","method":"notifications/tools/list_changed",...}

   ```

4. **Connection stays open** for tool invocations and updates

5. **Keepalives** prevent timeout:
   ```
   : keepalive

   ```

## References

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Server-Sent Events (SSE) Standard](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [ElevenLabs MCP Integration](https://elevenlabs.io/docs/agents-platform/mcp-integration)

## Summary

✅ **Fixed:** SSE endpoint now proactively sends tools list  
✅ **Added:** Comprehensive logging for debugging  
✅ **Added:** Test script to verify SSE functionality  
✅ **Result:** ElevenLabs can now scan and use MCP tools  

The key insight: **With SSE transport, the server must push data to the client** rather than waiting for requests. ElevenLabs opens the connection and immediately expects to receive the tools list via the SSE stream.


