# راهنمای نصب و راه‌اندازی ProxiMan

## پیش‌نیازها

- سرور مجازی با Ubuntu 20.04+
- حداقل 2GB RAM و 20GB دیسک
- دامنه (Domain) متصل به آیپی سرور
- توکن ربات تلگرام (از @BotFather)

## نصب سریع

```bash
git clone https://github.com/yourusername/proxyman.git
cd proxyman
chmod +x install.sh
sudo ./install.sh
```

## نصب دستی

### 1. نصب Docker و Docker Compose

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. کلون پروژه

```bash
git clone https://github.com/yourusername/proxyman.git /opt/proxyman
cd /opt/proxyman
```

### 3. تنظیمات

```bash
cp .env.example .env
nano .env
```

فایل `.env` را ویرایش کنید:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
DB_PASSWORD=strong_password
REDIS_PASSWORD=strong_password
SECRET_KEY=very_long_random_string
DOMAIN=bot.yourdomain.com
```

### 4. راه‌اندازی

```bash
docker-compose build
docker-compose up -d
```

### 5. تنظیم Nginx و SSL

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d bot.yourdomain.com
```

## پس از نصب

### تنظیم Webhook

در @BotFather دستور `/setwebhook` را بفرستید و آدرس زیر را وارد کنید:

```
https://bot.yourdomain.com/webhook
```

### ورود به پنل ادمین

در ربات دستور `/admin` را بفرستید.

### افزودن کارت بانکی

از پنل ادمین، بخش "کارت‌های بانکی" را انتخاب کنید و کارت خود را اضافه کنید.

### ایجاد دسته‌بندی و محصول

1. از پنل ادمین، بخش "دسته‌بندی‌ها" را انتخاب کنید
2. یک دسته‌بندی جدید ایجاد کنید
3. به بخش "محصولات" بروید و محصول جدید اضافه کنید

## عیب‌یابی

### مشکل: ربات پاسخ نمی‌دهد

```bash
# بررسی لاگ‌ها
docker-compose logs -f bot

# بررسی وضعیت کانتینرها
docker-compose ps
```

### مشکل: خطای دیتابیس

```bash
# ریست دیتابیس
docker-compose down -v
docker-compose up -d
```

### مشکل: اتصال پنل

```bash
# بررسی اتصال
docker-compose exec bot python -c "
from database.models import Panel
from api.bridges import get_bridge
import asyncio

async def test():
    # Test panel connection
    pass

asyncio.run(test())
"
```

## بروزرسانی

```bash
cd /opt/proxyman
git pull
docker-compose build --no-cache
docker-compose up -d
```

## بکاپ

```bash
# بکاپ دیتابیس
docker exec proxyman_db pg_dump -U proxyman proxyman > backup.sql

# بکاپ خودکار (اضافه کردن به crontab)
0 2 * * * cd /opt/proxyman && ./scripts/backup.sh
```
