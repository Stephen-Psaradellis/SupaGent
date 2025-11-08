# Optimized Dockerfile for Railway
# Uses multi-stage build and better caching

FROM python:3.11-slim as builder

ENV DOPPLER_TOKEN=${DOPPLER_TOKEN}

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
# This layer is cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Runtime stage - smaller image
FROM python:3.11-slim

# Install Doppler CLI and additional browser dependencies
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg \
    # Browser automation dependencies
    libnss3-dev libatk-bridge2.0-dev libdrm2 libxkbcommon-dev libxcomposite-dev libxdamage-dev \
    libxrandr-dev libgbm-dev libxss1 libasound2-dev libgtk-3-dev && \
    # Doppler CLI
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to use local packages and Doppler
ENV PATH=/root/.local/bin:/usr/local/bin:$PATH

# Environment variables for headless browser operation in containers
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
# Browser-use specific environment variables
ENV BROWSER_USE_HEADLESS=1
ENV BROWSER_USE_DISABLE_SECURITY=1

# Install Playwright browsers for browser automation
# --with-deps installs system dependencies required for browsers
RUN playwright install --with-deps

WORKDIR /app

# Copy application code (this changes frequently, so it's last)
COPY . .

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/sessions

# Note: EXPOSE is not needed - Railway handles port binding automatically via PORT env var

# Run the application with Doppler
# Note: DOPPLER_TOKEN should be set as an environment variable in your deployment platform
CMD ["doppler", "run", "--project", "shortforge", "--config", "dev", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]