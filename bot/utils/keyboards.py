"""کیبوردهای ربات"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class admin_keyboard:
    """کیبوردهای ادمین"""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 داشبورد", callback_data="admin_dashboard"),
                InlineKeyboardButton("🛍️ محصولات", callback_data="admin_products"),
            ],
            [
                InlineKeyboardButton("📂 دسته‌بندی‌ها", callback_data="admin_categories"),
                InlineKeyboardButton("🖥️ پنل‌ها", callback_data="admin_panels"),
            ],
            [
                InlineKeyboardButton("💳 کارت‌های بانکی", callback_data="admin_cards"),
                InlineKeyboardButton("📋 سفارشات", callback_data="admin_orders"),
            ],
            [
                InlineKeyboardButton("💳 پرداخت‌های در انتظار", callback_data="admin_pending_payments"),
                InlineKeyboardButton("🖥️ سفارشات VPS", callback_data="admin_vps_orders"),
            ],
            [
                InlineKeyboardButton("👥 کاربران", callback_data="admin_users"),
                InlineKeyboardButton("📡 کاربران پنل", callback_data="admin_panel_users"),
            ],
            [
                InlineKeyboardButton("👥 ادمین‌ها", callback_data="admin_manage_admins"),
                InlineKeyboardButton("🎫 کد تخفیف", callback_data="admin_discount"),
            ],
            [
                InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings"),
                InlineKeyboardButton("🎨 شخصی‌سازی دکمه‌ها", callback_data="admin_button_customize"),
            ],
        ])


class product_keyboard:
    """کیبوردهای محصولات"""

    @staticmethod
    def menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 لیست محصولات", callback_data="admin_products_list")],
            [InlineKeyboardButton("➕ افزودن محصول", callback_data="admin_add_product")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
        ])


class panel_keyboard:
    """کیبوردهای پنل‌ها"""

    @staticmethod
    def menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ افزودن پنل", callback_data="admin_add_panel")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
        ])
