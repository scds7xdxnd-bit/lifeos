#!/bin/bash
# LifeOS Production Deployment Script
# Usage: ./deploy.sh [action] [environment]
# Actions: deploy, rollback, health-check, logs, status
# Environments: production, staging

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_ROOT}/.env"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
COMPOSE_MONITORING="${PROJECT_ROOT}/docker-compose.monitoring.yml"

# Default values
ACTION="${1:-deploy}"
ENVIRONMENT="${2:-production}"
APP_VERSION="${APP_VERSION:-latest}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
LOG_DIR="${LOG_DIR:-${PROJECT_ROOT}/logs}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/deploy.log"
}

# Create necessary directories
setup_directories() {
    mkdir -p "$BACKUP_DIR" "$LOG_DIR"
    log_info "Created backup and log directories"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "docker-compose.yml not found at $COMPOSE_FILE"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Using defaults."
    fi
    
    log_success "Prerequisites check passed"
}

# Backup current state
backup_state() {
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log_info "Creating backup: $backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup docker-compose state
    docker-compose -f "$COMPOSE_FILE" ps > "$backup_path/services.txt" 2>&1 || true
    
    # Backup database (if DB container exists)
    local db_container="lifeos-db"
    if docker ps -a --format '{{.Names}}' | grep -q "^${db_container}$"; then
        log_info "Backing up database..."
        docker exec "$db_container" pg_dump -U lifeos lifeos > "$backup_path/database.sql" 2>&1 || true
        gzip "$backup_path/database.sql"
        log_success "Database backup created"
    fi
    
    log_success "Backup created at $backup_path"
    echo "$backup_path"
}

# Pre-deployment checks
pre_deploy_checks() {
    log_info "Running pre-deployment checks..."
    
    # Validate docker-compose files
    log_info "Validating docker-compose files..."
    docker-compose -f "$COMPOSE_FILE" config > /dev/null || {
        log_error "docker-compose.yml validation failed"
        exit 1
    }
    
    log_info "Checking disk space..."
    local available_space
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 1048576 ]; then  # 1GB
        log_warning "Less than 1GB free disk space available"
    fi
    
    log_success "Pre-deployment checks passed"
}

# Deploy function
deploy() {
    log_info "Starting deployment for environment: $ENVIRONMENT"
    
    # Run pre-deployment checks
    pre_deploy_checks
    
    # Backup current state
    BACKUP_PATH=$(backup_state)
    
    # Load environment
    if [ -f "$ENV_FILE" ]; then
        # shellcheck disable=SC2086
        set -a
        # shellcheck source=/dev/null
        source "$ENV_FILE"
        set +a
    fi
    
    log_info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull || {
        log_error "Failed to pull images"
        exit 1
    }
    
    log_info "Stopping old containers..."
    docker-compose -f "$COMPOSE_FILE" down || true
    
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d || {
        log_error "Failed to start services"
        log_info "Rolling back to backup: $BACKUP_PATH"
        rollback "$BACKUP_PATH"
        exit 1
    }
    
    # Wait for services to be ready
    log_info "Waiting for services to be healthy..."
    sleep 5
    
    # Run health checks
    if health_check; then
        log_success "Deployment completed successfully"
        
        # Start monitoring stack
        log_info "Starting monitoring stack..."
        docker-compose -f "$COMPOSE_MONITORING" up -d || true
        
        log_info "Deployment Summary:"
        docker-compose -f "$COMPOSE_FILE" ps
        return 0
    else
        log_error "Health checks failed"
        log_info "Rolling back to backup: $BACKUP_PATH"
        rollback "$BACKUP_PATH"
        exit 1
    fi
}

# Rollback function
rollback() {
    local backup_path="${1:-}"
    
    if [ -z "$backup_path" ]; then
        log_error "No backup path specified for rollback"
        exit 1
    fi
    
    log_warning "Rolling back deployment..."
    
    if [ -f "$backup_path/database.sql.gz" ]; then
        log_info "Restoring database from backup..."
        local db_container="lifeos-db"
        
        gunzip -c "$backup_path/database.sql.gz" | \
            docker exec -i "$db_container" psql -U lifeos -d lifeos || true
        
        log_success "Database restored"
    fi
    
    log_success "Rollback completed"
}

# Health check function
health_check() {
    log_info "Running health checks..."
    
    local max_attempts=30
    local attempt=0
    local services=("lifeos-web" "lifeos-db" "lifeos-redis" "lifeos-worker")
    
    while [ $attempt -lt $max_attempts ]; do
        local all_healthy=true
        
        for service in "${services[@]}"; do
            if ! docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
                log_warning "Service $service is not running yet (attempt $((attempt+1))/$max_attempts)"
                all_healthy=false
                break
            fi
        done
        
        if [ "$all_healthy" = true ]; then
            # Check web app endpoint
            log_info "Checking web app health endpoint..."
            if curl -fsS http://localhost:8000/health > /dev/null 2>&1; then
                log_success "Health checks passed"
                return 0
            fi
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Logs function
show_logs() {
    local service="${1:-all}"
    
    if [ "$service" == "all" ]; then
        log_info "Showing logs from all services..."
        docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
    else
        log_info "Showing logs from $service..."
        docker-compose -f "$COMPOSE_FILE" logs -f --tail=100 "$service"
    fi
}

# Status function
status() {
    log_info "LifeOS Status"
    echo "================================"
    
    log_info "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Database Status:"
    docker exec lifeos-db pg_isready -U lifeos 2>&1 || true
    
    echo ""
    log_info "Redis Status:"
    docker exec lifeos-redis redis-cli ping 2>&1 || true
    
    echo ""
    log_info "Web App Status:"
    curl -fsS http://localhost:8000/health 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "Not responding"
}

# Main logic
main() {
    setup_directories
    check_prerequisites
    
    case "$ACTION" in
        deploy)
            deploy
            ;;
        rollback)
            if [ -z "$BACKUP_DIR" ]; then
                log_error "Please specify backup directory: BACKUP_DIR=/path/to/backup $0 rollback"
                exit 1
            fi
            rollback "$BACKUP_DIR"
            ;;
        health-check)
            health_check
            ;;
        logs)
            show_logs "${3:-all}"
            ;;
        status)
            status
            ;;
        *)
            log_error "Unknown action: $ACTION"
            echo ""
            echo "Usage: $0 [action] [environment]"
            echo ""
            echo "Actions:"
            echo "  deploy         - Deploy LifeOS (default)"
            echo "  rollback       - Rollback to previous version"
            echo "  health-check   - Run health checks"
            echo "  logs           - Show service logs"
            echo "  status         - Show current status"
            echo ""
            echo "Environments: production, staging"
            echo ""
            exit 1
            ;;
    esac
}

main "$@"
