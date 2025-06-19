#!/bin/bash

# Crypto News Bot Deploy Script
# Usage: ./deploy.sh [heroku|docker|local]

set -e

DEPLOY_TYPE=${1:-local}
BOT_NAME="crypto-news-bot"

echo "🚀 Kripto Xəbər Botu Deploy Script"
echo "📦 Deploy tipi: $DEPLOY_TYPE"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env faylı tapılmadı!"
        log_info "env_example.txt faylını .env adı ilə kopyalayın və API key-ləri doldurún"
        cp env_example.txt .env
        log_info ".env faylı yaradıldı. Zəhmət olmasa API key-ləri doldurún:"
        echo "- TELEGRAM_BOT_TOKEN"
        echo "- GEMINI_API_KEY"
        echo "- ADMIN_USER_IDS"
        exit 1
    fi
    log_success ".env faylı mövcuddur"
}

# Check Python and pip
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 quraşdırılmayıb!"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 quraşdırılmayıb!"
        exit 1
    fi
    
    log_success "Python və pip mövcuddur"
}

# Install dependencies
install_deps() {
    log_info "Python paketləri quraşdırılır..."
    pip3 install -r requirements.txt
    log_success "Paketlər quraşdırıldı"
}

# Local deployment
deploy_local() {
    log_info "🏠 Local deployment başlayır..."
    
    check_python
    check_env
    install_deps
    
    log_info "Botu test edirik..."
    python3 test_bot.py
    
    log_success "✅ Local deployment tamamlandı!"
    log_info "Botu başlatmaq üçün: python3 main.py"
}

# Heroku deployment
deploy_heroku() {
    log_info "☁️  Heroku deployment başlayır..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        log_error "Heroku CLI quraşdırılmayıb!"
        log_info "Quraşdırmaq üçün: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    check_env
    
    # Login to Heroku
    log_info "Heroku-ya giriş..."
    heroku login
    
    # Create Heroku app
    log_info "Heroku app yaradılır..."
    heroku create $BOT_NAME || log_warning "App artıq mövcuddur"
    
    # Set environment variables
    log_info "Environment variables təyin edilir..."
    source .env
    heroku config:set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" --app $BOT_NAME
    heroku config:set GEMINI_API_KEY="$GEMINI_API_KEY" --app $BOT_NAME
    heroku config:set ADMIN_USER_IDS="$ADMIN_USER_IDS" --app $BOT_NAME
    
    # Deploy to Heroku
    log_info "Heroku-ya deploy edilir..."
    git add .
    git commit -m "Deploy crypto news bot" || true
    git push heroku main || git push heroku master
    
    # Scale worker
    heroku ps:scale worker=1 --app $BOT_NAME
    
    log_success "✅ Heroku deployment tamamlandı!"
    log_info "Logları görmək üçün: heroku logs --tail --app $BOT_NAME"
}

# Docker deployment
deploy_docker() {
    log_info "🐳 Docker deployment başlayır..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker quraşdırılmayıb!"
        log_info "Quraşdırmaq üçün: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    check_env
    
    # Build Docker image
    log_info "Docker image build edilir..."
    docker build -t $BOT_NAME .
    
    # Stop existing container
    log_info "Köhnə container dayandırılır..."
    docker stop $BOT_NAME 2>/dev/null || true
    docker rm $BOT_NAME 2>/dev/null || true
    
    # Run new container
    log_info "Yeni container başladılır..."
    docker run -d \
        --name $BOT_NAME \
        --restart unless-stopped \
        --env-file .env \
        -v $(pwd)/logs:/app/logs \
        $BOT_NAME
    
    log_success "✅ Docker deployment tamamlandı!"
    log_info "Container statusu: docker ps | grep $BOT_NAME"
    log_info "Logları görmək üçün: docker logs -f $BOT_NAME"
}

# Docker Compose deployment
deploy_docker_compose() {
    log_info "🐳 Docker Compose deployment başlayır..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose quraşdırılmayıb!"
        exit 1
    fi
    
    check_env
    
    # Stop existing services
    log_info "Mövcud servislər dayandırılır..."
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    log_info "Servislər başladılır..."
    docker-compose up -d --build
    
    log_success "✅ Docker Compose deployment tamamlandı!"
    log_info "Servis statusu: docker-compose ps"
    log_info "Logları görmək üçün: docker-compose logs -f"
}

# Main deployment logic
case $DEPLOY_TYPE in
    "local")
        deploy_local
        ;;
    "heroku")
        deploy_heroku
        ;;
    "docker")
        deploy_docker
        ;;
    "docker-compose")
        deploy_docker_compose
        ;;
    *)
        log_error "Naməlum deploy tipi: $DEPLOY_TYPE"
        echo "İstifadə: $0 [local|heroku|docker|docker-compose]"
        exit 1
        ;;
esac

echo ""
log_success "🎉 Deployment tamamlandı!"
echo "==================================" 