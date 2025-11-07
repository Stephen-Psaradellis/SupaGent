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
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

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
CMD ["doppler", "run", "--project", "shortforge", "--config", "dev", "--", "uvicorn", "app.main:app"]

