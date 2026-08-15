"""هندلرهای پنل - مدیریت و اتصال به پنل‌های VPN"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters,
)
from telegram.constants import ParseMode

from database.db import get_session
from database.models import Panel, PanelType
from bot.utils.helpers import format_price


# Conversation states
(NAME, HOST, PORT, USERNAME, PASSWORD, API_TOKEN) = range(6)


def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(add_panel_start, pattern="^admin_add_panel$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_panel_name)],
            HOST: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_panel_host)],
            PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_panel_port)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_panel_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_panel_password)],
            API_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_panel_token)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )


async def add_panel_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.edit_message_text(
        "➕ **افزودن پنل جدید**\n\n"
        "لطفاً نام پنل را ارسال کنید:\n"
        "مثال: `پنل اصلی آلمان`",
        parse_mode=ParseMode.MARKDOWN,
    )
    return NAME


async def add_panel_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["panel_name"] = update.message.text
    await update.message.reply_text(
        "✅ نام ثبت شد.\n\n"
        "🌐 لطفاً هاست (آیپی یا دامنه) را ارسال کنید:",
    )
    return HOST


async def add_panel_host(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["panel_host"] = update.message.text
    await update.message.reply_text(
        "✅ هاست ثبت شد.\n\n"
        "🔌 لطفاً پورت را ارسال کنید:",
    )
    return PORT


async def add_panel_port(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        port = int(update.message.text)
        context.user_data["panel_port"] = port
        await update.message.reply_text(
            "✅ پورت ثبت شد.\n\n"
            "👤 لطفاً نام کاربری ادمین را ارسال کنید:",
        )
        return USERNAME
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return PORT


async def add_panel_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["panel_username"] = update.message.text
    await update.message.reply_text(
        "✅ نام کاربری ثبت شد.\n\n"
        "🔒 لطفاً رمز عبور را ارسال کنید:",
    )
    return PASSWORD


async def add_panel_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["panel_password"] = update.message.text
    await update.message.reply_text(
        "✅ رمز عبور ثبت شد.\n\n"
        "🔑 لطفاً API Token را ارسال کنید (اگر نیاز نیست skip بزنید):",
    )
    return API_TOKEN


async def add_panel_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    session = await get_session().__anext__()

    panel_type_str = context.user_data.get("panel_type", "marzban")
    panel = Panel(
        name=context.user_data["panel_name"],
        panel_type=PanelType(panel_type_str),
        host=context.user_data["panel_host"],
        port=context.user_data["panel_port"],
        username=context.user_data["panel_username"],
        password=context.user_data["panel_password"],
        api_token=update.message.text if update.message.text.lower() != "skip" else None,
    )
    session.add(panel)
    await session.commit()

    await update.message.reply_text(
        f"✅ پنل جدید با موفقیت اضافه شد!\n\n"
        f"🖥️ نام: **{panel.name}**\n"
        f"📍 هاست: `{panel.host}:{panel.port}`\n"
        f"🔧 نوع: **{panel.panel_type.value}**",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های پنل"""
    query = update.callback_query
    data = query.data

    if data.startswith("admin_panel_test_"):
        panel_id = int(data.split("_")[-1])
        await test_connection(update, context, panel_id)


async def test_connection(update: Update, context: ContextTypes.DEFAULT_TYPE, panel_id: int) -> None:
    """تست اتصال به پنل"""
    session = await get_session().__anext__()
    panel = await session.query(Panel).filter(Panel.id == panel_id).first()

    if not panel:
        await update.callback_query.answer("❌ پنل یافت نشد!", show_alert=True)
        return

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
            f"❌ اتصال ناموفق: {result.get('error', 'Unknown')}",
            show_alert=True,
        )


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END
