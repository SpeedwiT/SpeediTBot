"""هندلرهای ادمین - مدیریت کامل از داخل ربات"""

import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.settings import settings
from database.db import get_session
from database.models import (
    User, Product, Category, Panel, BankCard, Order,
    OrderStatus, PanelType, VPSOrder,
)
from bot.utils.keyboards import admin_keyboard, product_keyboard, panel_keyboard
from bot.utils.helpers import is_admin, format_price, format_date
from bot.handlers import button_handler


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش پنل اصلی ادمین"""
    user_id = update.effective_user.id
    if user_id not in settings.bot.admin_ids:
        await update.message.reply_text("⛔ شما دسترسی ادمین ندارید.")
        return

    await update.message.reply_text(
        "⚙️ **پنل مدیریت ProxiMan**\n\n"
        "از دکمه‌های زیر برای مدیریت استفاده کنید:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_keyboard.main_menu(),
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های ادمین"""
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id

    if user_id not in settings.bot.admin_ids:
        await query.answer("⛔ دسترسی ندارید!", show_alert=True)
        return

    # Dashboard
    if data == "admin_dashboard":
        await show_dashboard(update, context)

    # Product management
    elif data == "admin_products":
        await product_menu(update, context)
    elif data == "admin_products_list":
        await products_list(update, context)
    elif data == "admin_add_product":
        await add_product_start(update, context)

    # Category management
    elif data == "admin_categories":
        await categories_menu(update, context)
    elif data == "admin_add_category":
        await add_category_start(update, context)

    # Panel management
    elif data == "admin_panels":
        await panels_menu(update, context)
    elif data == "admin_add_panel":
        await add_panel_start(update, context)
    elif data.startswith("admin_panel_test_"):
        await test_panel_connection(update, context)

    # Bank card management
    elif data == "admin_cards":
        await cards_menu(update, context)
    elif data == "admin_add_card":
        await add_card_start(update, context)

    # Orders & Transactions
    elif data == "admin_orders":
        await orders_list(update, context)
    elif data == "admin_pending_payments":
        await pending_payments(update, context)

    # VPS management
    elif data == "admin_vps_orders":
        await vps_orders_list(update, context)

    # Admin management
    elif data == "admin_manage_admins":
        await manage_admins(update, context)
    elif data == "admin_discount":
        await discount_menu(update, context)

    # Settings
    elif data == "admin_settings":
        await bot_settings(update, context)

    # User management
    elif data == "admin_users":
        await users_list(update, context)
    elif data == "admin_panel_users":
        await panel_users_list(update, context)


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش داشبورد آماری جامع"""
    session = await get_session().__anext__()

    total_users = await session.query(User).count()
    total_orders = await session.query(Order).count()
    pending_orders = await session.query(Order).filter(
        Order.status == OrderStatus.PENDING
    ).count()
    total_products = await session.query(Product).count()
    active_panels = await session.query(Panel).filter(
        Panel.is_active == True
    ).count()
    
    # Panel stats
    total_admins = 0
    total_panel_clients = 0
    active_panel_clients = 0
    panels_info = await session.query(Panel).filter(Panel.is_active == True).all()
    
    for panel in panels_info:
        try:
            if panel.panel_type.value == "hm_panel":
                from api.bridges import get_hm_bridge
                bridge = get_hm_bridge(panel)
                stats = await bridge.get_dashboard_stats()
                await bridge.close()
                if stats and not stats.get("error"):
                    total_admins += stats.get("totalAdmins", 0)
                    total_panel_clients += stats.get("totalClients", 0)
                    active_panel_clients += stats.get("activeClients", 0)
            elif panel.panel_type.value == "marzban":
                from api.bridges import get_bridge
                bridge = get_bridge(panel)
                stats = await bridge.get_system_stats()
                await bridge.close()
                if stats:
                    total_panel_clients += stats.get("users", 0)
                    active_panel_clients += stats.get("active_users", 0)
        except Exception:
            pass

    text = (
        "📊 **داشبورد جامع مدیریت**\n\n"
        "─── 📊 ربات ───\n"
        f"👥 کاربران ربات: `{total_users}`\n"
        f"📦 سفارشات: `{total_orders}`\n"
        f"⏳ در انتظار: `{pending_orders}`\n"
        f"🛍️ محصولات: `{total_products}`\n"
        f"🖥️ پنل‌های فعال: `{active_panels}`\n\n"
        "─── 📊 پنل‌ها ───\n"
        f"👤 ادمین‌های پنل: `{total_admins}`\n"
        f"👥 کلاینت‌های پنل: `{total_panel_clients}`\n"
        f"🟢 کلاینت فعال: `{active_panel_clients}`\n"
        f"🔴 کلاینت غیرفعال: `{total_panel_clients - active_panel_clients}`\n\n"
        f"📅 تاریخ: `{format_date(datetime.utcnow())}`"
    )

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_keyboard.main_menu()
    )


async def product_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی مدیریت محصولات"""
    await update.callback_query.edit_message_text(
        "🛍️ **مدیریت محصولات**\n\n"
        "محصول جدید اضافه کنید یا محصولات موجود را مدیریت کنید:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=product_keyboard.menu()
    )


async def products_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """لیست محصولات"""
    session = await get_session().__anext__()
    products = await session.query(Product).filter(Product.is_active == True).all()

    text = "📋 **لیست محصولات:**\n\n"
    keyboard = []

    for p in products:
        status_emoji = "🟢" if p.is_active else "🔴"
        text += (
            f"{status_emoji} **{p.name}**\n"
            f"   💰 {format_price(p.price)} | 📅 {p.duration_days} روز\n"
            f"   📊 {p.traffic_gb} گیگ | 👥 {p.max_connections} کاربر\n\n"
        )
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {p.name}", callback_data=f"admin_edit_product_{p.id}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_products")])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع افزودن محصول جدید"""
    await update.callback_query.edit_message_text(
        "➕ **افزودن محصول جدید**\n\n"
        "لطفاً اطلاعات محصول را ارسال کنید:\n\n"
        "فرمت: `نام|قیمت|روز|گیگ|اتصال|نوع پنل`\n\n"
        "مثال: `وی‌پی۱ ماهه|150000|30|50|2|sanaei`",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["admin_state"] = "add_product"


async def categories_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی دسته‌بندی‌ها"""
    session = await get_session().__anext__()
    categories = await session.query(Category).filter(Category.is_active == True).all()

    text = "📂 **دسته‌بندی‌ها:**\n\n"
    keyboard = []

    for cat in categories:
        text += f"{cat.icon} **{cat.name}** ({len(cat.products)} محصول)\n"
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ {cat.name}", callback_data=f"admin_edit_category_{cat.id}"
            )
        ])

    keyboard.extend([
        [InlineKeyboardButton("➕ افزودن دسته‌بندی", callback_data="admin_add_category")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع افزودن دسته‌بندی"""
    await update.callback_query.edit_message_text(
        "➕ **افزودن دسته‌بندی جدید**\n\n"
        "لطفاً اطلاعات را ارسال کنید:\n"
        "فرمت: `نام|آیکون|توضیحات`\n\n"
        "مثال: `سرور اروپا|🇩🇪|سرورهای واقع در اروپا`",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["admin_state"] = "add_category"


async def panels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی مدیریت پنل‌ها"""
    session = await get_session().__anext__()
    panels = await session.query(Panel).all()

    text = "🖥️ **پنل‌های متصل:**\n\n"
    keyboard = []

    for panel in panels:
        status = "🟢" if panel.is_active else "🔴"
        text += (
            f"{status} **{panel.name}**\n"
            f"   📍 `{panel.host}:{panel.port}`\n"
            f"   🔧 {panel.panel_type.value}\n\n"
        )
        keyboard.append([
            InlineKeyboardButton(
                f"🔌 تست {panel.name}", callback_data=f"admin_panel_test_{panel.id}"
            )
        ])

    keyboard.extend([
        [InlineKeyboardButton("➕ افزودن پنل", callback_data="admin_add_panel")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_panel_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع افزودن پنل جدید"""
    await update.callback_query.edit_message_text(
        "➕ **افزودن پنل جدید**\n\n"
        "لطفاً اطلاعات پنل را ارسال کنید:\n"
        "فرمت: `نام|نوع|هاست|پورت|یوزر|پسورد`\n\n"
        "انواع: sanaei, marzban, pasarGuard, rebecca, hm_panel\n"
        "مثال: `پنل تست|marzban|192.168.1.1|8080|admin|mypass`",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["admin_state"] = "add_panel"


async def test_panel_connection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تست اتصال به پنل"""
    panel_id = int(update.callback_query.data.split("_")[-1])
    session = await get_session().__anext__()
    panel = await session.query(Panel).filter(Panel.id == panel_id).first()

    if not panel:
        await update.callback_query.answer("❌ پنل یافت نشد!", show_alert=True)
        return

    # Import bridge dynamically
    from api.bridges import get_bridge
    bridge = get_bridge(panel)
    result = await bridge.test_connection()

    if result["success"]:
        await update.callback_query.answer(
            f"✅ اتصال موفق! ({result.get('latency', 'N/A')}ms)",
            show_alert=True,
        )
    else:
        await update.callback_query.answer(
            f"❌ اتصال ناموفق: {result.get('error', 'Unknown error')}",
            show_alert=True,
        )


async def cards_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی مدیریت کارت‌های بانکی"""
    session = await get_session().__anext__()
    cards = await session.query(BankCard).filter(BankCard.is_active == True).all()

    text = "💳 **کارت‌های بانکی:**\n\n"
    keyboard = []

    for card in cards:
        text += (
            f"🏦 **{card.bank_name or 'بانک'}**\n"
            f"   💳 `{card.card_number}`\n"
            f"   👤 {card.card_holder}\n\n"
        )
        keyboard.append([
            InlineKeyboardButton(
                f"🗑️ حذف {card.card_number[-4:]}", callback_data=f"admin_delete_card_{card.id}"
            )
        ])

    keyboard.extend([
        [InlineKeyboardButton("➕ افزودن کارت", callback_data="admin_add_card")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع افزودن کارت بانکی"""
    await update.callback_query.edit_message_text(
        "➕ **افزودن کارت بانکی**\n\n"
        "لطفاً اطلاعات کارت را ارسال کنید:\n"
        "فرمت: `شماره کارت|نام دارنده|نام بانک`\n\n"
        "مثال: `6037991234567890|علی محمدی|ملی`",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["admin_state"] = "add_card"


async def orders_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """لیست سفارشات"""
    session = await get_session().__anext__()
    orders = await session.query(Order).order_by(Order.created_at.desc()).limit(20).all()

    text = "📋 **آخرین سفارشات:**\n\n"

    for order in orders:
        status_emoji = {
            OrderStatus.PENDING: "⏳",
            OrderStatus.PAID: "✅",
            OrderStatus.PROCESSING: "🔄",
            OrderStatus.COMPLETED: "📦",
            OrderStatus.CANCELLED: "❌",
            OrderStatus.REJECTED: "🚫",
        }.get(order.status, "❓")

        text += (
            f"{status_emoji} **سفارش #{order.id}**\n"
            f"   💰 {format_price(order.amount)} | 📊 {order.status.value}\n"
            f"   📅 {format_date(order.created_at)}\n\n"
        )

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")]
        ])
    )


async def pending_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پرداخت‌های در انتظار تایید"""
    session = await get_session().__anext__()
    from database.models import Transaction
    transactions = await session.query(Transaction).filter(
        Transaction.status == OrderStatus.PENDING
    ).all()

    if not transactions:
        await update.callback_query.edit_message_text(
            "✅ هیچ پرداخت در انتظاری وجود ندارد.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")]
            ])
        )
        return

    for tx in transactions:
        user = await session.query(User).filter(User.id == tx.user_id).first()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ تایید", callback_data=f"admin_verify_tx_{tx.id}"),
                InlineKeyboardButton("❌ رد", callback_data=f"admin_reject_tx_{tx.id}"),
            ]
        ])

        text = (
            f"💳 **پرداخت جدید**\n\n"
            f"👤 کاربر: @{user.username or 'بدون یوزر'} (`{user.telegram_id}`)\n"
            f"💰 مبلغ: {format_price(tx.amount)}\n"
            f"📅 تاریخ: {format_date(tx.created_at)}"
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )

    await update.callback_query.message.reply_text("👆 پرداخت‌های در انتظار بالا نمایش داده شد.")


async def vps_orders_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """لیست سفارشات VPS"""
    session = await get_session().__anext__()
    vps_orders = await session.query(VPSOrder).filter(
        VPSOrder.status == OrderStatus.PENDING
    ).all()

    if not vps_orders:
        await update.callback_query.edit_message_text(
            "✅ سفارش VPS در انتظاری وجود ندارد.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")]
            ])
        )
        return

    text = "🖥️ **سفارشات VPS در انتظار:**\n\n"
    for vps in vps_orders:
        text += (
            f"🖥️ **VPS #{vps.id}**\n"
            f"   💻 {vps.cpu or 'N/A'} CPU | 🧠 {vps.ram or 'N/A'} RAM\n"
            f"   💾 {vps.disk or 'N/A'} Disk | 🐧 {vps.os}\n"
            f"   📅 {format_date(vps.created_at)}\n\n"
        )

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")]
        ])
    )


async def manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت ادمین‌ها"""
    admins = settings.bot.admin_ids
    text = "👥 **لیست ادمین‌ها:**\n\n"
    for admin_id in admins:
        text += f"• `{admin_id}`\n"

    text += "\nبرای افزودن ادمین جدید، آیدی عددی را ارسال کنید:"
    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["admin_state"] = "add_admin"


async def bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تنظیمات ربات"""
    text = (
        "⚙️ **تنظیمات ربات**\n\n"
        f"🔑 Token: `{settings.bot.token[:10]}...`\n"
        f"🌐 Webhook: `{settings.bot.webhook_url or 'غیرفعال'}`\n"
        f"🔄 Polling: `{settings.bot.use_polling}`\n"
        f"📊 Debug: `{settings.app.debug}`\n"
        f"📝 Log Level: `{settings.app.log_level}`"
    )
    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")]
        ])
    )


async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """لیست کاربران"""
    session = await get_session().__anext__()
    users = await session.query(User).order_by(User.created_at.desc()).limit(50).all()

    text = "👥 **لیست کاربران:**\n\n"
    for user in users:
        status = "🟢" if user.is_active and not user.is_banned else "🔴"
        text += (
            f"{status} @{user.username or 'بدون یوزر'} (`{user.telegram_id}`)\n"
            f"   💰 موجودی: {format_price(user.balance)}\n"
            f"   📅 عضویت: {format_date(user.created_at)}\n\n"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 کاربران پنل", callback_data="admin_panel_users")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def panel_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """لیست کاربران متصل به پنل‌ها"""
    session = await get_session().__anext__()
    panels = await session.query(Panel).filter(Panel.is_active == True).all()

    if not panels:
        await update.callback_query.edit_message_text(
            "❌ هیچ پنل فعالی وجود ندارد.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
            ]),
        )
        return

    text = "📡 **کاربران پنل‌ها:**\n\n"

    for panel in panels:
        text += f"─── 🖥️ **{panel.name}** ({panel.panel_type.value}) ───\n"
        
        try:
            if panel.panel_type.value == "hm_panel":
                from api.bridges import get_hm_bridge
                bridge = get_hm_bridge(panel)
                result = await bridge.get_clients()
                await bridge.close()
                
                if result and not result.get("error"):
                    clients = result.get("clients", result.get("data", []))
                    if isinstance(clients, list):
                        text += f"   👥 تعداد کاربران: {len(clients)}\n"
                        for client in clients[:10]:  # Show first 10
                            status = "🟢" if client.get("enable", True) else "🔴"
                            username = client.get("username", client.get("subId", "unknown"))
                            text += f"   {status} {username}\n"
                        if len(clients) > 10:
                            text += f"   ... و {len(clients) - 10} نفر دیگر\n"
                    else:
                        text += f"   👥 تعداد کاربران: {result.get('total', 'نامشخص')}\n"
                else:
                    text += f"   ❌ خطا در دریافت اطلاعات\n"
            elif panel.panel_type.value == "marzban":
                from api.bridges import get_bridge
                bridge = get_bridge(panel)
                stats = await bridge.get_system_stats()
                await bridge.close()
                text += f"   👥 تعداد کاربران: {stats.get('users', 'نامشخص')}\n"
            else:
                text += f"   ℹ️ این نوع پنل پشتیبانی نشده\n"
        except Exception as e:
            text += f"   ❌ خطا: {str(e)[:50]}\n"
        
        text += "\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_panel_users")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def discount_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی مدیریت کدهای تخفیف"""
    from database.models import DiscountCode
    session = await get_session().__anext__()
    codes = await session.query(DiscountCode).order_by(DiscountCode.created_at.desc()).limit(20).all()

    text = "🎫 **کدهای تخفیف:**\n\n"
    keyboard = []

    for code in codes:
        status = "🟢" if code.is_active and not code.is_expired else "🔴"
        text += (
            f"{status} **{code.code}**\n"
            f"   💰 تخفیف: {code.discount_percent}%\n"
            f"   📊 استفاده: {code.used_count}/{code.max_uses}\n"
            f"   📅 انقضا: {format_date(code.expire_at)}\n\n"
        )

    keyboard.extend([
        [InlineKeyboardButton("➕ ایجاد کد تخفیف", callback_data="admin_add_discount")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def create_admin_on_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ساخت ادمین در پنل مستقیماً از ربات"""
    session = await get_session().__anext__()
    panels = await session.query(Panel).filter(
        Panel.is_active == True,
        Panel.panel_type == PanelType.HM_PANEL
    ).all()

    if not panels:
        await update.callback_query.edit_message_text(
            "❌ هیچ پنل HM Panel فعالی وجود ندارد.\n"
            "ابتدا پنل HM Panel را اضافه کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
            ]),
        )
        return

    text = "👤 **ساخت ادمین در پنل**\n\n"
    text += "لطفاً اطلاعات ادمین را ارسال کنید:\n"
    text += "فرمت: `نام کاربری|رمز عبور|ایمیل|حداکثر کاربران|حداکثر ترافیک(GB)|روز انقضا`\n\n"
    text += "مثال: `admin1|pass123|admin@test.com|100|50|30`"

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["admin_state"] = "create_panel_admin"


async def handle_create_panel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پردازش ساخت ادمین پنل"""
    session = await get_session().__anext__()
    
    text = update.message.text.strip().split("|")
    if len(text) < 6:
        await update.message.reply_text("❌ فرمت نامعتبر. دوباره وارد کنید:")
        return

    username, password, email, max_clients, max_traffic, expire_days = [x.strip() for x in text]
    
    panels = await session.query(Panel).filter(
        Panel.is_active == True,
        Panel.panel_type == PanelType.HM_PANEL
    ).all()

    if not panels:
        await update.message.reply_text("❌ پنلی یافت نشد.")
        return

    panel = panels[0]  # Use first active HM Panel
    
    try:
        from api.bridges import get_hm_bridge
        import time
        bridge = get_hm_bridge(panel)
        
        admin_data = {
            "username": username,
            "password": password,
            "email": email,
            "role": "admin",
            "maxClients": int(max_clients),
            "maxTraffic": int(max_traffic),
            "expireAt": int(time.time()) + (int(expire_days) * 86400),
            "isActive": True,
        }
        
        result = await bridge.create_admin(admin_data)
        await bridge.close()
        
        if result and not result.get("error"):
            await update.message.reply_text(
                f"✅ ادمین **{username}** با موفقیت در پنل ساخته شد!\n\n"
                f"👤 نام کاربری: `{username}`\n"
                f"📧 ایمیل: {email}\n"
                f"👥 حداکثر کاربران: {max_clients}\n"
                f"📊 حداکثر ترافیک: {max_traffic} GB",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text(
                f"❌ خطا در ساخت ادمین: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

    context.user_data.pop("admin_state", None)
