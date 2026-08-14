# ProxiMan - Telegram Bot & Mini App

## Overview
A comprehensive Telegram Bot and Mini App system for managing VPN panels with full sales automation.

## Architecture

```
proxyman/
├── bot/              # Telegram Bot (python-telegram-bot)
├── api/              # REST API (FastAPI)
├── webapp/           # Mini App (HTML/JS/CSS)
├── database/         # SQLAlchemy models & migrations
├── config/           # Configuration files
├── nginx/            # Nginx config & SSL
├── scripts/          # Utility scripts
├── docker-compose.yml
├── install.sh        # One-command installer
└── README.md
```

## Quick Install

```bash
git clone https://github.com/yourusername/proxyman.git
cd proxyman
chmod +x install.sh
sudo ./install.sh
```

## Features

### Triple Sales System
1. **Config Sales** - Automatic config generation after payment
2. **Reseller Panel Sales** - Create sub-admin accounts
3. **VPS Sales** - Order -> Prepare -> Deliver workflow

### Multi-Panel Support
| Panel | Status | Features |
|-------|--------|----------|
| Sanaei/X-UI | ✅ | Full CRUD, user management |
| Marzban | ✅ | Full CRUD, node management |
| PasarGuard | ✅ | Full CRUD, admin creation |
| Rebecca | ✅ | Full CRUD, multi-server |
| HM Panel | ✅ | Full API bridge wrapper |

### Payment System
- **Card-to-Card** with dynamic bank card image generation
- **Receipt Upload** with instant admin notification
- **Approve/Reject** buttons for admins
- **QR Code** generation for subscriptions

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| `/admin` | Admin panel (admins only) |
| `/panel` | Connect panel |
| `/support` | Support contact |
| `/help` | Help |

## Admin Panel Features

### Product Management
- Add/Edit/Delete products
- Category management
- Pricing configuration
- Traffic & duration settings

### Panel Management
- Connect multiple panels
- Test connection
- Auto-create users

### Order Management
- View all orders
- Pending payments
- VPS orders

### User Management
- View user list
- Ban/Unban users
- Balance management

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/{telegram_id}` | Get user info |
| POST | `/api/users` | Create user |
| GET | `/api/products` | List products |
| GET | `/api/orders` | List orders |
| POST | `/api/orders` | Create order |
| GET | `/api/panels` | List panels |
| POST | `/api/panels/{id}/test` | Test panel |
| GET | `/api/cards` | List bank cards |
| POST | `/api/transactions/{id}/verify` | Verify transaction |

## Configuration

Edit `.env` file:

```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789,987654321
DB_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password
SECRET_KEY=your_secret_key
DOMAIN=your-domain.com
```

## Development

```bash
# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f bot

# Run migrations
docker-compose exec bot python -m database.migrations

# Create admin
docker-compose exec bot python -c "from database.models import User; ..."
```

## Production Deployment

```bash
# Clone
git clone https://github.com/yourusername/proxyman.git /opt/proxyman
cd /opt/proxyman

# Configure
cp .env.example .env
nano .env

# Run installer
sudo ./install.sh
```

## Security

- All passwords hashed with bcrypt
- API authentication via JWT tokens
- Rate limiting on all endpoints
- SSL/TLS encryption
- Database encryption at rest
- Regular backups recommended

## Backup

```bash
./scripts/backup.sh
```

## Update

```bash
./scripts/update.sh
```

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/yourusername/proxyman/issues
- Telegram: @your_support
