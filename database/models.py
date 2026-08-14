"""مدل‌های دیتابیس - SQLAlchemy"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, Enum, BigInteger, JSON,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
import enum

from config.settings import settings


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    RESELLER = "reseller"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PanelType(str, enum.Enum):
    SANAEI = "sanaei"
    MARZBAN = "marzban"
    PASARGAD = "pasargad"
    REBECCA = "rebecca"
    HM_PANEL = "hm_panel"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="📦")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)  # مدت روز
    traffic_gb = Column(Float, nullable=False)  # حجم گیگابایت
    max_connections = Column(Integer, default=1)
    panel_type = Column(Enum(PanelType), nullable=False)
    panel_id = Column(Integer, ForeignKey("panels.id"), nullable=True)
    config_template = Column(JSON, nullable=True)  # تنظیمات اضافی
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    orders = relationship("Order", back_populates="product")


class Panel(Base):
    __tablename__ = "panels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    panel_type = Column(Enum(PanelType), nullable=False)
    host = Column(String(200), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(200), nullable=False)
    api_token = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    extra_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="panel")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    order_type = Column(String(50), nullable=False)  # config, reseller, vps
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    amount = Column(Float, nullable=False)
    config_data = Column(JSON, nullable=True)  # اطلاعات کانفیگ ساخته شده
    uuid = Column(String(100), nullable=True)
    subscription_link = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")


class BankCard(Base):
    __tablename__ = "bank_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(String(16), nullable=False)
    card_holder = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    max_amount = Column(Float, nullable=True)  # محدودیت مبلغ
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    bank_card_id = Column(Integer, ForeignKey("bank_cards.id"), nullable=True)
    amount = Column(Float, nullable=False)
    receipt_photo_id = Column(String(200), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])


class VPSOrder(Base):
    __tablename__ = "vps_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    server_ip = Column(String(45), nullable=True)
    server_port = Column(Integer, default=22)
    ssh_user = Column(String(50), nullable=True)
    ssh_password = Column(String(200), nullable=True)
    os = Column(String(50), default="ubuntu-22.04")
    cpu = Column(String(20), nullable=True)
    ram = Column(String(20), nullable=True)
    disk = Column(String(20), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DiscountCode(Base):
    """کدهای تخفیف"""
    __tablename__ = "discount_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percent = Column(Float, nullable=False)  # درصد تخفیف
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    expire_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_expired(self):
        if self.expire_at:
            return datetime.utcnow() > self.expire_at
        return False


class ButtonTheme(Base):
    """تم‌های دکمه‌ها"""
    __tablename__ = "button_themes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    # JSON structure for theme data
    theme_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PremiumEmoji(Base):
    """ایموجی‌های پرمیوم تلگرام"""
    __tablename__ = "premium_emojis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    emoji_id = Column(String(100), nullable=False)  # Telegram premium emoji ID
    unicode_emoji = Column(String(10), nullable=True)
    category = Column(String(50), default="general")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPreference(Base):
    """تنظیمات شخصی کاربر"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme_name = Column(String(100), default="default")
    language = Column(String(10), default="fa")
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database engine & session
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}"
    f"@{settings.database.host}:{settings.database.port}/{settings.database.name}"
)

engine = create_async_engine(DATABASE_URL, echo=settings.app.debug)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """ایجاد جداول دیتابیس"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
