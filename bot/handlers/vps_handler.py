"""هندلرهای VPS - سفارش و تحویل سرور مجازی"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters,
)
from telegram.constants import ParseMode

from database.db import get_session
from database.models import VPSOrder, Order, OrderStatus, User
from bot.utils.helpers import format_price


# Conversation states
(SPECIFY_SERVER, ENTER_CREDS) = range(2)


async def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(vps_order_start, pattern="^user_buy_vps$")],
        states={
            SPECIFY_SERVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, vps_specs_entered)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )


async def vps_order_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع سفارش VPS"""
    await update.callback_query.edit_message_text(
        "💻 **سفارش سرور مجازی**\n\n"
        "لطفاً مشخصات مورد نظر را ارسال کنید:\n\n"
        "فرمت: `CPU|RAM|Disk|OS|Location`\n\n"
        "مثال: `2|4GB|50GB|ubuntu-22.04|Germany`\n\n"
        "پس از ثبت سفارش، ادمین سرور را آماده و تحویل می‌دهد.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return SPECIFY_SERVER


async def vps_specs_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت مشخصات VPS"""
    session = await get_session().__anext__()
    user = await session.query(User).filter(
        User.telegram_id == update.effective_user.id
    ).first()

    text = update.message.text.strip().split("|")
    if len(text) < 5:
        await update.message.reply_text(
            "❌ فرمت نامعتبر. لطفاً به شکل زیر وارد کنید:\n"
            "`CPU|RAM|Disk|OS|Location`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return SPECIFY_SERVER

    cpu, ram, disk, os, location = [x.strip() for x in text]

    # Create VPS order
    vps = VPSOrder(
        user_id=user.id,
        cpu=cpu,
        ram=ram,
        disk=disk,
        os=os,
        status=OrderStatus.PENDING,
    )
    session.add(vps)

    # Create corresponding order
    order = Order(
        user_id=user.id,
        order_type="vps",
        amount=0,  # Will be set by admin
        status=OrderStatus.PENDING,
    )
    session.add(order)
    await session.commit()

    # Notify admins
    for admin_id in settings.bot.admin_ids:
        try:
            text = (
                f"🖥️ **سفارش VPS جدید**\n\n"
                f"👤 کاربر: @{user.username or 'بدون یوزر'} (`{user.telegram_id}`)\n"
                f"💻 CPU: {cpu} | 🧠 RAM: {ram} | 💾 Disk: {disk}\n"
                f"🐧 OS: {os} | 📍 Location: {location}\n"
                f"📅 تاریخ: {vps.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ آماده شد", callback_data=f"vps_ready_{vps.id}")],
                [InlineKeyboardButton("❌ لغو", callback_data=f"vps_cancel_{vps.id}")],
            ])

            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
        except Exception:
            pass

    await update.message.reply_text(
        "✅ سفارش VPS شما ثبت شد.\n"
        "ادمین سرور را آماده کرده و اطلاعات دسترسی را برای شما ارسال می‌کند."
    )

    return ConversationHandler.END


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های VPS"""
    query = update.callback_query
    data = query.data

    if data.startswith("vps_ready_"):
        vps_id = int(data.split("_")[-1])
        await vps_ready(update, context, vps_id)
    elif data.startswith("vps_cancel_"):
        vps_id = int(data.split("_")[-1])
        await vps_cancel(update, context, vps_id)
    elif data.startswith("vps_deliver_"):
        vps_id = int(data.split("_")[-1])
        await vps_deliver(update, context, vps_id)


async def vps_ready(update: Update, context: ContextTypes.DEFAULT_TYPE, vps_id: int) -> None:
    """ادمین سرور را آماده کرده و اطلاعات را وارد می‌کند"""
    await update.callback_query.edit_message_text(
        f"✅ **VPS #{vps_id} آماده تحویل است**\n\n"
        "لطفاً اطلاعات دسترسی را وارد کنید:\n"
        "فرمت: `IP|Port|User|Password`",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["vps_id"] = vps_id
    context.user_data["admin_state"] = "vps_deliver"


async def vps_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE, vps_id: int) -> None:
    """لغو سفارش VPS"""
    session = await get_session().__anext__()
    vps = await session.query(VPSOrder).filter(VPSOrder.id == vps_id).first()

    if vps:
        vps.status = OrderStatus.CANCELLED
        await session.commit()

        # Notify user
        user = await session.query(User).filter(User.id == vps.user_id).first()
        try:
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text=f"❌ سفارش VPS #{vps.id} توسط ادمین لغو شد.",
            )
        except Exception:
            pass

    await update.callback_query.edit_message_text(f"❌ سفارش VPS #{vps_id} لغو شد.")


async def vps_deliver(update: Update, context: ContextTypes.DEFAULT_TYPE, vps_id: int) -> None:
    """تحویل VPS به کاربر"""
    session = await get_session().__anext__()
    vps = await session.query(VPSOrder).filter(VPSOrder.id == vps_id).first()

    if not vps:
        await update.callback_query.answer("❌ سفارش یافت نشد!", show_alert=True)
        return

    text = update.callback_query.message.text.split("\n")[-1].strip().split("|")
    if len(text) < 4:
        await update.callback_query.answer("❌ فرمت نامعتبر!", show_alert=True)
        return

    ip, port, user, password = [x.strip() for x in text]

    vps.server_ip = ip
    vps.server_port = int(port)
    vps.ssh_user = user
    vps.ssh_password = password
    vps.status = OrderStatus.COMPLETED
    await session.commit()

    # Notify user
    db_user = await session.query(User).filter(User.id == vps.user_id).first()
    try:
        text = (
            f"🖥️ **سرور مجازی شما آماده است!**\n\n"
            f"🌐 IP: `{ip}`\n"
            f"🔌 Port: `{port}`\n"
            f"👤 User: `{user}`\n"
            f"🔒 Password: `{password}`\n"
            f"🐧 OS: {vps.os}\n\n"
            "⚠️ لطفاً اطلاعات را در جای امن نگه دارید."
        )

        await context.bot.send_message(
            chat_id=db_user.telegram_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        pass

    await update.callback_query.edit_message_text(
        f"✅ VPS #{vps_id} با موفقیت تحویل داده شد."
    )


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END
