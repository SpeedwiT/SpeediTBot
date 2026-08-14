"""ماژول تنظیمات - خواندن از فایل toml و متغیرهای محیطی"""

import os
from dataclasses import dataclass, field
from typing import List
from pathlib import Path

import tomllib


@dataclass
class BotConfig:
    token: str = ""
    admin_ids: List[int] = field(default_factory=list)
    webhook_url: str = ""
    use_polling: bool = True


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "proxyman"
    user: str = "proxyman"
    password: str = ""


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0


@dataclass
class AppConfig:
    debug: bool = False
    secret_key: str = "change-me"
    log_level: str = "INFO"


@dataclass
class Settings:
    bot: BotConfig = field(default_factory=BotConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    app: AppConfig = field(default_factory=AppConfig)


def _load_settings() -> Settings:
    config_path = Path(__file__).parent / "settings.toml"
    data = {}
    if config_path.exists():
        with open(config_path, "rb") as f:
            data = tomllib.load(f)

    s = Settings()

    # Bot
    bot = data.get("bot", {})
    s.bot.token = os.getenv("BOT_TOKEN", bot.get("token", ""))
    s.bot.admin_ids = [
        int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    ] or bot.get("admin_ids", [])
    s.bot.webhook_url = os.getenv("WEBHOOK_URL", bot.get("webhook_url", ""))
    s.bot.use_polling = os.getenv("USE_POLLING", "true").lower() == "true"

    # Database
    db = data.get("database", {})
    s.database.host = os.getenv("DB_HOST", db.get("host", "localhost"))
    s.database.port = int(os.getenv("DB_PORT", db.get("port", 5432)))
    s.database.name = os.getenv("DB_NAME", db.get("name", "proxyman"))
    s.database.user = os.getenv("DB_USER", db.get("user", "proxyman"))
    s.database.password = os.getenv("DB_PASSWORD", db.get("password", ""))

    # Redis
    rd = data.get("redis", {})
    s.redis.host = os.getenv("REDIS_HOST", rd.get("host", "localhost"))
    s.redis.port = int(os.getenv("REDIS_PORT", rd.get("port", 6379)))
    s.redis.db = int(os.getenv("REDIS_DB", rd.get("db", 0)))

    # App
    app = data.get("app", {})
    s.app.debug = os.getenv("DEBUG", str(app.get("debug", False))).lower() == "true"
    s.app.secret_key = os.getenv("SECRET_KEY", app.get("secret_key", "change-me"))
    s.app.log_level = os.getenv("LOG_LEVEL", app.get("log_level", "INFO"))

    return s


settings = _load_settings()
