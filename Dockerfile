# syntax=docker/dockerfile:1.5

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

ARG DOPPLER_TOKEN

RUN --mount=type=cache,id=cacheKey=apt-cache,target=/var/cache/apt \
    --mount=type=cache,id=cacheKey=apt-lists,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        cmake \
        pkg-config \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies with cacheable pip wheel cache
COPY requirements.txt .
RUN --mount=type=cache,id=cacheKey=pip-cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --user -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:/usr/local/bin:$PATH \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0 \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright \
    BROWSER_USE_HEADLESS=1 \
    BROWSER_USE_DISABLE_SECURITY=1

RUN --mount=type=cache,id=cacheKey=apt-cache2,target=/var/cache/apt \
    --mount=type=cache,id=cacheKey=apt-lists2,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        libnss3-dev \
        libatk-bridge2.0-dev \
        libdrm2 \
        libxkbcommon-dev \
        libxcomposite-dev \
        libxdamage-dev \
        libxrandr-dev \
        libgbm-dev \
        libxss1 \
        libasound2-dev \
        libgtk-3-dev && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" \
        https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key \
        | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" \
        | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends doppler && \
    rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Install Playwright browsers (depends on runtime libs already installed)
RUN --mount=type=cache,id=cacheKey=playwright-cache,target=/root/.cache/ms-playwright \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright \
    playwright install --with-deps

WORKDIR /app

# Copy source code after installing deps to leverage layer caching
COPY . .

# Make entrypoint script executable & create data directories
RUN chmod +x scripts/entrypoint.sh && \
    mkdir -p /app/data/chroma /app/data/sessions

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["doppler", "run", "--project", "shortforge", "--config", "dev", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]