#!/bin/bash
# ============================================
# ProxiMan - Automatic Installer
# نصب خودکار سیستم مدیریت پنل VPN
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables
PROJECT_NAME="proxyman"
PROJECT_DIR="/opt/${PROJECT_NAME}"
GITHUB_REPO="https://github.com/yourusername/proxyman.git"
DOMAIN=""
EMAIL=""
BOT_TOKEN=""
ADMIN_IDS=""

# ============================================
# Functions
# ============================================

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                                                      ║"
    echo "║   ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗███╗   ███╗   ║"
    echo "║   ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝██║████╗ ████║   ║"
    echo "║   ██████╔╝██████╔╝██║   ██║ ╚███╔╝ ██║██╔████╔██║   ║"
    echo "║   ██╔══██╗██╔══██╗██║   ██║ ██╔██╗ ██║██║╚██╔╝██║   ║"
    echo "║   ██║  ██║██║  ██║╚██████╔╝██╔╝ ██╗██║██║ ╚═╝ ██║   ║"
    echo "║   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝   ║"
    echo "║                                                      ║"
    echo "║   Telegram Bot + Mini App for VPN Panel Management   ║"
    echo "║                                                      ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "لطفاً این اسکریپت را با دسترسی root اجرا کنید:"
        log_error "sudo ./install.sh"
        exit 1
    fi
}

check_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [ "$ID" != "ubuntu" ] && [ "$ID" != "debian" ]; then
            log_warn "این اسکریپت برای Ubuntu/Debian طراحی شده است."
            log_warn "سیستم عامل شما: $ID"
            read -p "آیا می‌خواهید ادامه دهید؟ (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
        log_info "سیستم عامل: $PRETTY_NAME"
    else
        log_error "تشخیص سیستم عامل ممکن نیست."
        exit 1
    fi
}

collect_info() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}  جمع‌آوری اطلاعات نصب${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo ""

    # Domain
    while [ -z "$DOMAIN" ]; do
        read -p "🌐 دامنه خود را وارد کنید (مثال: bot.example.com): " DOMAIN
        if [ -z "$DOMAIN" ]; then
            log_error "دامنه الزامی است."
        fi
    done

    # Email
    while [ -z "$EMAIL" ]; do
        read -p "📧 ایمیل خود را وارد کنید (برای SSL): " EMAIL
        if [ -z "$EMAIL" ]; then
            log_error "ایمیل الزامی است."
        fi
    done

    # Bot Token
    while [ -z "$BOT_TOKEN" ]; do
        read -p "🤖 توکن ربات تلگرام را وارد کنید: " BOT_TOKEN
        if [ -z "$BOT_TOKEN" ]; then
            log_error "توکن ربات الزامی است."
        fi
    done

    # Admin IDs
    while [ -z "$ADMIN_IDS" ]; do
        read -p "👤 آیدی عددی ادمین‌ها را وارد کنید (با کاما جدا کنید): " ADMIN_IDS
        if [ -z "$ADMIN_IDS" ]; then
            log_error "حداقل یک آیدی ادمین الزامی است."
        fi
    done

    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${CYAN}  خلاصه اطلاعات${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "🌐 دامنه: ${GREEN}$DOMAIN${NC}"
    echo -e "📧 ایمیل: ${GREEN}$EMAIL${NC}"
    echo -e "🤖 توکن ربات: ${GREEN}${BOT_TOKEN:0:10}...${NC}"
    echo -e "👤 ادمین‌ها: ${GREEN}$ADMIN_IDS${NC}"
    echo ""

    read -p "آیا اطلاعات صحیح است؟ (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        DOMAIN=""
        EMAIL=""
        BOT_TOKEN=""
        ADMIN_IDS=""
        collect_info
    fi
}

update_system() {
    log_step "بروزرسانی سیستم..."
    apt-get update -y
    apt-get upgrade -y
    apt-get install -y \
        curl \
        wget \
        git \
        vim \
        nano \
        htop \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    log_info "سیستم بروزرسانی شد."
}

install_docker() {
    log_step "نصب Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker قبلاً نصب شده است."
        docker --version
    else
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl enable docker
        systemctl start docker
        log_info "Docker نصب شد."
    fi

    # Install Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose قبلاً نصب شده است."
    else
        DOCKER_COMPOSE_VERSION="2.23.0"
        curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        log_info "Docker Compose نصب شد."
    fi
}

install_nginx() {
    log_step "نصب Nginx..."
    
    if command -v nginx &> /dev/null; then
        log_info "Nginx قبلاً نصب شده است."
    else
        apt-get install -y nginx
        systemctl enable nginx
        systemctl start nginx
        log_info "Nginx نصب شد."
    fi
}

install_certbot() {
    log_step "نصب Certbot برای SSL..."
    
    if command -v certbot &> /dev/null; then
        log_info "Certbot قبلاً نصب شده است."
    else
        apt-get install -y certbot python3-certbot-nginx
        log_info "Certbot نصب شد."
    fi
}

setup_ssl() {
    log_step "دریافت گواهی SSL..."
    
    # Stop nginx temporarily
    systemctl stop nginx 2>/dev/null || true
    
    # Get certificate
    certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        || {
            log_warn "دریافت SSL با خطا مواجه شد. از HTTP استفاده می‌شود."
            return 1
        }
    
    # Copy certificates
    mkdir -p /opt/proxyman/nginx/ssl
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/proxyman/nginx/ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/proxyman/nginx/ssl/
    
    log_info "گواهی SSL دریافت و کپی شد."
    
    # Setup auto-renewal
    echo "0 0,12 * * * root certbot renew --quiet && docker-compose -f /opt/proxyman/docker-compose.yml restart nginx" >> /etc/crontab
    
    systemctl start nginx 2>/dev/null || true
}

setup_firewall() {
    log_step "تنظیم فایروال..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 8443/tcp
        ufw --force enable
        log_info "فایروال تنظیم شد."
    fi
}

clone_project() {
    log_step "دانلود پروژه..."
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warn "پوشه پروژه قبلاً وجود دارد."
        cd "$PROJECT_DIR"
        git pull
    else
        git clone "$GITHUB_REPO" "$PROJECT_DIR" 2>/dev/null || {
            log_info "استفاده از فایل‌های محلی..."
            mkdir -p "$PROJECT_DIR"
        }
    fi
    
    log_info "پروژه آماده است."
}

create_env_file() {
    log_step "ایجاد فایل تنظیمات..."
    
    cd "$PROJECT_DIR"
    
    # Generate random passwords
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d '/+' | cut -c1-24)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '/+' | cut -c1-24)
    SECRET_KEY=$(openssl rand -base64 48 | tr -d '/+' | cut -c1-48)
    
    cat > .env << EOF
# ProxiMan Configuration
# Generated on $(date)

# Telegram Bot
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_IDS
USE_POLLING=true
WEBHOOK_URL=https://$DOMAIN/webhook

# Database
DB_NAME=proxyman
DB_USER=proxyman
DB_PASSWORD=$DB_PASSWORD

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD

# Security
SECRET_KEY=$SECRET_KEY

# Domain
DOMAIN=$DOMAIN

# Logging
LOG_LEVEL=INFO
EOF

    log_info "فایل .env ایجاد شد."
}

create_nginx_config() {
    log_step "ایجاد تنظیمات Nginx..."
    
    cd "$PROJECT_DIR"
    
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        # HTTPS config
        cat > nginx/nginx.conf << 'EOF'
server {
    listen 80;
    server_name DOMAIN;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name DOMAIN;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # API
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Mini App
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Bot webhook
    location /webhook {
        proxy_pass http://bot:8443/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /usr/share/nginx/html/;
    }
}
EOF
    else
        # HTTP config
        cat > nginx/nginx.conf << 'EOF'
server {
    listen 80;
    server_name DOMAIN;

    # API
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Mini App
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Bot webhook
    location /webhook {
        proxy_pass http://bot:8443/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /usr/share/nginx/html/;
    }
}
EOF
    fi
    
    # Replace DOMAIN placeholder
    sed -i "s/DOMAIN/$DOMAIN/g" nginx/nginx.conf
    
    log_info "تنظیمات Nginx ایجاد شد."
}

deploy_project() {
    log_step "راه‌اندازی پروژه..."
    
    cd "$PROJECT_DIR"
    
    # Build and start containers
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for services
    log_info "صبر برای راه‌اندازی سرویس‌ها..."
    sleep 15
    
    # Check status
    docker-compose ps
    
    log_info "پروژه با موفقیت راه‌اندازی شد!"
}

print_success() {
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  نصب با موفقیت انجام شد!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "🌐 آدرس ربات: ${CYAN}https://$DOMAIN${NC}"
    echo -e "🌐 API: ${CYAN}https://$DOMAIN/api/${NC}"
    echo -e "📱 Mini App: ${CYAN}https://$DOMAIN/miniapp${NC}"
    echo ""
    echo -e "${YELLOW}دستورات مفید:${NC}"
    echo -e "  مشاهده لاگ‌ها: ${CYAN}cd $PROJECT_DIR && docker-compose logs -f${NC}"
    echo -e "  توقف ربات: ${CYAN}cd $PROJECT_DIR && docker-compose stop${NC}"
    echo -e "  راه‌اندازی مجدد: ${CYAN}cd $PROJECT_DIR && docker-compose restart${NC}"
    echo -e "  بروزرسانی: ${CYAN}cd $PROJECT_DIR && git pull && docker-compose up -d --build${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  حتماً موارد زیر را انجام دهید:${NC}"
    echo -e "  1. تنظیم Webhook ربات در @BotFather"
    echo -e "  2. افزودن کارت بانکی از پنل ادمین ربات"
    echo -e "  3. ایجاد دسته‌بندی و محصولات"
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════${NC}"
}

# ============================================
# Main Installation
# ============================================

main() {
    clear
    print_banner
    check_root
    check_os
    collect_info
    
    echo ""
    echo -e "${CYAN}شروع نصب...${NC}"
    echo ""
    
    update_system
    install_docker
    install_nginx
    install_certbot
    setup_firewall
    clone_project
    create_env_file
    create_nginx_config
    setup_ssl
    deploy_project
    
    print_success
}

# Run
main "$@"
