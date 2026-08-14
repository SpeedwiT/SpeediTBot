"""میدلور محدودیت درخواست‌ها"""

import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes


# Rate limiting storage
_user_requests = defaultdict(list)
_REQUEST_LIMIT = 30  # requests per window
_REQUEST_WINDOW = 60  # seconds


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
