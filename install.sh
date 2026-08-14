#!/bin/bash
# SpeediT - One-Click Installer
# curl -fsSL https://raw.githubusercontent.com/SpeedwiT/SpeediTBot/main/install.sh | bash

set -e

REPO="SpeedwiT/SpeediTBot"
INSTALL_DIR="/opt/speedit"

echo ""
echo "  ███████╗██████╗ ███████╗███████╗██████╗ ██╗████████╗"
echo "  ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██║╚══██╔══╝"
echo "  ███████╗██████╔╝█████╗  █████╗  ██║  ██║██║   ██║"
echo "  ╚════██║██╔═══╝ ██╔══╝  ██╔══╝  ██║  ██║██║   ██║"
echo "  ███████║██║     ███████╗███████╗██████╔╝██║   ██║"
echo "  ╚══════╝╚═╝     ╚══════╝╚══════╝╚═════╝ ╚═╝   ╚═╝"
echo ""
echo "  SpeediT - Telegram Bot Installer"
echo "  Support: @SpeedwIT"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root: sudo bash install.sh"
    exit 1
fi

# Check OS
if [ ! -f /etc/debian_version ] && [ ! -f /etc/lsb-release ]; then
    echo "WARNING: This script is designed for Ubuntu/Debian"
fi

echo "[1/6] Checking system..."

# Check RAM
RAM_MB=$(free -m | awk '/Mem:/{print $2}')
if [ "$RAM_MB" -lt 1000 ]; then
    echo "WARNING: Less than 1GB RAM. Recommended: 2GB+"
fi

echo "[2/6] Installing requirements..."

# Update system
apt-get update -qq

# Install required packages
apt-get install -y -qq curl wget git software-properties-common apt-transport-https ca-certificates

# Install Docker if not found
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not found
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    pip3 install docker-compose 2>/dev/null || {
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    }
fi

echo "[3/6] Getting configuration..."

# Get bot token
while true; do
    read -p "Enter Bot Token: " BOT_TOKEN
    if [ ${#BOT_TOKEN} -gt 20 ] && [[ "$BOT_TOKEN" == *":"* ]]; then
        break
    fi
    echo "Invalid token format. Try again."
done

# Get admin ID
while true; do
    read -p "Enter Admin ID (numeric): " ADMIN_ID
    if [[ "$ADMIN_ID" =~ ^[0-9]+$ ]] && [ ${#ADMIN_ID} -gt 5 ]; then
        break
    fi
    echo "Invalid ID. Enter numeric Telegram user ID."
done

# Get domain (optional)
read -p "Enter Domain (optional, press Enter to skip): " DOMAIN

EMAIL=""
if [ -n "$DOMAIN" ]; then
    read -p "Enter Email (for SSL): " EMAIL
fi

echo "[4/6] Downloading SpeediT..."

# Clone repository
cd /root
if [ -d "SpeediTBot" ]; then
    rm -rf SpeediTBot
fi
git clone "https://github.com/${REPO}.git"

# Copy files to install directory
mkdir -p "$INSTALL_DIR"
cp -r SpeediTBot/bot "$INSTALL_DIR/"
cp -r SpeediTBot/api "$INSTALL_DIR/"
cp -r SpeediTBot/webapp "$INSTALL_DIR/"
cp -r SpeediTBot/database "$INSTALL_DIR/"
cp -r SpeediTBot/config "$INSTALL_DIR/"
cp -r SpeediTBot/scripts "$INSTALL_DIR/"
cp -r SpeediTBot/nginx "$INSTALL_DIR/"
cp SpeediTBot/docker-compose.yml "$INSTALL_DIR/"
cp SpeediTBot/Dockerfile.* "$INSTALL_DIR/"
cp SpeediTBot/requirements-* "$INSTALL_DIR/"

# Create directories
mkdir -p "$INSTALL_DIR/nginx/ssl"
mkdir -p "$INSTALL_DIR/backups"

# Generate passwords
DB_PASS=$(openssl rand -base64 32 | tr -d '/+' | cut -c1-24)
REDIS_PASS=$(openssl rand -base64 32 | tr -d '/+' | cut -c1-24)
SECRET_KEY=$(openssl rand -base64 48 | tr -d '/+' | cut -c1-48)

# Create .env file
cat > "$INSTALL_DIR/.env" << EOF
# SpeediT Configuration
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_ID
USE_POLLING=true
WEBHOOK_URL=
DB_NAME=speedit
DB_USER=speedit
DB_PASSWORD=$DB_PASS
REDIS_PASSWORD=$REDIS_PASS
SECRET_KEY=$SECRET_KEY
DOMAIN=$DOMAIN
LOG_LEVEL=INFO
EOF

# Update docker-compose.yml with domain if provided
if [ -n "$DOMAIN" ]; then
    sed -i "s/server_name _;/server_name $DOMAIN;/" "$INSTALL_DIR/nginx/nginx.conf"
fi

echo "[5/6] Setting up SSL..."

if [ -n "$DOMAIN" ] && [ -n "$EMAIL" ]; then
    if ! command -v certbot &> /dev/null; then
        apt-get install -y -qq certbot python3-certbot-nginx
    fi
    
    # Stop any service on port 80
    systemctl stop nginx 2>/dev/null || true
    
    certbot certonly --standalone --non-interactive --agree-tos --email "$EMAIL" -d "$DOMAIN" 2>/dev/null || {
        echo "WARNING: SSL setup failed. Continuing without SSL."
    }
    
    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem "$INSTALL_DIR/nginx/ssl/"
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem "$INSTALL_DIR/nginx/ssl/"
        echo "SSL certificates installed"
    fi
fi

echo "[6/6] Deploying SpeediT..."

cd "$INSTALL_DIR"
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Check status
echo ""
echo "=============================="
echo "Installation Complete!"
echo "=============================="
echo ""
docker-compose ps
echo ""
echo "Commands:"
echo "  Logs:      cd $INSTALL_DIR && docker-compose logs -f"
echo "  Restart:   cd $INSTALL_DIR && docker-compose restart"
echo "  Stop:      cd $INSTALL_DIR && docker-compose stop"
echo "  Uninstall: cd $INSTALL_DIR && docker-compose down -v && rm -rf $INSTALL_DIR"
echo ""
if [ -n "$DOMAIN" ]; then
    echo "URLs:"
    echo "  Mini App: https://$DOMAIN/miniapp"
    echo "  API:      https://$DOMAIN/api"
    echo ""
fi
echo "Support: @SpeedwIT"
echo "Channel: @Speedw_IT"
echo ""
