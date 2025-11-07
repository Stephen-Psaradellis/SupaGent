# Deploying to Railway

Railway provides a public URL that the ElevenLabs Agent can access. This guide walks you through deploying your SupaGent API to Railway.

## Quick Deploy

### 1. Create Railway Project

1. Go to [Railway](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo" (or use Railway CLI)
3. Select your SupaGent repository

### 2. Configure Secrets and Environment Variables

**Secrets (Doppler):**
1. Create a Doppler service token:
   ```bash
   doppler service-tokens create railway-prod --project <your-project> --config <your-config>
   ```

2. In Railway's dashboard, add this environment variable:
   - `DOPPLER_TOKEN` - Your Doppler service token

**Configuration (Railway Environment Variables):**
- `ELEVENLABS_AGENT_ID` - Your agent ID (will be auto-created if not set)

**Optional (Auto-configured on Railway):**
- `SUPAGENT_BASE_URL` - Auto-detected from `RAILWAY_PUBLIC_DOMAIN`
- `CHROMA_PERSIST_DIR` - Auto-defaults to `/app/data/chroma` on Railway
- `SESSIONS_DIR` - Auto-defaults to `/app/data/sessions` on Railway
- `EMBEDDING_MODEL` - Default: `sentence-transformers/all-MiniLM-L6-v2`
- `VECTOR_BACKEND` - `CHROMA` (default) or `FAISS`

**Note:** The app automatically detects Railway environment and adjusts paths accordingly. You only need to set these if you want custom values.

### 3. Railway Auto-Detection

The app automatically detects Railway's public URL via the `RAILWAY_PUBLIC_DOMAIN` environment variable (set automatically by Railway). You don't need to set `SUPAGENT_BASE_URL` manually.

### 4. Deploy

Railway will:
1. Detect your Python project (via `Procfile` or auto-detection)
2. Install dependencies from `requirements.txt`
3. Run the app using the `Procfile` start command

**Start Command:**
The Dockerfile automatically uses `doppler run` to inject secrets. The app will:
- Load secrets (`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`) from Doppler
- Load configuration from Railway environment variables

Railway sets the `PORT` environment variable automatically. The app will:
- Auto-detect Railway environment and use `/app/data/chroma` for vector store
- Auto-detect Railway public URL for MCP server configuration
- Create MCP server automatically on startup

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

## Vector Store Hosting Options

The vector store (Chroma or FAISS) needs persistent storage. Here are your options:

### Option 1: Railway Persistent Volumes (Recommended)

Railway provides persistent volumes that survive deployments and restarts.

**Setup:**
1. In Railway dashboard → Your service → Settings → Volumes
2. Create a new volume (e.g., `chroma-data`)
3. Mount it to `/app/data/chroma`
4. Set environment variable: `CHROMA_PERSIST_DIR=/app/data/chroma`

**Pros:**
- ✅ Simple setup
- ✅ Data persists across deployments
- ✅ No additional services needed
- ✅ Fast local access

**Cons:**
- ⚠️ Limited by Railway's volume size limits
- ⚠️ Data is tied to Railway service

**Ingesting Documents:**
```bash
# After deployment, ingest documents
railway run python -m tools.ingest --dir dataset
```

### Option 2: Railway Volume + Git (For Small Datasets)

For small vector stores (< 100MB), you can commit the data to git:

```bash
# Ingest locally
python -m tools.ingest --dir dataset

# Commit vector store data
git add data/chroma
git commit -m "Add vector store data"
git push
```

**Pros:**
- ✅ Version controlled
- ✅ Easy to deploy
- ✅ No volume setup needed

**Cons:**
- ⚠️ Only works for small datasets
- ⚠️ Increases repo size
- ⚠️ Slower deployments

### Option 3: External Cloud Storage (Advanced)

For large datasets or multi-region deployments, use cloud storage:

**Using S3-compatible storage:**
1. Store vector store files in S3/R2/etc.
2. Download on startup or use a sync mechanism
3. Modify `VectorStore` to support remote storage

**Pros:**
- ✅ Scalable
- ✅ Can share across multiple instances
- ✅ Backup-friendly

**Cons:**
- ⚠️ Requires code changes
- ⚠️ More complex setup
- ⚠️ Additional costs

### Option 4: Managed Vector Database (Future)

For production at scale, consider:
- **Chroma Cloud** (when available)
- **Pinecone**
- **Weaviate Cloud**
- **Qdrant Cloud**

These would require modifying the `VectorStore` class to use their APIs.

## Recommended Setup for Railway

**For most use cases, use Option 1 (Railway Persistent Volumes):**

1. **Create Volume:**
   - Railway dashboard → Your service → Volumes → Create Volume
   - Name: `chroma-data`
   - Mount path: `/app/data/chroma`

2. **Set Environment Variable:**
   ```
   CHROMA_PERSIST_DIR=/app/data/chroma
   ```

3. **Ingest Documents After Deployment:**
   ```bash
   railway run python -m tools.ingest --dir dataset
   ```

4. **Verify Storage:**
   ```bash
   # Check volume contents
   railway run ls -la /app/data/chroma
   
   # Test vector store
   curl https://your-app.up.railway.app/test/vector_store?query=password
   ```

## Storage Size Considerations

- **Small datasets (< 1GB):** Railway volumes work well
- **Medium datasets (1-10GB):** Railway volumes or cloud storage
- **Large datasets (> 10GB):** Consider external storage or managed vector DB

**Typical sizes:**
- 100 documents: ~10-50MB
- 1,000 documents: ~100-500MB
- 10,000 documents: ~1-5GB

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DOPPLER_TOKEN` | Yes | - | Doppler service token (for secrets) |
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

