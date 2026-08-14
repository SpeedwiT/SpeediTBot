<div align="center">

# 🚀 SpeediT

### ربات تلگرام مدیریت پنل‌های VPN

[![Stars](https://img.shields.io/github/stars/SpeedwiT?style=flat-square&color=yellow)](https://github.com/SpeedwiT)
[![Telegram Support](https://img.shields.io/badge/Telegram-Support-2CA5E0?style=flat-square&logo=telegram)](https://t.me/SpeedwIT)
[![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-2CA5E0?style=flat-square&logo=telegram)](https://t.me/Speedw_IT)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**ربات تلگرام + مینی‌اپ برای مدیریت پنل‌های VPN با سیستم فروش خودکار**

</div>

---

## 📸 پیش‌نمایش

```
   ███████╗██████╗ ███████╗███████╗██████╗ ██╗████████╗
   ██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██║╚══██╔══╝
   ███████╗██████╔╝█████╗  █████╗  ██║  ██║██║   ██║   
   ╚════██║██╔═══╝ ██╔══╝  ██╔══╝  ██║  ██║██║   ██║   
   ███████║██║     ███████╗███████╗██████╔╝██║   ██║   
   ╚══════╝╚═╝     ╚══════╝╚══════╝╚═════╝ ╚═╝   ╚═╝   
```

---

## 🚀 نصب سریع (One-Click)

### با دامنه (Webhook + SSL):
```bash
curl -fsSL https://raw.githubusercontent.com/SpeedwiT/SpeediTBot/main/install.sh | bash
```

### بدون دامنه (Polling):
```bash
curl -fsSL https://raw.githubusercontent.com/SpeedwiT/SpeediTBot/main/install.sh | bash
```

> **توجه:** اگر دامنه ندارید، گزینه Domain رو خالی بذارید. ربات حالت Polling فعال میشه و نیازی به SSL نداره.

---

## 📋 پیش‌نیازها

- **سیستم‌عامل:** Ubuntu 20.04+ / Debian 11+
- **رم:** حداقل 2GB
- **دیسک:** حداقل 20GB
- **دامنه:** اختیاری (برای Webhook و SSL)

---

## 🏗️ معماری پروژه

```
speedit/
├── bot/              # ربات تلگرام (python-telegram-bot)
├── api/              # REST API (FastAPI)
├── webapp/           # مینی‌اپ (HTML/JS/CSS)
├── database/         # مدل‌های SQLAlchemy
├── config/           # فایل‌های تنظیمات
├── nginx/            # تنظیمات Nginx و SSL
├── scripts/          # اسکریپت‌های کمکی
├── docker-compose.yml
├── speedit.py        # مدیریت CLI
└── install.sh        # نصب‌کننده خودکار
```

---

## 🎯 قابلیت‌ها

### سیستم فروش سه‌گانه
- **فروش کانفیگ** - ساخت خودکار کانفیگ بعد از پرداخت
- **فروش پنل نمایندگی** - ساخت حساب زیر-ادمین مستقیم از ربات
- **فروش VPS** - سفارش -> آماده‌سازی -> تحویل

### پشتیبانی چند پنلی
| پنل | وضعیت | قابلیت‌ها |
|-----|--------|-----------|
| Sanaei/X-UI | ✅ | مدیریت کامل، مدیریت کاربران |
| Marzban | ✅ | مدیریت کامل، مدیریت نودها |
| PasarGuard | ✅ | مدیریت کامل، ساخت ادمین |
| Rebecca | ✅ | مدیریت کامل، چند سروره |
| HM Panel | ✅ | API bridge کامل |

### کارت به کارت هوشمند
- تولید داینامیک تصویر کارت بانکی
- آپلود فیش با اطلاع‌رسانی فوری به ادمین
- دکمه‌های تایید/رد برای ادمین

### رابط کاربری مدرن
- دکمه‌های رنگی و استایل‌شده
- پشتیبانی از ایموجی‌های پرمیوم
- مینی‌اپ مدرن

---

## 🔌 API Endpoints

| Method | Endpoint | توضیحات |
|--------|----------|---------|
| GET | `/api/users/{telegram_id}` | دریافت اطلاعات کاربر |
| POST | `/api/users` | ساخت کاربر جدید |
| GET | `/api/products` | لیست محصولات |
| GET | `/api/orders` | لیست سفارشات |
| POST | `/api/orders` | ساخت سفارش |
| GET | `/api/panels` | لیست پنل‌ها |
| POST | `/api/panels/{id}/test` | تست پنل |
| GET | `/api/cards` | لیست کارت‌های بانکی |
| POST | `/api/transactions/{id}/verify` | تایید تراکنش |

---

## 💳 روش‌های پرداخت پشتیبانی‌شده
- کارت به کارت (دستی با تایید ادمین)
- ارز دیجیتال (NowPayments, Plisio)
- درگاه‌های آنلاین (زرین‌پال, آقای پرداخت, ایران‌پی)

---

## 📱 دستورات ربات

| دستور | توضیحات |
|-------|---------|
| `/start` | منوی اصلی |
| `/admin` | پنل مدیریت |
| `/help` | راهنما |
| `/support` | پشتیبانی |

---

## 📄 مجمج

این پروژه تحت مجوز MIT منتشر شده - فایل [LICENSE](LICENSE) رو ببینید.

---

## 💬 ارتباط با ما

- **پشتیبانی:** [@SpeedwIT](https://t.me/SpeedwIT)
- **کانال:** [@Speedw_IT](https://t.me/Speedw_IT)
- **گیت‌هاب:** [https://github.com/SpeedwiT](https://github.com/SpeedwiT)

---

<div align="center">

**ساخته شده با ❤️ توسط تیم SpeediT**

⭐ به ما ستاره بدید — انگیزه میده!

</div>
