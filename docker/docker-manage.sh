#!/bin/bash
# Docker management scripts for Email Client

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp "$PROJECT_DIR/docker/.env.example" "$PROJECT_DIR/.env"
        print_warning "Please edit .env file with your configuration before proceeding."
        return 1
    fi
    return 0
}

# Development setup
setup_dev() {
    print_status "Setting up development environment..."
    
    check_docker
    if ! check_env_file; then
        exit 1
    fi
    
    print_status "Building and starting development containers..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    
    print_status "Waiting for services to be ready..."
    sleep 30
    
    print_status "Running database migrations..."
    docker-compose exec backend python -c "
from app.core.database import create_tables
create_tables()
print('Database tables created successfully!')
"
    
    print_success "Development environment is ready!"
    print_status "Access the application at: http://localhost"
    print_status "Backend API docs at: http://localhost:8000/docs"
    print_status "Mailpit (testing) at: http://localhost:8025"
}

# Production setup
setup_prod() {
    print_status "Setting up production environment..."
    
    check_docker
    if ! check_env_file; then
        exit 1
    fi
    
    # Check required environment variables for production
    if ! grep -q "SECRET_KEY=your-super-secret-key-change-this-in-production" "$PROJECT_DIR/.env"; then
        print_error "Please change the SECRET_KEY in .env file for production!"
        exit 1
    fi
    
    print_status "Building and starting production containers..."
    docker-compose -f docker-compose.yml up --build -d
    
    print_status "Waiting for services to be ready..."
    sleep 30
    
    print_status "Running database migrations..."
    docker-compose exec backend python -c "
from app.core.database import create_tables
create_tables()
print('Database tables created successfully!')
"
    
    print_success "Production environment is ready!"
    print_status "Access the application at: http://localhost"
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped."
}

# Clean up everything
cleanup() {
    print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up Docker resources..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Cleanup completed."
    else
        print_status "Cleanup cancelled."
    fi
}

# Show logs
show_logs() {
    SERVICE=${1:-}
    if [ -n "$SERVICE" ]; then
        print_status "Showing logs for $SERVICE..."
        docker-compose logs -f "$SERVICE"
    else
        print_status "Showing logs for all services..."
        docker-compose logs -f
    fi
}

# Check service status
check_status() {
    print_status "Checking service status..."
    docker-compose ps
    
    print_status "Checking service health..."
    for service in backend frontend database redis; do
        if docker-compose ps | grep -q "$service.*Up"; then
            if docker-compose exec "$service" echo "Health check" > /dev/null 2>&1; then
                print_success "$service: Running and healthy"
            else
                print_warning "$service: Running but may have issues"
            fi
        else
            print_error "$service: Not running"
        fi
    done
}

# Backup database
backup_db() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    print_status "Creating database backup: $BACKUP_FILE"
    
    docker-compose exec database pg_dump -U emailuser emailclient > "$PROJECT_DIR/backups/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Database backup created: $BACKUP_FILE"
    else
        print_error "Database backup failed"
        exit 1
    fi
}

# Restore database
restore_db() {
    BACKUP_FILE=${1:-}
    if [ -z "$BACKUP_FILE" ]; then
        print_error "Please provide backup file name"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_DIR/backups/$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_warning "This will overwrite the current database. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Restoring database from: $BACKUP_FILE"
        docker-compose exec -T database psql -U emailuser emailclient < "$PROJECT_DIR/backups/$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            print_success "Database restored successfully"
        else
            print_error "Database restore failed"
            exit 1
        fi
    else
        print_status "Database restore cancelled"
    fi
}

# Update application
update_app() {
    print_status "Updating application..."
    
    print_status "Pulling latest changes..."
    git pull
    
    print_status "Rebuilding containers..."
    docker-compose build --no-cache
    
    print_status "Restarting services..."
    docker-compose up -d
    
    print_success "Application updated successfully!"
}

# Main script logic
case "${1:-}" in
    "dev"|"development")
        setup_dev
        ;;
    "prod"|"production")
        setup_prod
        ;;
    "stop")
        stop_services
        ;;
    "cleanup")
        cleanup
        ;;
    "logs")
        show_logs "${2:-}"
        ;;
    "status")
        check_status
        ;;
    "backup")
        backup_db
        ;;
    "restore")
        restore_db "${2:-}"
        ;;
    "update")
        update_app
        ;;
    *)
        echo "Email Client Docker Management Script"
        echo ""
        echo "Usage: $0 {dev|prod|stop|cleanup|logs|status|backup|restore|update}"
        echo ""
        echo "Commands:"
        echo "  dev        - Setup development environment"
        echo "  prod       - Setup production environment"
        echo "  stop       - Stop all services"
        echo "  cleanup    - Remove all containers, images, and volumes"
        echo "  logs       - Show logs for all services or specific service"
        echo "  status     - Check service status and health"
        echo "  backup     - Create database backup"
        echo "  restore    - Restore database from backup"
        echo "  update     - Update application (git pull + rebuild)"
        echo ""
        echo "Examples:"
        echo "  $0 dev                    # Start development environment"
        echo "  $0 logs backend          # Show backend logs"
        echo "  $0 restore backup.sql    # Restore from backup file"
        exit 1
        ;;
esac
