# Optimized Dockerfile for Railway
# Uses multi-stage build and better caching

FROM python:3.10-slim as builder

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
FROM python:3.10-slim

# Install Doppler CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh -o /tmp/doppler-install.sh \
    && chmod +x /tmp/doppler-install.sh \
    && /tmp/doppler-install.sh --yes \
    && rm -f /tmp/doppler-install.sh \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to use local packages and Doppler
ENV PATH=/root/.local/bin:/usr/local/bin:$PATH

WORKDIR /app

# Copy application code (this changes frequently, so it's last)
COPY . .

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/sessions

# Expose port (Railway sets PORT env var)
EXPOSE $PORT

# Run the application with Doppler
# Note: DOPPLER_TOKEN should be set as an environment variable in your deployment platform
CMD doppler run -- uvicorn app.main:app

