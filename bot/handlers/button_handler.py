"""بخش شخصی‌سازی دکمه‌ها در پنل ادمین"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from telegram.constants import ParseMode

from config import settings
from database.db import get_session
from bot.utils.button_customizer import (
    ButtonCustomizer, ButtonConfig, ButtonColor, ButtonStyle,
    button_customizer, COLOR_EMOJI_MAP,
)
from bot.utils.helpers import format_price


# States for button customization
(SELECT_SECTION, SELECT_BUTTON, CHANGE_EMOJI, CHANGE_COLOR, CHANGE_TEXT, PREVIEW) = range(6)


async def button_customization_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی شخصی‌سازی دکمه‌ها"""
    theme = button_customizer.get_active_theme()

    text = (
        "🎨 **شخصی‌سازی دکمه‌ها**\n\n"
        f"تم فعال: **{theme.name}**\n"
        f"تعداد تم‌ها: **{len(button_customizer.themes)}**\n\n"
        "از این بخش می‌توانید:\n"
        "• رنگ دکمه‌ها را تغییر دهید\n"
        "• ایموجی دکمه‌ها را تغییر دهید\n"
        "• متن دکمه‌ها را ویرایش کنید\n"
        "• تم جدید ایجاد کنید\n\n"
        "⚠️ توجه: تغییر رنگ و ایموجی پرمیوم نیاز به ربات با اشتراک پرمیوم دارد."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔘 دکمه‌های اصلی", callback_data="btn_section_main")],
        [InlineKeyboardButton("🛍️ دکمه‌های محصولات", callback_data="btn_section_product")],
        [InlineKeyboardButton("💳 دکمه‌های پرداخت", callback_data="btn_section_payment")],
        [InlineKeyboardButton("⚙️ دکمه‌های ادمین", callback_data="btn_section_admin")],
        [InlineKeyboardButton("➕ ایجاد تم جدید", callback_data="btn_create_theme")],
        [InlineKeyboardButton("👀 پیش‌نمایش", callback_data="btn_preview")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_dashboard")],
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard,
    )


async def show_section_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش دکمه‌های یک بخش"""
    query = update.callback_query
    section = query.data.replace("btn_section_", "")

    context.user_data["btn_section"] = section
    theme = button_customizer.get_active_theme()

    sections = {
        "main": theme.main_buttons,
        "product": theme.product_buttons,
        "payment": theme.payment_buttons,
        "admin": theme.admin_buttons,
    }

    buttons = sections.get(section, [])
    section_names = {
        "main": "اصلی",
        "product": "محصولات",
        "payment": "پرداخت",
        "admin": "ادمین",
    }

    text = (
        f"🔘 **دکمه‌های بخش {section_names.get(section, section)}**\n\n"
        "برای ویرایش، روی دکمه کلیک کنید:"
    )

    keyboard = []
    for i, btn in enumerate(buttons):
        emoji_preview = btn.emoji_name or ""
        color_emoji = COLOR_EMOJI_MAP.get(btn.color, "🔵")
        keyboard.append([
            InlineKeyboardButton(
                f"{color_emoji} {emoji_preview} {btn.text}",
                callback_data=f"btn_edit_{section}_{i}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_button_customize"),
    ])

    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def edit_button_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """منوی ویرایش یک دکمه"""
    query = update.callback_query
    parts = query.data.replace("btn_edit_", "").split("_")
    section = parts[0]
    btn_index = int(parts[1])

    context.user_data["btn_section"] = section
    context.user_data["btn_index"] = btn_index

    theme = button_customizer.get_active_theme()
    sections = {
        "main": theme.main_buttons,
        "product": theme.product_buttons,
        "payment": theme.payment_buttons,
        "admin": theme.admin_buttons,
    }

    buttons = sections.get(section, [])
    if btn_index >= len(buttons):
        await query.answer("❌ دکمه یافت نشد!", show_alert=True)
        return

    btn = buttons[btn_index]

    text = (
        "✏️ **ویرایش دکمه**\n\n"
        f"📝 متن: **{btn.text}**\n"
        f"🎨 رنگ: **{btn.color.value}** {COLOR_EMOJI_MAP.get(btn.color, '')}\n"
        f"😀 ایموجی: **{btn.emoji_name or 'ندارد'}**\n"
        f"🔗 callback: `{btn.callback_data}`\n\n"
        "بخشی را برای ویرایش انتخاب کنید:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("😀 تغییر ایموجی", callback_data="btn_change_emoji")],
        [InlineKeyboardButton("🎨 تغییر رنگ", callback_data="btn_change_color")],
        [InlineKeyboardButton("📝 تغییر متن", callback_data="btn_change_text")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"btn_section_{section}")],
    ])

    await query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard,
    )


async def change_emoji_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع تغییر ایموجی"""
    await update.callback_query.edit_message_text(
        "😀 **تغییر ایموجی دکمه**\n\n"
        "لطفاً ایموجی جدید را ارسال کنید:\n\n"
        "• می‌توانید از ایموجی یونیکد استفاده کنید\n"
        "• یا شناسه ایموجی پرمیوم را ارسال کنید\n\n"
        "برای حذف ایمعبی، `none` بفرستید:",
        parse_mode=ParseMode.MARKDOWN,
    )
    return CHANGE_EMOJI


async def change_emoji_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ثبت ایموجی جدید"""
    new_emoji = update.message.text.strip()
    section = context.user_data.get("btn_section", "main")
    btn_index = context.user_data.get("btn_index", 0)

    theme = button_customizer.get_active_theme()
    sections = {
        "main": theme.main_buttons,
        "product": theme.product_buttons,
        "payment": theme.payment_buttons,
        "admin": theme.admin_buttons,
    }

    buttons = sections.get(section, [])
    if btn_index < len(buttons):
        if new_emoji.lower() == "none":
            buttons[btn_index].emoji_name = None
        else:
            buttons[btn_index].emoji_name = new_emoji
        await update.message.reply_text(f"✅ ایموجی دکمه به **{new_emoji}** تغییر کرد.", parse_mode=ParseMode.MARKDOWN)
    return -1


async def change_color_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع تغییر رنگ"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵 آبی", callback_data="color_blue"),
            InlineKeyboardButton("🟢 سبز", callback_data="color_green"),
        ],
        [
            InlineKeyboardButton("🔴 قرمز", callback_data="color_red"),
            InlineKeyboardButton("⚪ خاکستری", callback_data="color_gray"),
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_button_customize")],
    ])

    await update.callback_query.edit_message_text(
        "🎨 **تغییر رنگ دکمه**\n\n"
        "رنگ جدید را انتخاب کنید:\n\n"
        "🔵 آبی - دکمه‌های اصلی و اطلاعات\n"
        "🟢 سبز - دکمه‌های تایید و خرید\n"
        "🔴 قرمز - دکمه‌های لغو و خطر\n"
        "⚪ خاکستری - دکمه‌های ثانویه",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def change_color_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ثبت رنگ جدید"""
    query = update.callback_query
    new_color = query.data.replace("color_", "")

    section = context.user_data.get("btn_section", "main")
    btn_index = context.user_data.get("btn_index", 0)

    theme = button_customizer.get_active_theme()
    sections = {
        "main": theme.main_buttons,
        "product": theme.product_buttons,
        "payment": theme.payment_buttons,
        "admin": theme.admin_buttons,
    }

    buttons = sections.get(section, [])
    if btn_index < len(buttons):
        try:
            color = ButtonColor(new_color)
            buttons[btn_index].color = color
            await query.answer(f"✅ رنگ به {new_color} تغییر کرد!")
        except ValueError:
            await query.answer("❌ رنگ نامعتبر!", show_alert=True)
            return

    await query.edit_message_text(
        "✅ رنگ دکمه با موفقیت تغییر کرد!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data=f"btn_section_{section}")],
        ]),
    )


async def change_text_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع تغییر متن"""
    await update.callback_query.edit_message_text(
        "📝 **تغییر متن دکمه**\n\n"
        "لطفاً متن جدید را ارسال کنید:\n"
        "(ایموجی قبل از متن اختیاری است)",
        parse_mode=ParseMode.MARKDOWN,
    )
    return CHANGE_TEXT


async def change_text_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ثبت متن جدید"""
    new_text = update.message.text.strip()
    section = context.user_data.get("btn_section", "main")
    btn_index = context.user_data.get("btn_index", 0)

    theme = button_customizer.get_active_theme()
    sections = {
        "main": theme.main_buttons,
        "product": theme.product_buttons,
        "payment": theme.payment_buttons,
        "admin": theme.admin_buttons,
    }

    buttons = sections.get(section, [])
    if btn_index < len(buttons):
        buttons[btn_index].text = new_text
        await update.message.reply_text(f"✅ متن دکمه به **{new_text}** تغییر کرد.", parse_mode=ParseMode.MARKDOWN)
    return -1


async def preview_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پیش‌نمایش دکمه‌ها با تنظیمات فعلی"""
    theme = button_customizer.get_active_theme()

    text = (
        "👀 **پیش‌نمایش دکمه‌ها**\n\n"
        f"تم: **{theme.name}**\n\n"
        "دکمه‌های فعلی با تنظیمات رنگ و ایموجی:"
    )

    keyboard = []
    for btn in theme.main_buttons:
        emoji_prefix = f"{btn.emoji_name} " if btn.emoji_name else ""
        color_dot = COLOR_EMOJI_MAP.get(btn.color, "🔵")
        keyboard.append([
            InlineKeyboardButton(
                f"{color_dot} {emoji_prefix}{btn.text}",
                callback_data="dummy",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 بازگشت", callback_data="admin_button_customize"),
    ])

    await update.callback_query.edit_message_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def create_theme_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """شروع ایجاد تم جدید"""
    await update.callback_query.edit_message_text(
        "➕ **ایجاد تم جدید**\n\n"
        "لطفاً نام تم جدید را ارسال کنید:\n"
        "مثال: `تم رنگی تابستانی`",
        parse_mode=ParseMode.MARKDOWN,
    )
    return CHANGE_TEXT


async def create_theme_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ثبت تم جدید"""
    theme_name = update.message.text.strip()

    if theme_name in button_customizer.themes:
        await update.message.reply_text("❌ تمی با این نام وجود دارد. نام دیگری انتخاب کنید:")
        return CHANGE_TEXT

    from bot.utils.button_customizer import ButtonTheme
    new_theme = ButtonTheme(name=theme_name)
    button_customizer.add_theme(new_theme)

    await update.message.reply_text(
        f"✅ تم **{theme_name}** با موفقیت ایجاد شد!\n\n"
        "حالا می‌توانید دکمه‌های این تم را ویرایش کنید.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return -1


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت callback های شخصی‌سازی دکمه"""
    query = update.callback_query
    data = query.data

    if data == "admin_button_customize":
        await button_customization_menu(update, context)
    elif data.startswith("btn_section_"):
        await show_section_buttons(update, context)
    elif data.startswith("btn_edit_"):
        await edit_button_menu(update, context)
    elif data == "btn_change_emoji":
        return await change_emoji_start(update, context)
    elif data == "btn_change_color":
        await change_color_start(update, context)
    elif data == "btn_change_text":
        return await change_text_start(update, context)
    elif data == "btn_preview":
        await preview_buttons(update, context)
    elif data == "btn_create_theme":
        return await create_theme_start(update, context)
    elif data.startswith("color_"):
        await change_color_done(update, context)


def get_conversation_handler() -> ConversationHandler:
    """ایجاد ConversationHandler برای شخصی‌سازی دکمه‌ها"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_customization_menu, pattern="^admin_button_customize$"),
        ],
        states={
            CHANGE_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_emoji_done)],
            CHANGE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_text_done)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
