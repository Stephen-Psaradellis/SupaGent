# SupaGent Deployment Guide

## Database Integration

SupaGent now supports PostgreSQL storage for business intelligence data. The system automatically handles database setup during deployment.

### Environment Variables

Set these in your Railway environment:

```bash
DATABASE_URL=postgresql://postgres:[password]@postgres.railway.internal:5432/railway
```

### Automatic Deployment Process

The deployment process automatically:

1. **Checks Database Configuration**: Only runs database setup if `DATABASE_URL` is configured
2. **Database Health Check**: Verifies PostgreSQL connection
3. **Table Creation**: Creates tables if they don't exist
4. **Data Migration**: Migrates existing file-based data to PostgreSQL
5. **Application Startup**: Starts the FastAPI application

### Deployment Flow

```
Docker Build → Entrypoint Script → Database Setup → Verification → App Start
```

### Manual Commands (if needed)

If you need to run setup manually:

```bash
# Check database status
python scripts/verify_database.py

# Run setup (only if needed)
python scripts/setup_database.py

# Migrate data manually
python tools/migrate_business_data.py
```

### Database Behavior

- **First Deployment**: Creates tables and migrates existing data
- **Subsequent Deployments**: Checks if setup is needed, skips if already complete
- **No DATABASE_URL**: Uses file storage (backward compatible)
- **Database Issues**: Falls back to file storage gracefully

### Data Migration

The system migrates:
- Business domains
- Scraped website content (about, services, team, blog, general)
- Intelligence bundles with Hunter.io enrichment
- All metadata and timestamps

### Monitoring

Check logs for these indicators:
- `✅ Database is ready!` - Setup complete
- `✅ No migration needed - database is up to date` - Already configured
- `⏭️ No DATABASE_URL configured, using file storage` - File mode

### Troubleshooting

**Database Connection Issues:**
```bash
# Test connection
python -c "from core.database import health_check; print('DB Health:', health_check())"
```

**Check Database Content:**
```bash
# Count records
python scripts/verify_database.py
```

**Force Migration:**
```bash
# Reset and migrate
python scripts/setup_database.py
```

### Performance Benefits

- **Scalability**: Handle thousands of domains efficiently
- **Query Speed**: Indexed database lookups vs file scans
- **Concurrency**: Multiple processes can safely access data
- **Backup**: Railway-managed PostgreSQL backups
- **Analytics**: SQL queries for business intelligence insights
