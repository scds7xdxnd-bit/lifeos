# LifeOS Deployment & Operations Guide

**Last Updated:** 2024-12-18  
**Architecture Version:** 1.0  
**Deployment Status:** Production Ready

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Deployment Architecture](#deployment-architecture)
3. [Local Development](#local-development)
4. [Production Deployment](#production-deployment)
5. [Monitoring & Observability](#monitoring--observability)
6. [Troubleshooting](#troubleshooting)
7. [Operations Runbooks](#operations-runbooks)
8. [Security Best Practices](#security-best-practices)

---

## Quick Start

### Prerequisites

- Docker & Docker Compose 2.0+
- GNU Make (optional but recommended)
- Linux/macOS (Windows via WSL2)
- 4+ CPU cores, 8GB+ RAM

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd finance_app_clean

# Create .env file from template
cp .env.example .env

# Start entire stack (web, db, redis, worker)
docker-compose up -d

# Verify services are running
docker-compose ps

# Check application health
curl http://localhost:8000/health

# View logs
docker-compose logs -f lifeos-web
```

### Quick Monitoring Check

```bash
# Access Grafana dashboard
# URL: http://localhost:3000
# Default: admin/grafana

# View Prometheus metrics
# URL: http://localhost:9090

# Check alerts
# URL: http://localhost:9093
```

---

## Deployment Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Load Balancer / Reverse Proxy (nginx/Traefik)             │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴──────────────┐
        │                           │
    ┌───▼────┐              ┌──────▼────┐
    │ Web    │              │ Web       │
    │ (8000) │              │ (8000)    │
    └───┬────┘              └──────┬────┘
        │                           │
        └────────────┬──────────────┘
                     │
        ┌────────────┴──────────────────────┐
        │                                   │
    ┌───▼────┐    ┌──────────┐    ┌────────▼──┐
    │PostgreSQL   │  Redis    │    │ Worker    │
    │(5432)       │  (6379)   │    │ (async)   │
    └────────────┘ └──────────┘    └───────────┘
        │                                │
        └────────────┬──────────────────┘
                     │
        ┌────────────▼──────────────┐
        │  Monitoring Stack         │
        │  • Prometheus (9090)      │
        │  • Grafana (3000)         │
        │  • AlertManager (9093)    │
        │  • cAdvisor (8080)        │
        └───────────────────────────┘
```

### Service Architecture

| Service | Port | Purpose | Scaling |
|---------|------|---------|---------|
| lifeos-web | 8000 | Flask WSGI application | Horizontal (CPU-bound) |
| lifeos-db | 5432 | PostgreSQL database | Vertical (primary-replica) |
| lifeos-redis | 6379 | Cache & sessions | Vertical w/ replication |
| lifeos-worker | N/A | Async event processor | Horizontal (queue-based) |
| prometheus | 9090 | Metrics collection | Vertical |
| grafana | 3000 | Dashboards & alerts | Vertical |
| alertmanager | 9093 | Alert routing | Vertical w/ clustering |

---

## Local Development

### Setup Environment

```bash
# Create .env file
cat > .env << 'EOF'
APP_ENV=development
SECRET_KEY=dev-secret-key-change-in-prod
JWT_SECRET_KEY=jwt-dev-secret-key
DATABASE_URL=postgresql://lifeos:lifeos@db:5432/lifeos
REDIS_URL=redis://redis:6379/0
ENABLE_ML=true
ENABLE_INSIGHTS=true
RUN_MIGRATIONS=true
GUNICORN_WORKERS=2
GUNICORN_THREADS=2
GUNICORN_LOGLEVEL=debug
WORKER_LOGLEVEL=DEBUG
EOF
```

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Start with monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# View live logs
docker-compose logs -f lifeos-web

# Tail specific service
docker-compose logs -f lifeos-worker --tail=50

# Stop all services
docker-compose down

# Clean up volumes (careful!)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Execute command in container
docker-compose exec lifeos-web flask db upgrade
docker-compose exec lifeos-web flask shell
```

### Database Management

```bash
# Run migrations
docker-compose exec lifeos-web flask db upgrade

# Create new migration (after model changes)
docker-compose exec lifeos-web flask db migrate -m "description"

# Downgrade migration
docker-compose exec lifeos-web flask db downgrade

# Check migration status
docker-compose exec lifeos-db psql -U lifeos lifeos -c \
  "SELECT * FROM alembic_version;"
```

### Testing

```bash
# Run all tests
docker-compose exec lifeos-web pytest lifeos/tests -v

# Run specific test file
docker-compose exec lifeos-web pytest lifeos/tests/test_auth.py -v

# Run tests with coverage
docker-compose exec lifeos-web \
  pytest lifeos/tests --cov=lifeos --cov-report=html

# Watch mode (requires pytest-watch)
pytest-watch lifeos/tests
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing (GitHub Actions)
- [ ] Code reviewed and approved
- [ ] Security scan passed (bandit, safety)
- [ ] Database backup taken
- [ ] Load balancer configured
- [ ] SSL certificates valid
- [ ] Secrets loaded in secret manager
- [ ] Monitoring alerting configured
- [ ] Rollback plan documented

### Environment Configuration

**Production `.env` template:**

```bash
# Application
APP_ENV=production
DEBUG=false

# Security
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)
SESSION_COOKIE_SECURE=true
JWT_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Lax

# Database
DATABASE_URL=postgresql://lifeos:PASSWORD@db.internal:5432/lifeos
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Cache
REDIS_URL=redis://redis.internal:6379/0

# Performance
GUNICORN_WORKERS=8
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=60
GUNICORN_MAX_REQUESTS=10000

# Monitoring
STATSD_HOST=statsd-exporter
STATSD_PREFIX=lifeos.prod
ENABLE_INSIGHTS=true
ENABLE_ML=true

# Worker
WORKER_BATCH_SIZE=50
WORKER_POLL_INTERVAL=5
WORKER_MAX_ATTEMPTS=5
OUTBOX_BACKOFF_MULTIPLIER=2

# Logging
GUNICORN_LOGLEVEL=info
WORKER_LOGLEVEL=INFO

# Alerts
GRAFANA_PASSWORD=$(openssl rand -base64 32)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
PAGERDUTY_SERVICE_KEY=...
```

### Deployment Methods

#### 1. Using Deployment Script

```bash
# Make script executable
chmod +x deploy/scripts/deploy.sh

# Deploy to production
./deploy/scripts/deploy.sh deploy production

# Check deployment status
./deploy/scripts/deploy.sh status

# View logs
./deploy/scripts/deploy.sh logs

# Rollback if needed
./deploy/scripts/deploy.sh rollback /path/to/backup
```

#### 2. Manual Docker Compose Deployment

```bash
# Pull latest images
docker-compose pull

# Backup current state
docker-compose exec db pg_dump -U lifeos lifeos | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Stop old containers gracefully
docker-compose down

# Start new services
docker-compose up -d

# Verify services
docker-compose exec db pg_isready
docker-compose exec redis redis-cli ping
curl http://localhost:8000/health
```

#### 3. Using CI/CD Pipeline (GitHub Actions)

```bash
# Push to main branch triggers automatic deployment
git tag v1.0.0
git push origin v1.0.0

# CI pipeline will:
# 1. Run tests
# 2. Build Docker image
# 3. Push to registry
# 4. Deploy to production (if manually approved)
```

### Health Check Verification

```bash
# After deployment, verify all services
docker-compose ps

# Should show all services as 'Up'
# Expected output:
# CONTAINER ID  IMAGE              STATUS
# xxxxx         postgres:16        Up (healthy)
# xxxxx         redis:7            Up (healthy)
# xxxxx         lifeos-web:latest  Up (healthy)
# xxxxx         lifeos-worker      Up
```

---

## Monitoring & Observability

### Accessing Dashboards

| Dashboard | URL | Access |
|-----------|-----|--------|
| Grafana | http://localhost:3000 | admin/grafana |
| Prometheus | http://localhost:9090 | No auth |
| AlertManager | http://localhost:9093 | No auth |

### Key Metrics to Monitor

#### Application Metrics
- **Request Rate**: `rate(http_requests_total[5m])` 
- **Error Rate**: `rate(http_requests_total{status=~"5.."}[5m])`
- **Response Time (p95)**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Worker Lag**: `platform_outbox_pending_messages`

#### Infrastructure Metrics
- **CPU Usage**: `rate(container_cpu_usage_seconds_total[5m]) * 100`
- **Memory Usage**: `(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100`
- **Disk Space**: `(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100`
- **Database Connections**: `pg_stat_activity_count`

### Alerts

See `prometheus.rules.yml` for alert definitions:
- Critical: Web app down, database down, Redis down
- Warning: High error rate, slow queries, memory pressure
- Info: Outbox backlog, connection limits

---

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
docker-compose logs lifeos-web
# Check: port conflicts, out of memory, network issues
docker system prune -a
docker-compose down -v
docker-compose up -d
```

#### Database Connection Failures
```bash
docker-compose exec db pg_isready -U lifeos
# If not ready, check db logs
docker-compose logs db
```

#### Worker Not Processing
```bash
docker-compose logs lifeos-worker
# Check outbox queue
docker-compose exec db psql -U lifeos lifeos -c \
  "SELECT status, COUNT(*) FROM platform_outbox GROUP BY status;"
```

---

## Operations Runbooks

### Deploy New Release

**Time:** 15-30 min | **Risk:** Medium | **Rollback:** 5-10 min

```bash
./deploy/scripts/deploy.sh deploy production
docker-compose ps
curl http://localhost:8000/health
```

### Emergency Restart

**Time:** 2 min | **Risk:** Low

```bash
docker-compose restart
# If graceful doesn't work
docker-compose down && docker-compose up -d
```

### Database Backup

```bash
docker-compose exec db pg_dump -U lifeos lifeos | gzip > backup.sql.gz
```

### Database Recovery

```bash
docker-compose stop lifeos-web lifeos-worker
gunzip < backup.sql.gz | docker-compose exec -T db psql -U lifeos lifeos
docker-compose start lifeos-web lifeos-worker
```

---

## Security Best Practices

- Rotate secrets every 90 days
- Use strong passwords (32+ chars)
- Enable SSL/TLS (terminate at reverse proxy)
- Restrict database access to application subnet
- Enable audit logging for compliance
- Use rate limiting for API endpoints
- Keep dependencies updated (renovate bot)

---

## Support

- **Slack:** #lifeos-incidents
- **Email:** ops@example.com
- **PagerDuty:** See on-call rotation
- **Documentation:** See `lifeos/docs/lifeos_architecture.md`
