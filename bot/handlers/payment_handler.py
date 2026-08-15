"""هندلرهای پرداخت - کارت به کارت و تایید فیش"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters,
)
from telegram.constants import ParseMode

from config import settings

from database.db import get_session
from database.models import (
    Transaction, Order, OrderStatus, BankCard, User,
)
from bot.utils.helpers import format_price
from bot.utils.bank_image import generate_card_image


# Conversation states
(SELECT_CARD, ENTER_AMOUNT, UPLOAD_RECEIPT, VERIFY_CODE) = range(4)


def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(select_card_start, pattern="^pay_select_card$"),
            CallbackQueryHandler(enter_amount_start, pattern="^pay_enter_amount$"),
        ],
        states={
            SELECT_CARD: [CallbackQueryHandler(card_selected)],
            ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_entered)],
            UPLOAD_RECEIPT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receipt_uploaded)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )


async def select_card_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """نمایش لیست کارت‌های بانکی"""
    session = await get_session().__anext__()
    cards = await session.query(BankCard).filter(BankCard.is_active == True).all()

    if not cards:
        await update.callback_query.edit_message_text(
            "❌ هیچ کارت بانکی فعالی وجود ندارد.\n"
            "لطفاً با پشتیبانی تماس بگیرید."
        )
        return ConversationHandler.END

    context.user_data["amount"] = context.user_data.get("amount", 0)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"💳 {card.bank_name or 'بانک'} - {card.card_number[-4:]}",
            callback_data=f"card_{card.id}",
        )]
        for card in cards
    ])

    await update.callback_query.edit_message_text(
        "💳 **انتخاب کارت بانکی**\n\n"
        "لطفاً کارتی که مبلغ را به آن واریز کردید را انتخاب کنید:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )
    return SELECT_CARD


async def card_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """کارت انتخاب شد - نمایش اطلاعات کارت با تصویر"""
    query = update.callback_query
    card_id = int(query.data.split("_")[-1])
    session = await get_session().__anext__()
    card = await session.query(BankCard).filter(BankCard.id == card_id).first()

    if not card:
        await query.answer("❌ کارت یافت نشد!", show_alert=True)
        return ConversationHandler.END

    amount = context.user_data.get("amount", 0)
    context.user_data["selected_card_id"] = card_id

    # Generate card image
    try:
        image_path = await generate_card_image(
            card_number=card.card_number,
            card_holder=card.card_holder,
            bank_name=card.bank_name or "بانک",
            amount=amount,
        )

        text = (
            f"💳 **اطلاعات پرداخت**\n\n"
            f"🏦 بانک: **{card.bank_name or 'نامشخص'}**\n"
            f"💳 شماره کارت: `{card.card_number}`\n"
            f"👤 به نام: **{card.card_holder}**\n"
            f"💰 مبلغ: **{format_price(amount)}**\n\n"
            f"⚠️ لطفاً دقیقاً این مبلغ را واریز کنید.\n"
            f"سپس فیش واریزی را ارسال کنید:"
        )

        with open(image_path, "rb") as img:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=img,
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="pay_select_card")],
                ]),
            )

    except Exception as e:
        await query.edit_message_text(
            f"❌ خطا در تولید تصویر کارت: {e}\n\n"
            f"💳 شماره کارت: `{card.card_number}`\n"
            f"👤 به نام: **{card.card_holder}**\n"
            f"💰 مبلغ: **{format_price(amount)}**\n\n"
            f"لطفاً فیش واریزی را ارسال کنید:",
            parse_mode=ParseMode.MARKDOWN,
        )

    return UPLOAD_RECEIPT


async def enter_amount_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع وارد کردن مبلغ"""
    await update.callback_query.edit_message_text(
        "💰 **وارد کردن مبلغ**\n\n"
        "لطفاً مبلغ واریزی (تومان) را وارد کنید:",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ENTER_AMOUNT


async def amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مبلغ وارد شد"""
    try:
        amount = float(update.message.text.replace(",", ""))
        context.user_data["amount"] = amount
        await update.message.reply_text(
            f"✅ مبلغ **{format_price(amount)}** ثبت شد.\n\n"
            f"لطفاً فیش واریزی را ارسال کنید:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return UPLOAD_RECEIPT
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کنید:")
        return ENTER_AMOUNT


async def receipt_uploaded(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """فیش آپلود شد - ارسال به ادمین برای تایید"""
    session = await get_session().__anext__()

    # Get receipt photo
    if update.message.photo:
        photo = update.message.photo[-1]
        photo_id = photo.file_id
    elif update.message.document:
        photo_id = update.message.document.file_id
    else:
        await update.message.reply_text("❌ لطفاً یک تصویر یا فایل ارسال کنید:")
        return UPLOAD_RECEIPT

    amount = context.user_data.get("amount", 0)
    card_id = context.user_data.get("selected_card_id")

    # Save transaction
    user = await session.query(User).filter(
        User.telegram_id == update.effective_user.id
    ).first()

    tx = Transaction(
        user_id=user.id,
        amount=amount,
        bank_card_id=card_id,
        receipt_photo_id=photo_id,
        status=OrderStatus.PENDING,
    )
    session.add(tx)
    await session.commit()

    # Forward to admins
    for admin_id in settings.bot.admin_ids:
        try:
            text = (
                f"💳 **پرداخت جدید در انتظار تایید**\n\n"
                f"👤 کاربر: @{user.username or 'بدون یوزر'} (`{user.telegram_id}`)\n"
                f"💰 مبلغ: **{format_price(amount)}**\n"
                f"📅 تاریخ: {tx.created_at.strftime('%Y-%m-%d %H:%M')}"
            )

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ تایید", callback_data=f"admin_verify_tx_{tx.id}"),
                    InlineKeyboardButton("❌ رد", callback_data=f"admin_reject_tx_{tx.id}"),
                ],
                [InlineKeyboardButton("👤 پروفایل کاربر", callback_data=f"admin_user_{user.id}")],
            ])

            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo_id,
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
        except Exception:
            pass

    await update.message.reply_text(
        "✅ فیش شما دریافت شد.\n"
        "پس از تایید توسط ادمین، به اطلاع شما خواهد رسید."
    )

    context.user_data.clear()
    return ConversationHandler.END


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های پرداخت"""
    query = update.callback_query
    data = query.data

    if data.startswith("admin_verify_tx_"):
        tx_id = int(data.split("_")[-1])
        await verify_transaction(update, context, tx_id, True)
    elif data.startswith("admin_reject_tx_"):
        tx_id = int(data.split("_")[-1])
        await verify_transaction(update, context, tx_id, False)
    elif data.startswith("card_"):
        await card_selected(update, context)


async def verify_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE, tx_id: int, approve: bool
) -> None:
    """تایید یا رد تراکنش توسط ادمین"""
    session = await get_session().__anext__()
    tx = await session.query(Transaction).filter(Transaction.id == tx_id).first()

    if not tx:
        await update.callback_query.answer("❌ تراکنش یافت نشد!", show_alert=True)
        return

    user = await session.query(User).filter(User.id == tx.user_id).first()

    if approve:
        tx.status = OrderStatus.PAID
        tx.verified_by = update.effective_user.id
        await session.commit()

        # Update user balance
        user.balance += tx.amount
        await session.commit()

        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    f"✅ **پرداخت تایید شد**\n\n"
                    f"💰 مبلغ: **{format_price(tx.amount)}**\n"
                    f"📅 تاریخ: {tx.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"موجودی جدید: **{format_price(user.balance)}**"
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            pass

        await update.callback_query.edit_message_caption(
            caption=(
                f"✅ **پرداخت تایید شد**\n\n"
                f"👤 کاربر: @{user.username or 'بدون یوزر'}\n"
                f"💰 مبلغ: **{format_price(tx.amount)}**\n"
                f"📅 تاریخ: {tx.updated_at.strftime('%Y-%m-%d %H:%M')}"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید شده", callback_data="dummy")],
            ]),
        )
    else:
        tx.status = OrderStatus.REJECTED
        tx.verified_by = update.effective_user.id
        await session.commit()

        # Notify user
        try:
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text=(
                    f"❌ **پرداخت رد شد**\n\n"
                    f"💰 مبلغ: **{format_price(tx.amount)}**\n"
                    f"📅 تاریخ: {tx.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"لطفاً فیش صحیح را ارسال کنید یا با پشتیبانی تماس بگیرید."
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            pass

        await update.callback_query.edit_message_caption(
            caption=(
                f"❌ **پرداخت رد شد**\n\n"
                f"👤 کاربر: @{user.username or 'بدون یوزر'}\n"
                f"💰 مبلغ: **{format_price(tx.amount)}**\n"
                f"📅 تاریخ: {tx.updated_at.strftime('%Y-%m-%d %H:%M')}"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ رد شده", callback_data="dummy")],
            ]),
        )


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END
