<div align="center">

# 🚀 SpeediT

### Telegram Bot for VPN Panel Management

[![Stars](https://img.shields.io/github/stars/SpeedwiT?style=flat-square&color=yellow)](https://github.com/SpeedwiT)
[![Telegram Support](https://img.shields.io/badge/Telegram-Support-2CA5E0?style=flat-square&logo=telegram)](https://t.me/SpeedwIT)
[![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-2CA5E0?style=flat-square&logo=telegram)](https://t.me/Speedw_IT)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**Advanced Telegram Bot + Mini App for managing VPN panels with full sales automation**

</div>

---

## 🇮🇷 [فارسی](https://github.com/SpeedwiT/SpeediTBot/blob/main/docs/README_fa.md)

---

## 🚀 Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/SpeedwiT/SpeediTBot/main/install.sh | bash
```

---

## ⚡ Features

### Triple Sales System
- **Config Sales** - Automated config generation after payment
- **Reseller Panel Sales** - Create sub-admin accounts directly from bot
- **VPS Sales** - Order -> Prepare -> Deliver workflow

### Multi-Panel Support
| Panel | Status | Features |
|-------|--------|----------|
| Sanaei/X-UI | ✅ | Full CRUD, user management |
| Marzban | ✅ | Full CRUD, node management |
| PasarGuard | ✅ | Full CRUD, admin creation |
| Rebecca | ✅ | Full CRUD, multi-server |
| HM Panel | ✅ | Full API bridge wrapper |

### Smart Card-to-Card
- Dynamic bank card image generation
- Receipt upload with instant admin notification
- Approve/Reject buttons for admins

### Modern Telegram UI
- Styled/colored buttons
- Premium emojis support
- Modern Mini App interface

---

## 🛠️ Management Menu

```bash
sudo python3 speedit.py speed
```

| Option | Description |
|--------|-------------|
| 📊 Check Status | Container health, RAM, disk, network |
| 📜 View Logs | Live logs for all services |
| 🔄 Restart | Restart all services |
| ⏹️ Stop | Stop all services |
| ▶️ Start | Start all services |
| ⬆️ Update | Pull latest from GitHub and rebuild |
| 💾 Backup | Full backup of bot, DB, configs |
| ♻️ Restore | Restore from backup |
| 🗑️ Uninstall | Complete removal |

---

## 📋 Requirements

- Ubuntu 20.04+ / Debian 11+
- 2GB RAM (minimum)
- 20GB Disk
- Domain name (optional, for webhook + SSL)

---

## 🏗️ Architecture

```
speedit/
├── bot/              # Telegram Bot (python-telegram-bot)
├── api/              # REST API (FastAPI)
├── webapp/           # Mini App (HTML/JS/CSS)
├── database/         # SQLAlchemy models & migrations
├── config/           # Configuration files
├── nginx/            # Nginx config & SSL
├── scripts/          # Utility scripts
├── docker-compose.yml
├── speedit.py        # CLI Manager
└── install.sh        # Auto installer
```

---

## 🔌 API Endpoints

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

---

## 💳 Supported Payment Methods

- Card-to-Card (manual with admin approval)
- Crypto (NowPayments, Plisio)
- Online gateways (Zarinpal, Aqayepardakht, IranPay)

---

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| `/admin` | Admin panel |
| `/help` | Help |
| `/support` | Support contact |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Contact

- **Support:** [@SpeedwIT](https://t.me/SpeedwIT)
- **Channel:** [@Speedw_IT](https://t.me/Speedw_IT)
- **GitHub:** [https://github.com/SpeedwiT](https://github.com/SpeedwiT)

---

<div align="center">

**Made with ❤️ by SpeediT Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>
