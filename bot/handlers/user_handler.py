"""هندلرهای کاربران - ثبت‌نام و پروفایل"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.db import get_session
from database.models import User, UserRole, Order, OrderStatus
from bot.utils.helpers import format_price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع کار با ربات"""
    session = await get_session().__anext__()

    user = await session.query(User).filter(
        User.telegram_id == update.effective_user.id
    ).first()

    if not user:
        user = User(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            full_name=update.effective_user.full_name,
            role=UserRole.USER,
        )
        session.add(user)
        await session.commit()

    text = (
        f"👋 **سلام {update.effective_user.first_name}!**\n\n"
        f"به **ProxiMan** خوش آمدید.\n"
        f"از طریق این ربات می‌توانید:\n"
        f"• کانفیگ VPN خریداری کنید\n"
        f"• پنل نمایندگی تهیه کنید\n"
        f"• سرور مجازی سفارش دهید\n\n"
        f"💰 موجودی شما: **{format_price(user.balance)}**"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛍️ خرید کانفیگ", callback_data="user_buy_config"),
            InlineKeyboardButton("🖥️ خرید پنل", callback_data="user_buy_panel"),
        ],
        [
            InlineKeyboardButton("💻 سفارش VPS", callback_data="user_buy_vps"),
            InlineKeyboardButton("💳 شارژ کیف پول", callback_data="user_charge"),
        ],
        [
            InlineKeyboardButton("📋 سفارشات من", callback_data="user_my_orders"),
            InlineKeyboardButton("👤 پروفایل", callback_data="user_profile"),
        ],
        [
            InlineKeyboardButton("⚙️ مدیریت", callback_data="user_manage"),
            InlineKeyboardButton("💬 پشتیبانی", callback_data="user_support"),
        ],
    ])

    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """راهنمای ربات"""
    text = (
        "📖 **راهنمای ProxiMan**\n\n"
        "🛍️ **خرید کانفیگ:**\n"
        "محصول مورد نظر را انتخاب کنید و پرداخت کنید. کانفیگ بلافاصله تحویل داده می‌شود.\n\n"
        "🖥️ **خرید پنل نمایندگی:**\n"
        "پنل اختصاصی با محدودیت تعیین‌شده دریافت کنید.\n\n"
        "💻 **سفارش VPS:**\n"
        "سرور مجازی اختصاصی سفارش دهید. ادمین سرور را آماده و تحویل می‌دهد.\n\n"
        "💳 **شارژ کیف پول:**\n"
        "از طریق کارت به کارت کیف پول خود را شارژ کنید.\n\n"
        "📱 **پشتیبانی:**\n"
        "در صورت مشکل با پشتیبانی تماس بگیرید."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های کاربران"""
    query = update.callback_query
    data = query.data

    if data == "user_buy_config":
        await show_categories(update, context)
    elif data == "user_buy_panel":
        await show_reseller_products(update, context)
    elif data == "user_buy_vps":
        await start_vps_order(update, context)
    elif data == "user_charge":
        await start_charge(update, context)
    elif data == "user_my_orders":
        await show_my_orders(update, context)
    elif data == "user_profile":
        await show_profile(update, context)
    elif data == "user_support":
        await contact_support(update, context)
    elif data == "user_manage":
        await user_manage_menu(update, context)
    elif data.startswith("buy_product_"):
        await start_purchase(update, context)


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش دسته‌بندی‌ها"""
    session = await get_session().__anext__()
    from database.models import Category
    categories = await session.query(Category).filter(Category.is_active == True).all()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{cat.icon} {cat.name}", callback_data=f"category_{cat.id}"
        )]
        for cat in categories
    ])

    await update.callback_query.edit_message_text(
        "📂 **دسته‌بندی محصولات:**\n\n"
        "لطفاً یک دسته را انتخاب کنید:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def show_reseller_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش محصولات نمایندگی"""
    await update.callback_query.edit_message_text(
        "🖥️ **پنل نمایندگی**\n\n"
        "برای خرید پنل نمایندگی با پشتیبانی تماس بگیرید.\n"
        "ادمین پنل با محدودیت‌های تعیین‌شده برای شما ایجاد می‌کند.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 تماس با پشتیبانی", callback_data="user_support")],
        ]),
    )


async def start_vps_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع سفارش VPS"""
    await update.callback_query.edit_message_text(
        "💻 **سفارش سرور مجازی**\n\n"
        "لطفاً مشخصات مورد نظر را ارسال کنید:\n\n"
        "فرمت: `CPU|RAM|Disk|OS|Location`\n\n"
        "مثال: `2|4GB|50GB|ubuntu-22.04|Germany`",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["user_state"] = "vps_order"


async def start_charge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع شارژ کیف پول"""
    await update.callback_query.edit_message_text(
        "💳 **شارژ کیف پول**\n\n"
        "لطفاً مبلغ (تومان) را وارد کنید:",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["user_state"] = "charge_amount"


async def show_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش سفارشات کاربر"""
    session = await get_session().__anext__()
    user = await session.query(User).filter(
        User.telegram_id == update.effective_user.id
    ).first()

    orders = await session.query(Order).filter(
        Order.user_id == user.id
    ).order_by(Order.created_at.desc()).limit(10).all()

    if not orders:
        await update.callback_query.edit_message_text(
            "📋 شما هیچ سفارشی ندارید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ خرید کانفیگ", callback_data="user_buy_config")],
            ]),
        )
        return

    text = "📋 **سفارشات شما:**\n\n"
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
        )
        if order.subscription_link:
            text += f"   🔗 لینک سابسکریپشن ارسال شد\n"
        text += "\n"

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="user_profile")],
        ]),
    )


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش پروفایل"""
    session = await get_session().__anext__()
    user = await session.query(User).filter(
        User.telegram_id == update.effective_user.id
    ).first()

    text = (
        f"👤 **پروفایل شما**\n\n"
        f"🆔 آیدی: `{user.telegram_id}`\n"
        f"👤 نام: **{user.full_name or 'ثبت نشده'}**\n"
        f"📛 یوزرنیم: @{user.username or 'ندارید'}\n"
        f"💰 موجودی: **{format_price(user.balance)}**\n"
        f"📅 عضویت: {user.created_at.strftime('%Y-%m-%d')}"
    )

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 شارژ کیف پول", callback_data="user_charge")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="user_profile")],
        ]),
    )


async def contact_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تماس با پشتیبانی"""
    await update.callback_query.edit_message_text(
        "💬 **پشتیبانی**\n\n"
        "برای ارتباط با پشتیبانی می‌توانید:\n"
        "• پیام خود را همین‌جا ارسال کنید\n"
        "• به آیدی پشتیبانی پیام دهید\n\n"
        "لطفاً پیام خود را ارسال کنید:",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["user_state"] = "support_message"


async def user_manage_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی مدیریت کاربر - دسترسی به پنل ادمین"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id not in settings.bot.admin_ids:
        await update.callback_query.edit_message_text(
            "⛔ شما دسترسی ادمین ندارید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="user_profile")],
            ]),
        )
        return

    # Show admin panel directly
    from bot.handlers.admin_handler import admin_panel
    await admin_panel(update, context)


async def start_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع خرید محصول"""
    product_id = int(update.callback_query.data.split("_")[-1])
    session = await get_session().__anext__()
    from database.models import Product
    product = await session.query(Product).filter(Product.id == product_id).first()

    if not product:
        await update.callback_query.answer("❌ محصول یافت نشد!", show_alert=True)
        return

    text = (
        f"🛍️ **خرید محصول**\n\n"
        f"📦 نام: **{product.name}**\n"
        f"💰 قیمت: **{format_price(product.price)}**\n"
        f"📅 مدت: **{product.duration_days} روز**\n"
        f"📊 حجم: **{product.traffic_gb} گیگ**\n"
        f"👥 اتصال: **{product.max_connections} کاربر**\n\n"
        "نحوه پرداخت را انتخاب کنید:"
    )

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💳 کارت به کارت", callback_data=f"pay_card_{product_id}"),
                InlineKeyboardButton("💰 از موجودی", callback_data=f"pay_balance_{product_id}"),
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data=f"category_{product.category_id}")],
        ]),
    )
