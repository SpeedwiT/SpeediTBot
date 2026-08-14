"""مدیریت شخصی‌سازی دکمه‌ها - ایموجی و رنگ"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ButtonColor(str, Enum):
    """رنگ‌های پشتیبانی شده دکمه‌های تلگرام"""
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    GRAY = "gray"
    WHITE = "white"


class ButtonStyle(str, Enum):
    """استایل دکمه‌ها"""
    DEFAULT = "default"
    PRIMARY = "primary"       # آبی پررنگ
    SECONDARY = "secondary"   # خاکستری
    SUCCESS = "success"       # سبز
    DANGER = "danger"         # قرمز
    LINK = "link"


# Map button colors to emoji indicators for visual identification
COLOR_EMOJI_MAP: Dict[ButtonColor, str] = {
    ButtonColor.BLUE: "🔵",
    ButtonColor.GREEN: "🟢",
    ButtonColor.RED: "🔴",
    ButtonColor.GRAY: "⚪",
    ButtonColor.WHITE: "⬜",
}


@dataclass
class ButtonConfig:
    """تنظیمات یک دکمه"""
    text: str = ""
    callback_data: str = ""
    url: Optional[str] = None
    emoji: Optional[str] = None           # Premium emoji placeholder ID
    emoji_name: Optional[str] = None     # Unicode emoji
    color: ButtonColor = ButtonColor.BLUE
    style: ButtonStyle = ButtonStyle.DEFAULT


@dataclass
class ButtonTheme:
    """تم کامل دکمه‌های ربات"""
    name: str = "پیش‌فرض"
    # Main menu buttons
    main_buttons: List[ButtonConfig] = field(default_factory=list)
    # Product buttons
    product_buttons: List[ButtonConfig] = field(default_factory=list)
    # Payment buttons
    payment_buttons: List[ButtonConfig] = field(default_factory=list)
    # Admin buttons
    admin_buttons: List[ButtonConfig] = field(default_factory=list)
    # Global settings
    default_color: ButtonColor = ButtonColor.BLUE
    default_emoji_set: str = "default"
    use_premium_emojis: bool = False


# ============== Default themes ==============

DEFAULT_THEME = ButtonTheme(
    name="پیش‌فرض",
    main_buttons=[
        ButtonConfig(text="🛍️ خرید کانفیگ", callback_data="user_buy_config", color=ButtonColor.GREEN),
        ButtonConfig(text="🖥️ خرید پنل", callback_data="user_buy_panel", color=ButtonColor.BLUE),
        ButtonConfig(text="💻 سفارش VPS", callback_data="user_buy_vps", color=ButtonColor.BLUE),
        ButtonConfig(text="💳 شارژ کیف پول", callback_data="user_charge", color=ButtonColor.GREEN),
        ButtonConfig(text="📋 سفارشات من", callback_data="user_my_orders", color=ButtonColor.GRAY),
        ButtonConfig(text="👤 پروفایل", callback_data="user_profile", color=ButtonColor.GRAY),
        ButtonConfig(text="💬 پشتیبانی", callback_data="user_support", color=ButtonColor.RED),
    ],
    product_buttons=[
        ButtonConfig(text="🛒 خرید", callback_data="buy_product", color=ButtonColor.GREEN),
        ButtonConfig(text="🔙 بازگشت", callback_data="back", color=ButtonColor.GRAY),
    ],
    payment_buttons=[
        ButtonConfig(text="💳 کارت به کارت", callback_data="pay_card", color=ButtonColor.BLUE),
        ButtonConfig(text="💰 از موجودی", callback_data="pay_balance", color=ButtonColor.GREEN),
        ButtonConfig(text="✅ تایید", callback_data="confirm", color=ButtonColor.GREEN),
        ButtonConfig(text="❌ انصراف", callback_data="cancel", color=ButtonColor.RED),
    ],
    admin_buttons=[
        ButtonConfig(text="📊 داشبورد", callback_data="admin_dashboard", color=ButtonColor.BLUE),
        ButtonConfig(text="🛍️ محصولات", callback_data="admin_products", color=ButtonColor.BLUE),
        ButtonConfig(text="📂 دسته‌بندی‌ها", callback_data="admin_categories", color=ButtonColor.BLUE),
        ButtonConfig(text="🖥️ پنل‌ها", callback_data="admin_panels", color=ButtonColor.BLUE),
        ButtonConfig(text="💳 کارت‌های بانکی", callback_data="admin_cards", color=ButtonColor.BLUE),
        ButtonConfig(text="📋 سفارشات", callback_data="admin_orders", color=ButtonColor.BLUE),
        ButtonConfig(text="✅ تایید", callback_data="admin_verify", color=ButtonColor.GREEN),
        ButtonConfig(text="❌ رد", callback_data="admin_reject", color=ButtonColor.RED),
    ],
)


class ButtonCustomizer:
    """مدیریت شخصی‌سازی دکمه‌ها"""

    def __init__(self):
        self.themes: Dict[str, ButtonTheme] = {
            "default": DEFAULT_THEME,
        }
        self.active_theme: str = "default"
        self.premium_emoji_ids: Dict[str, str] = {}  # name -> emoji_id

    def set_active_theme(self, theme_name: str) -> None:
        """تنظیم تم فعال"""
        if theme_name in self.themes:
            self.active_theme = theme_name

    def get_active_theme(self) -> ButtonTheme:
        """دریافت تم فعال"""
        return self.themes.get(self.active_theme, DEFAULT_THEME)

    def add_theme(self, theme: ButtonTheme) -> None:
        """افزودن تم جدید"""
        self.themes[theme.name] = theme

    def remove_theme(self, theme_name: str) -> None:
        """حذف تم"""
        if theme_name != "default" and theme_name in self.themes:
            del self.themes[theme_name]

    def register_premium_emoji(self, name: str, emoji_id: str) -> None:
        """ثبت ایموجی پرمیوم"""
        self.premium_emoji_ids[name] = emoji_id

    def get_button_text(self, text: str, emoji_name: Optional[str] = None) -> str:
        """تولید متن دکمه با ایموجی"""
        if emoji_name:
            return f"{emoji_name} {text}"
        return text

    def get_admin_buttons(self) -> List[ButtonConfig]:
        """دریافت دکمه‌های ادمین از تم فعال"""
        theme = self.get_active_theme()
        return theme.admin_buttons

    def get_main_buttons(self) -> List[ButtonConfig]:
        """دریافت دکمه‌های اصلی از تم فعال"""
        theme = self.get_active_theme()
        return theme.main_buttons


# Global instance
button_customizer = ButtonCustomizer()
