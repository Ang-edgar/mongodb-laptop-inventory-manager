#!/bin/bash

# Laptop Inventory Management System - Setup Script
# This script automates the installation and setup process

set -e  # Exit on error

echo "============================================"
echo "  Laptop Inventory Management System"
echo "  Setup Script"
echo "============================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Detected OS: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Detected OS: macOS"
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Check if Docker is installed
check_docker() {
    echo ""
    print_info "Checking Docker installation..."
    
    if command -v docker &> /dev/null; then
        print_success "Docker is installed: $(docker --version)"
    else
        print_error "Docker is not installed"
        echo ""
        echo "Please install Docker first:"
        echo "  Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        echo "  macOS: brew install docker"
        echo "  Or visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed: $(docker-compose --version)"
    else
        print_error "Docker Compose is not installed"
        exit 1
    fi
}

# Check if MongoDB is installed (for non-Docker setup)
check_mongodb() {
    echo ""
    print_info "Checking MongoDB installation..."
    
    if command -v mongod &> /dev/null; then
        print_success "MongoDB is installed: $(mongod --version | head -n1)"
        return 0
    else
        print_info "MongoDB is not installed (OK if using Docker)"
        return 1
    fi
}

# Setup environment file
setup_env() {
    echo ""
    print_info "Setting up environment configuration..."
    
    if [ -f ".env" ]; then
        print_info ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        
        # Generate random secret key
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
        
        if [[ "$OS" == "macos" ]]; then
            sed -i '' "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
        else
            sed -i "s/your-secret-key-change-this-in-production/$SECRET_KEY/" .env
        fi
        
        print_success "Generated random SECRET_KEY"
        
        echo ""
        print_info "Please review and update .env file with your settings"
        print_info "Important: Change ADMIN_PASSWORD before deploying to production!"
    else
        print_error ".env.example not found"
        exit 1
    fi
}

# Setup with Docker
setup_docker() {
    echo ""
    print_info "Setting up with Docker..."
    
    # Pull images
    print_info "Pulling Docker images..."
    docker-compose pull
    
    # Start services
    print_info "Starting services..."
    docker-compose up -d
    
    # Wait for MongoDB to be ready
    print_info "Waiting for MongoDB to be ready..."
    sleep 5
    
    # Initialize database
    print_info "Initializing database..."
    docker-compose exec -T web python scripts/init_db.py || {
        print_error "Database initialization failed"
        print_info "You can run it manually later: docker-compose exec web python scripts/init_db.py"
    }
    
    print_success "Docker setup complete!"
}

# Setup manual installation
setup_manual() {
    echo ""
    print_info "Setting up manual installation..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python is installed: $(python3 --version)"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
    
    # Check MongoDB
    if ! check_mongodb; then
        print_error "MongoDB is not installed or not running"
        echo ""
        echo "Please install MongoDB:"
        echo "  Ubuntu/Debian: sudo apt-get install mongodb"
        echo "  macOS: brew install mongodb-community"
        exit 1
    fi
    
    # Initialize database
    print_info "Initializing database..."
    python scripts/init_db.py
    
    print_success "Manual setup complete!"
}

# Display completion message
show_completion() {
    echo ""
    echo "============================================"
    echo "  Setup Complete! 🎉"
    echo "============================================"
    echo ""
    
    if [[ $SETUP_TYPE == "docker" ]]; then
        echo "Your application is running with Docker!"
        echo ""
        echo "Access the application:"
        echo "  URL: http://localhost:5000"
        echo ""
        echo "Default credentials:"
        echo "  Username: admin"
        echo "  Password: admin123"
        echo ""
        echo "Useful commands:"
        echo "  View logs:    docker-compose logs -f"
        echo "  Stop:         docker-compose down"
        echo "  Restart:      docker-compose restart"
        echo "  Rebuild:      docker-compose up -d --build"
    else
        echo "Manual setup complete!"
        echo ""
        echo "To run the application:"
        echo "  1. Activate virtual environment: source venv/bin/activate"
        echo "  2. Start the application: cd app && python __init__.py"
        echo ""
        echo "Access the application:"
        echo "  URL: http://localhost:5000"
        echo ""
        echo "Default credentials:"
        echo "  Username: admin"
        echo "  Password: admin123"
    fi
    
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "  - Change the default admin password!"
    echo "  - Update SECRET_KEY in .env for production"
    echo "  - Review DEPLOYMENT.md for production setup"
    echo ""
    echo "============================================"
}

# Main setup flow
main() {
    check_os
    
    echo ""
    echo "Choose setup method:"
    echo "  1) Docker (Recommended - Easiest)"
    echo "  2) Manual Installation"
    echo ""
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            SETUP_TYPE="docker"
            check_docker
            setup_env
            setup_docker
            ;;
        2)
            SETUP_TYPE="manual"
            setup_env
            setup_manual
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    show_completion
}

# Run main function
main
