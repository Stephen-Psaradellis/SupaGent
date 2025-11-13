#!/bin/bash

# SupaGent Deployment Entrypoint Script
# This script handles database setup and then starts the application

set -e  # Exit on any error

echo "🚀 Starting SupaGent deployment..."

# Change to the application directory
# In Docker this is /app, locally it might be different
if [ -d "/app" ]; then
    cd /app
elif [ -f "scripts/setup_database.py" ]; then
    # We're already in the project root
    :
else
    echo "❌ Cannot find application directory"
    exit 1
fi

# Run database setup if DATABASE_URL is configured
if [ -n "$DATABASE_URL" ]; then
    echo "📊 DATABASE_URL detected, checking database setup..."
    python scripts/setup_database.py
else
    echo "⏭️  No DATABASE_URL configured, using file storage"
fi

# Verify the database setup if configured
if [ -n "$DATABASE_URL" ]; then
    echo "🔍 Verifying database setup..."
    python scripts/verify_database.py
fi

echo "✅ Pre-deployment checks complete"

# Execute the main command (passed as arguments to this script)
echo "🏁 Starting application..."
exec "$@"
