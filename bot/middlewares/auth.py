"""میدلورها - احراز هویت و محدودیت درخواست"""

import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes

from config import settings


# Rate limiting storage
_user_requests = defaultdict(list)
_REQUEST_LIMIT = 30  # requests
_REQUEST_WINDOW = 60  # seconds


async def auth_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """بررسی احراز هویت و وضعیت کاربر"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id

    # Check if user is banned
    if hasattr(context, "bot_data") and "banned_users" in context.bot_data:
        if user_id in context.bot_data["banned_users"]:
            if update.message:
                await update.message.reply_text("⛔ شما از ربات مسدود شده‌اید.")
            return

    # Register user if new
    if update.message and update.message.text and update.message.text.startswith("/start"):
        from database.db import get_session
        from database.models import User, UserRole
        session = await get_session().__anext__()
        user = await session.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            user = User(
                telegram_id=user_id,
                username=update.effective_user.username,
                full_name=update.effective_user.full_name,
                role=UserRole.USER,
            )
            session.add(user)
            await session.commit()


async def throttle_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """محدودیت تعداد درخواست (Rate Limiting)"""
    if not update.effective_user:
        return

    user_id = update.effective_user.id
    now = time.time()

    # Clean old requests
    _user_requests[user_id] = [
        t for t in _user_requests[user_id] if now - t < _REQUEST_WINDOW
    ]

    if len(_user_requests[user_id]) >= _REQUEST_LIMIT:
        if update.message:
            await update.message.reply_text(
                "⚠️ لطفاً کمی صبر کنید و دوباره تلاش کنید."
            )
        return

    _user_requests[user_id].append(now)
