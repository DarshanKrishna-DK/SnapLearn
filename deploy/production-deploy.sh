#!/bin/bash

# SnapLearn AI - Production Deployment Script
# Phase 5 - Automated production deployment with health checks

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
ENV_FILE="$PROJECT_ROOT/.env.prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    command -v docker >/dev/null 2>&1 || error "Docker is not installed"
    command -v docker-compose >/dev/null 2>&1 || error "Docker Compose is not installed"
    
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file not found: $ENV_FILE"
    fi
    
    # Check if running as root (not recommended for production)
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. Consider using a dedicated user for production deployments."
    fi
    
    success "Prerequisites check passed"
}

# Validate environment variables
validate_environment() {
    log "Validating environment variables..."
    
    # Required variables
    required_vars=(
        "GEMINI_API_KEY"
        "JWT_SECRET_KEY" 
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "DATABASE_URL"
        "CORS_ORIGINS"
    )
    
    source "$ENV_FILE"
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable $var is not set"
        fi
    done
    
    success "Environment validation passed"
}

# Build production images
build_images() {
    log "Building production images..."
    
    cd "$PROJECT_ROOT"
    
    # Set build arguments
    BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    VERSION="5.0.0"
    
    # Build backend image
    log "Building backend image..."
    docker build \
        --file backend/Dockerfile.prod \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg VCS_REF="$VCS_REF" \
        --build-arg VERSION="$VERSION" \
        --tag snaplearn/backend:$VERSION \
        --tag snaplearn/backend:latest \
        backend/
    
    # Build frontend image
    log "Building frontend image..."
    docker build \
        --file frontend/Dockerfile.prod \
        --build-arg REACT_APP_VERSION="$VERSION" \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --tag snaplearn/frontend:$VERSION \
        --tag snaplearn/frontend:latest \
        frontend/
    
    success "Images built successfully"
}

# Database operations
setup_database() {
    log "Setting up database..."
    
    # Check if database is already running
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        log "Database is already running"
    else
        log "Starting database..."
        docker-compose -f "$COMPOSE_FILE" up -d postgres
        
        # Wait for database to be ready
        log "Waiting for database to be ready..."
        timeout=60
        while ! docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "$POSTGRES_USER" -d snaplearn; do
            sleep 2
            timeout=$((timeout - 2))
            if [[ $timeout -le 0 ]]; then
                error "Database failed to start within 60 seconds"
            fi
        done
    fi
    
    success "Database setup completed"
}

# Deploy application
deploy_application() {
    log "Deploying SnapLearn AI to production..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images (if using registry)
    # docker-compose -f "$COMPOSE_FILE" pull
    
    # Start all services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Application deployment initiated"
}

# Health checks
run_health_checks() {
    log "Running health checks..."
    
    services=("backend" "frontend" "redis" "postgres")
    max_attempts=30
    
    for service in "${services[@]}"; do
        log "Checking health of $service..."
        
        attempts=0
        while [[ $attempts -lt $max_attempts ]]; do
            if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy"; then
                success "$service is healthy"
                break
            elif docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "unhealthy"; then
                error "$service is unhealthy"
            else
                log "Waiting for $service to be ready... (attempt $((attempts + 1))/$max_attempts)"
                sleep 5
                attempts=$((attempts + 1))
            fi
        done
        
        if [[ $attempts -eq $max_attempts ]]; then
            error "$service failed health check after $max_attempts attempts"
        fi
    done
    
    # Test API endpoints
    log "Testing API endpoints..."
    
    # Wait a bit more for services to stabilize
    sleep 10
    
    # Test backend health endpoint
    if curl -f -s http://localhost:8000/health > /dev/null; then
        success "Backend API is responding"
    else
        error "Backend API health check failed"
    fi
    
    # Test frontend
    if curl -f -s http://localhost:3000/health.html > /dev/null; then
        success "Frontend is responding"
    else
        error "Frontend health check failed"
    fi
    
    success "All health checks passed"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Ensure monitoring services are running
    monitoring_services=("prometheus" "grafana")
    
    for service in "${monitoring_services[@]}"; do
        if ! docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            log "Starting $service..."
            docker-compose -f "$COMPOSE_FILE" up -d "$service"
        fi
    done
    
    log "Monitoring setup completed"
    log "Grafana available at: http://localhost:3001"
    log "Prometheus available at: http://localhost:9090"
}

# Backup current deployment
backup_current_deployment() {
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log "Creating backup of current deployment..."
        
        backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Export current docker-compose state
        docker-compose -f "$COMPOSE_FILE" config > "$backup_dir/docker-compose-backup.yml"
        
        # Backup database
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
            -U "$POSTGRES_USER" -d snaplearn > "$backup_dir/database_backup.sql" || true
        
        success "Backup created at $backup_dir"
    fi
}

# Cleanup old resources
cleanup() {
    log "Cleaning up old resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful in production!)
    # docker volume prune -f
    
    # Remove old backups (keep last 7 days)
    find "$PROJECT_ROOT/backups" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    
    success "Cleanup completed"
}

# Display deployment info
show_deployment_info() {
    echo
    success "🎉 SnapLearn AI Phase 5 deployed successfully!"
    echo
    echo "📊 Service URLs:"
    echo "  • Frontend:    http://localhost:3000"
    echo "  • Backend API: http://localhost:8000"
    echo "  • API Docs:    http://localhost:8000/docs"
    echo "  • Grafana:     http://localhost:3001"
    echo "  • Prometheus:  http://localhost:9090"
    echo
    echo "🔧 Management Commands:"
    echo "  • View logs:     docker-compose -f $COMPOSE_FILE logs -f"
    echo "  • Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "  • Restart:       docker-compose -f $COMPOSE_FILE restart"
    echo "  • Scale:         docker-compose -f $COMPOSE_FILE up -d --scale backend=3"
    echo
    echo "📈 Monitoring:"
    echo "  • Container status: docker-compose -f $COMPOSE_FILE ps"
    echo "  • Resource usage:   docker stats"
    echo "  • Health checks:    ./deploy/health-check.sh"
    echo
}

# Main deployment function
main() {
    log "🚀 Starting SnapLearn AI Phase 5 Production Deployment"
    
    check_prerequisites
    validate_environment
    backup_current_deployment
    build_images
    setup_database
    deploy_application
    run_health_checks
    setup_monitoring
    cleanup
    show_deployment_info
    
    success "Deployment completed successfully! 🎉"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "health-check")
        run_health_checks
        ;;
    "cleanup")
        cleanup
        ;;
    "backup")
        backup_current_deployment
        ;;
    "stop")
        log "Stopping SnapLearn AI services..."
        docker-compose -f "$COMPOSE_FILE" down
        success "Services stopped"
        ;;
    "restart")
        log "Restarting SnapLearn AI services..."
        docker-compose -f "$COMPOSE_FILE" restart
        success "Services restarted"
        ;;
    *)
        echo "Usage: $0 {deploy|health-check|cleanup|backup|stop|restart}"
        echo
        echo "Commands:"
        echo "  deploy      - Full production deployment (default)"
        echo "  health-check - Run health checks on running services"
        echo "  cleanup     - Clean up old Docker resources"
        echo "  backup      - Backup current deployment"
        echo "  stop        - Stop all services"
        echo "  restart     - Restart all services"
        exit 1
        ;;
esac