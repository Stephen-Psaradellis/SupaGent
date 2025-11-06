# Railway Deployment Checklist

Use this checklist to ensure your SupaGent app is ready for Railway deployment.

## Pre-Deployment

### ✅ Code Readiness

- [x] `Procfile` created with Railway-compatible start command
- [x] `runtime.txt` specifies Python version
- [x] `railway.json` configured (optional, Railway auto-detects)
- [x] `requirements.txt` includes all dependencies
- [x] Vector store defaults to Railway paths (`/app/data/chroma`)
- [x] App auto-detects Railway environment variables
- [x] MCP server auto-configures with Railway public URL

### ✅ Environment Variables

Set these in Railway dashboard:

**Required:**
- [ ] `ELEVENLABS_API_KEY` - Your ElevenLabs API key

**Optional (Auto-configured):**
- [ ] `ELEVENLABS_AGENT_ID` - Will be auto-created if not set
- [ ] `SUPAGENT_BASE_URL` - Auto-detected from Railway
- [ ] `CHROMA_PERSIST_DIR` - Defaults to `/app/data/chroma` on Railway
- [ ] `SESSIONS_DIR` - Defaults to `/app/data/sessions` on Railway

### ✅ Vector Store Setup

**Option 1: Railway Persistent Volume (Recommended)**
- [ ] Create volume in Railway dashboard
- [ ] Mount to `/app/data/chroma`
- [ ] Set `CHROMA_PERSIST_DIR=/app/data/chroma` (or use default)

**Option 2: Ingest After Deployment**
- [ ] Deploy app first
- [ ] Run: `railway run python -m tools.ingest --dir dataset`

## Deployment Steps

### 1. Deploy to Railway

1. [ ] Connect GitHub repo to Railway
2. [ ] Railway auto-detects Python project
3. [ ] Railway installs dependencies from `requirements.txt`
4. [ ] Railway runs `Procfile` start command
5. [ ] App starts on Railway's assigned port

### 2. Configure Persistent Storage

1. [ ] Go to Railway dashboard → Your service → Volumes
2. [ ] Create volume named `chroma-data`
3. [ ] Mount to `/app/data/chroma`
4. [ ] (Optional) Create volume for sessions: `/app/data/sessions`

### 3. Set Environment Variables

1. [ ] Add `ELEVENLABS_API_KEY` in Railway dashboard
2. [ ] (Optional) Add `CHROMA_PERSIST_DIR=/app/data/chroma` if using custom path
3. [ ] Railway automatically sets `RAILWAY_PUBLIC_DOMAIN` and `PORT`

### 4. Ingest Documents

After first deployment:

```bash
railway run python -m tools.ingest --dir dataset
```

Or if you have dataset files in your repo, they'll be available at `/app/dataset`.

## Post-Deployment Verification

### ✅ Health Checks

1. [ ] **Check App Status:**
   ```bash
   curl https://your-app.up.railway.app/admin/status
   ```
   Should return:
   - `persist_dir`: `/app/data/chroma`
   - `environment`: `production` (or Railway environment name)
   - `has_data`: `true` (after ingesting)

2. [ ] **Check MCP Configuration:**
   ```bash
   curl https://your-app.up.railway.app/config/eleven
   ```
   Should show:
   - `mcp_server.status`: `"configured"`
   - `mcp_server.endpoint`: Railway URL (not localhost)

3. [ ] **Test Vector Store:**
   ```bash
   curl https://your-app.up.railway.app/test/vector_store?query=password
   ```
   Should return results if data is ingested

4. [ ] **Test Full Chain:**
   ```bash
   curl https://your-app.up.railway.app/test/full_chain?query=How+do+I+reset+my+password
   ```
   All tests should pass

### ✅ MCP Server Verification

1. [ ] **Check MCP Endpoint:**
   ```bash
   curl -X POST https://your-app.up.railway.app/mcp \
     -H "Content-Type: application/json" \
     -d '{"method": "tools/list"}'
   ```
   Should return tool definitions

2. [ ] **Verify in ElevenLabs Dashboard:**
   - Go to ElevenLabs dashboard
   - Check your agent's MCP server configuration
   - Verify it points to your Railway URL

## Troubleshooting

### App Won't Start

- [ ] Check Railway logs for errors
- [ ] Verify `Procfile` has correct command
- [ ] Ensure Python version in `runtime.txt` is supported
- [ ] Check that all dependencies install correctly

### Vector Store Empty

- [ ] Verify volume is mounted correctly
- [ ] Check volume has write permissions
- [ ] Run ingestion: `railway run python -m tools.ingest --dir dataset`
- [ ] Verify data exists: `railway run ls -la /app/data/chroma`

### MCP Server Not Accessible

- [ ] Verify Railway URL is public (not localhost)
- [ ] Check `/config/eleven` endpoint shows Railway URL
- [ ] Manually trigger MCP config: `POST /config/eleven/configure_mcp`
- [ ] Check Railway logs for MCP creation errors

### Port Issues

- [ ] Railway sets `$PORT` automatically
- [ ] Ensure Procfile uses `$PORT` not hardcoded port
- [ ] App should listen on `0.0.0.0` (all interfaces)

## File Structure

Your repo should have:
```
.
├── Procfile                    # Railway start command
├── runtime.txt                 # Python version
├── railway.json                # Railway config (optional)
├── requirements.txt            # Python dependencies
├── app/
│   └── main.py                 # FastAPI app
├── memory/
│   └── vector_store.py         # Vector store implementation
├── agents/
│   └── ...                     # Agent implementations
└── dataset/                    # Your documents (optional)
```

## Quick Deploy Command

If using Railway CLI:

```bash
railway login
railway init
railway up
```

Then set environment variables in Railway dashboard.

## Success Criteria

✅ App is accessible at Railway public URL  
✅ `/admin/status` shows correct paths and environment  
✅ `/test/vector_store` returns results  
✅ `/config/eleven` shows MCP server configured with Railway URL  
✅ ElevenLabs Agent can call MCP tool successfully  

## Next Steps

After successful deployment:
1. Test with your ElevenLabs Agent using prompts from `TEST_PROMPTS.md`
2. Monitor Railway logs for any errors
3. Set up monitoring/alerting if needed
4. Consider custom domain for production

