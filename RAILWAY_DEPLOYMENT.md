# Deploying to Railway

Railway provides a public URL that the ElevenLabs Agent can access. This guide walks you through deploying your SupaGent API to Railway.

## Quick Deploy

### 1. Create Railway Project

1. Go to [Railway](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo" (or use Railway CLI)
3. Select your SupaGent repository

### 2. Configure Environment Variables

In Railway's dashboard, add these environment variables:

**Required:**
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key
- `ELEVENLABS_AGENT_ID` - Your agent ID (will be auto-created if not set)

**Optional:**
- `SUPAGENT_BASE_URL` - Leave empty to auto-detect Railway's public URL
- `CHROMA_PERSIST_DIR` - Default: `/app/data/chroma` (persistent volume)
- `EMBEDDING_MODEL` - Default: `sentence-transformers/all-MiniLM-L6-v2`
- `VECTOR_BACKEND` - `CHROMA` (default) or `FAISS`

### 3. Railway Auto-Detection

The app automatically detects Railway's public URL via the `RAILWAY_PUBLIC_DOMAIN` environment variable (set automatically by Railway). You don't need to set `SUPAGENT_BASE_URL` manually.

### 4. Deploy

Railway will:
1. Detect your Python project
2. Install dependencies from `requirements.txt`
3. Run the app (Railway auto-detects FastAPI/uvicorn)

**Start Command (if needed):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Railway sets the `PORT` environment variable automatically.

## Post-Deployment Steps

### 1. Get Your Public URL

After deployment, Railway provides a public URL like:
- `https://your-app-name.up.railway.app`

### 2. Configure MCP Server

The app will automatically:
- Detect the Railway public URL
- Create/register the MCP server with ElevenLabs
- Configure it to point to `https://your-app-name.up.railway.app/mcp`

**Manual Configuration (if needed):**
1. Visit `https://your-app-name.up.railway.app/config/eleven`
2. Check `mcp_server.status` - should be "configured"
3. If not, call `POST /config/eleven/configure_mcp`

### 3. Verify Connectivity

Test that everything works:

```bash
# Test vector store
curl https://your-app-name.up.railway.app/test/vector_store?query=password

# Test full chain
curl https://your-app-name.up.railway.app/test/full_chain?query=How+do+I+reset+my+password

# Check config
curl https://your-app-name.up.railway.app/config/eleven
```

## Persistent Storage

### Vector Store Data

Railway provides persistent volumes. Your vector store data will be stored at:
- `/app/data/chroma` (default)

This persists across deployments.

### Ingesting Documents

You can ingest documents in two ways:

**Option 1: Local ingestion, then deploy**
```bash
# Ingest locally
python -m tools.ingest --dir dataset

# Commit and push (data is in ./data/chroma)
git add data/chroma
git commit -m "Add vector store data"
git push
```

**Option 2: Ingest on Railway (using Railway CLI or one-off container)**
```bash
railway run python -m tools.ingest --dir dataset
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ELEVENLABS_API_KEY` | Yes | - | Your ElevenLabs API key |
| `ELEVENLABS_AGENT_ID` | No | - | Auto-created if not set |
| `SUPAGENT_BASE_URL` | No | Auto-detected | Public URL (Railway auto-sets) |
| `CHROMA_PERSIST_DIR` | No | `/app/data/chroma` | Vector store directory |
| `EMBEDDING_MODEL` | No | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `VECTOR_BACKEND` | No | `CHROMA` | `CHROMA` or `FAISS` |
| `SESSIONS_DIR` | No | `/app/data/sessions` | Session storage |

## Troubleshooting

### MCP Server Not Accessible

1. **Check Railway URL:**
   ```bash
   curl https://your-app-name.up.railway.app/config/eleven
   ```
   Verify `mcp_server.endpoint` shows the Railway URL (not localhost)

2. **Verify Public Access:**
   ```bash
   curl https://your-app-name.up.railway.app/mcp
   ```
   Should return MCP protocol response (may be an error, but should be reachable)

3. **Check Logs:**
   - Railway dashboard → Your service → Logs
   - Look for MCP server creation errors

### Vector Store Empty

If your vector store is empty after deployment:

1. **Check if data directory exists:**
   ```bash
   railway run ls -la /app/data/chroma
   ```

2. **Re-ingest documents:**
   ```bash
   railway run python -m tools.ingest --dir dataset
   ```

### Port Issues

Railway automatically sets the `PORT` environment variable. Make sure your app listens on:
- Host: `0.0.0.0` (all interfaces)
- Port: `$PORT` (Railway's assigned port)

The default uvicorn command handles this automatically.

## Custom Domain (Optional)

Railway supports custom domains:

1. Railway dashboard → Your service → Settings → Domains
2. Add your custom domain
3. Update `SUPAGENT_BASE_URL` to your custom domain
4. Re-configure MCP server: `POST /config/eleven/configure_mcp`

## Cost Considerations

- Railway has a free tier with usage limits
- Vector store data counts toward storage limits
- Consider using Railway's volume mounts for persistent data
- Monitor usage in Railway dashboard

## Next Steps

After successful deployment:

1. ✅ Verify MCP server is configured: `/config/eleven`
2. ✅ Test vector store connectivity: `/test/vector_store`
3. ✅ Test with your ElevenLabs Agent using prompts from `TEST_PROMPTS.md`
4. ✅ Monitor logs for any tool call errors

Your ElevenLabs Agent should now be able to access your MCP server and vector store!

