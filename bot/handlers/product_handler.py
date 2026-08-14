"""هندلرهای محصولات - مدیریت و خرید"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters,
)
from telegram.constants import ParseMode

from database.db import get_session
from database.models import Product, Category, Order, OrderStatus, User, PanelType
from bot.utils.helpers import format_price


# Conversation states
(NAME, PRICE, DURATION, TRAFFIC, CONNECTIONS, PANEL_TYPE, CATEGORY) = range(7)


async def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_product_start, pattern="^admin_add_product$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_duration)],
            TRAFFIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_traffic)],
            CONNECTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_connections)],
            PANEL_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_panel_type)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_category)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.edit_message_text(
        "➕ **افزودن محصول جدید**\n\n"
        "لطفاً نام محصول را ارسال کنید:\n"
        "مثال: `وی‌پی یک ماهه اروپا`",
        parse_mode=ParseMode.MARKDOWN,
    )
    return NAME


async def add_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["product_name"] = update.message.text
    await update.message.reply_text(
        "✅ نام ثبت شد.\n\n"
        "💰 لطفاً قیمت (تومان) را ارسال کنید:",
        parse_mode=ParseMode.MARKDOWN,
    )
    return PRICE


async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        price = float(update.message.text.replace(",", ""))
        context.user_data["product_price"] = price
        await update.message.reply_text(
            "✅ قیمت ثبت شد.\n\n"
            "📅 مدت زمان (روز) را ارسال کنید:",
        )
        return DURATION
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return PRICE


async def add_product_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        days = int(update.message.text)
        context.user_data["product_duration"] = days
        await update.message.reply_text(
            "✅ مدت زمان ثبت شد.\n\n"
            "📊 حجم (گیگابایت) را ارسال کنید:",
        )
        return TRAFFIC
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return DURATION


async def add_product_traffic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        traffic = float(update.message.text)
        context.user_data["product_traffic"] = traffic
        await update.message.reply_text(
            "✅ حجم ثبت شد.\n\n"
            "👥 حداکثر تعداد اتصال همزمان را ارسال کنید:",
        )
        return CONNECTIONS
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return TRAFFIC


async def add_product_connections(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        conns = int(update.message.text)
        context.user_data["product_connections"] = conns
        await update.message.reply_text(
            "✅ اتصال ثبت شد.\n\n"
            "🔧 نوع پنل را ارسال کنید:\n"
            "sanaei | marzban | pasarguard | rebecca | hm_panel",
        )
        return PANEL_TYPE
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return CONNECTIONS


async def add_product_panel_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    panel_type_str = update.message.text.lower().strip()
    try:
        panel_type = PanelType(panel_type_str)
        context.user_data["product_panel_type"] = panel_type
        await update.message.reply_text(
            "✅ نوع پنل ثبت شد.\n\n"
            "📂 آیدی دسته‌بندی را ارسال کنید:",
        )
        return CATEGORY
    except ValueError:
        await update.message.reply_text(
            "❌ نوع پنل نامعتبر. لطفاً یکی از موارد زیر را وارد کنید:\n"
            "sanaei | marzban | pasarguard | rebecca | hm_panel",
        )
        return PANEL_TYPE


async def add_product_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        category_id = int(update.message.text)
        session = await get_session().__anext__()

        category = await session.query(Category).filter(Category.id == category_id).first()
        if not category:
            await update.message.reply_text("❌ دسته‌بندی یافت نشد. دوباره وارد کنید:")
            return CATEGORY

        product = Product(
            name=context.user_data["product_name"],
            price=context.user_data["product_price"],
            duration_days=context.user_data["product_duration"],
            traffic_gb=context.user_data["product_traffic"],
            max_connections=context.user_data["product_connections"],
            panel_type=context.user_data["product_panel_type"],
            category_id=category_id,
        )
        session.add(product)
        await session.commit()

        await update.message.reply_text(
            f"✅ محصول جدید با موفقیت اضافه شد!\n\n"
            f"📦 نام: **{product.name}**\n"
            f"💰 قیمت: **{format_price(product.price)}**\n"
            f"📅 مدت: **{product.duration_days} روز**\n"
            f"📊 حجم: **{product.traffic_gb} گیگ**\n"
            f"👥 اتصال: **{product.max_connections} کاربر**",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return CATEGORY


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های محصولات"""
    query = update.callback_query
    data = query.data

    if data.startswith("admin_edit_product_"):
        product_id = int(data.split("_")[-1])
        await edit_product_menu(update, context, product_id)


async def edit_product_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int) -> None:
    """منوی ویرایش محصول"""
    session = await get_session().__anext__()
    product = await session.query(Product).filter(Product.id == product_id).first()

    if not product:
        await update.callback_query.answer("❌ محصول یافت نشد!", show_alert=True)
        return

    text = (
        f"✏️ **ویرایش محصول**\n\n"
        f"📦 نام: **{product.name}**\n"
        f"💰 قیمت: **{format_price(product.price)}**\n"
        f"📅 مدت: **{product.duration_days} روز**\n"
        f"📊 حجم: **{product.traffic_gb} گیگ**\n"
        f"👥 اتصال: **{product.max_connections} کاربر**\n"
        f"🔧 پنل: **{product.panel_type.value}**\n"
        f"🟢 وضعیت: **{'فعال' if product.is_active else 'غیرفعال'}**"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ ویرایش نام", callback_data=f"edit_product_name_{product_id}")],
        [InlineKeyboardButton("💰 ویرایش قیمت", callback_data=f"edit_product_price_{product_id}")],
        [InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_product_{product_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_products_list")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard,
    )
