"""ماژول اصلی ربات تلگرام - ProxiMan"""

import logging
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes,
)
from telegram.constants import ParseMode

from config import settings
from database.db import init_db, get_session
from bot.handlers import (
    admin_handler, product_handler, payment_handler,
    panel_handler, user_handler, vps_handler, button_handler,
)
from bot.middlewares.auth import auth_middleware
from bot.middlewares.throttle import throttle_middleware

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.app.log_level),
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """تنظیمات اولیه پس از راه‌اندازی ربات"""
    commands = [
        BotCommand("start", "🏠 صفحه اصلی"),
        BotCommand("admin", "⚙️ پنل مدیریت"),
        BotCommand("panel", "🖥️ اتصال پنل"),
        BotCommand("support", "💬 پشتیبانی"),
        BotCommand("help", "📖 راهنما"),
    ]
    await application.bot.set_my_commands(commands)
    await init_db()
    logger.info("✅ Bot started successfully!")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت خطاها"""
    logger.error(f"Exception while handling update: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )


def main() -> None:
    """نقطه ورود اصلی"""
    app = (
        Application.builder()
        .token(settings.bot.token)
        .post_init(post_init)
        .concurrent_updates(True)
        .build()
    )

    # Middlewares
    app.add_handler(MessageHandler(filters.ALL, auth_middleware), group=-1)
    app.add_handler(MessageHandler(filters.ALL, throttle_middleware), group=-2)

    # Base commands
    app.add_handler(CommandHandler("start", user_handler.start))
    app.add_handler(CommandHandler("help", user_handler.help_command))
    app.add_handler(CommandHandler("admin", admin_handler.admin_panel))

    # Conversation handlers
    app.add_handler(product_handler.get_conversation_handler())
    app.add_handler(panel_handler.get_conversation_handler())
    app.add_handler(payment_handler.get_conversation_handler())
    app.add_handler(vps_handler.get_conversation_handler())
    app.add_handler(button_handler.get_conversation_handler())

    # Callback query handler
    app.add_handler(CallbackQueryHandler(route_callback))

    # Error handler
    app.add_error_handler(error_handler)

    if settings.bot.use_polling:
        logger.info("🔄 Starting in polling mode...")
        app.run_polling(drop_pending_updates=True)
    else:
        logger.info("🌐 Starting in webhook mode...")
        app.run_webhook(
            listen="0.0.0.0",
            port=8443,
            webhook_url=settings.bot.webhook_url,
        )


async def route_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مسیردهی دکمه‌های اینلاین"""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("admin_"):
        await admin_handler.handle_callback(update, context)
    elif data.startswith("product_"):
        await product_handler.handle_callback(update, context)
    elif data.startswith("panel_"):
        await panel_handler.handle_callback(update, context)
    elif data.startswith("pay_"):
        await payment_handler.handle_callback(update, context)
    elif data.startswith("vps_"):
        await vps_handler.handle_callback(update, context)
    elif data.startswith("user_"):
        await user_handler.handle_callback(update, context)
    elif data.startswith("btn_"):
        await button_handler.handle_callback(update, context)
    else:
        await query.edit_message_text("❌ دکمه نامعتبر")


if __name__ == "__main__":
    main()
