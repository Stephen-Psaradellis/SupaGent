# Doppler Secrets Management

This project uses [Doppler](https://www.doppler.com/) for managing secrets (API keys). All other configuration is stored in `.env` file.

## Setup

### 1. Install Doppler CLI

```bash
# macOS
brew install dopplerhq/cli/doppler

# Linux
curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sh

# Windows (PowerShell)
powershell -Command "& {Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://cli.doppler.com/install.ps1'))}"
```

### 2. Authenticate with Doppler

```bash
doppler login
```

### 3. Link Your Project

```bash
doppler setup
```

This will prompt you to:
- Select your workspace
- Select your project
- Select your config (e.g., `dev`, `staging`, `prod`)

### 4. Set Secrets

```bash
# Set ElevenLabs API key
doppler secrets set ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Set OpenAI API key (for domain generation)
doppler secrets set OPENAI_API_KEY=your_openai_api_key
```

### 5. Run with Doppler

```bash
# Run the application with Doppler secrets injected
doppler run -- python -m uvicorn app.main:app --reload

# Or run any command with Doppler
doppler run -- python -m tools.switch_domain mcdonalds
```

## Local Development

Doppler works locally just like in production. Simply run commands with `doppler run`:

```bash
# Run the app locally with Doppler
doppler run -- python -m uvicorn app.main:app --reload

# Run any tool with Doppler
doppler run -- python -m tools.switch_domain mcdonalds
```

**Note:** All secrets must be configured in Doppler. There is no fallback to `.env` files for secrets.

## Secrets vs Configuration

### Secrets (Doppler)
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `OPENAI_API_KEY` - OpenAI API key

### Configuration (.env file)
- `ELEVENLABS_AGENT_ID` - ElevenLabs agent ID
- `ELEVENLABS_VOICE_ID` - Optional voice ID
- `DOMAIN_ID` - Domain configuration ID
- `CHROMA_PERSIST_DIR` - Vector store directory
- `EMBEDDING_MODEL` - Embedding model name
- All other non-secret configuration

## Production Deployment

The Dockerfile already includes Doppler CLI installation. In production environments, you need to provide a Doppler service token:

### Railway

1. **Create a Doppler Service Token:**
   ```bash
   doppler service-tokens create <token-name> --project <project> --config <config>
   ```

2. **Set the token in Railway:**
   - Railway Dashboard → Your Service → Variables
   - Add: `DOPPLER_TOKEN` = `<your-service-token>`

3. **Deploy:** The Dockerfile will automatically use `doppler run` to inject secrets

### Docker / Docker Compose

```bash
# Set Doppler service token
export DOPPLER_TOKEN=your_service_token

# Build and run
docker build -t supagent .
docker run -e DOPPLER_TOKEN=$DOPPLER_TOKEN supagent
```

### Kubernetes

Use Doppler Kubernetes operator or set `DOPPLER_TOKEN` as a secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: doppler-token
type: Opaque
stringData:
  DOPPLER_TOKEN: your_service_token
```

Then reference it in your deployment.

## Troubleshooting

### "ELEVENLABS_API_KEY not set in Doppler"

1. Check if Doppler is installed: `doppler --version`
2. Check if you're authenticated: `doppler me`
3. Check if project is linked: `doppler configure get`
4. Verify secret exists: `doppler secrets get ELEVENLABS_API_KEY`

### Running in CI/CD

For CI/CD environments, you can use Doppler's service tokens:

```bash
# Set service token as environment variable
export DOPPLER_TOKEN=your_service_token

# Run commands normally (Doppler will use the token)
python -m uvicorn app.main:app
```

Alternatively, use Doppler's download command to export secrets:

```bash
# Export secrets as environment variables
eval $(doppler secrets download --no-file --format env)

# Run your application
python -m uvicorn app.main:app
```

