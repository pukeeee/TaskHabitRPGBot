from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.l10n import SUPPORTED_LOCALES, DEFAULT_LOCALE

class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_locale = event.from_user.language_code
            if user_locale not in SUPPORTED_LOCALES:
                user_locale = DEFAULT_LOCALE
            data['language_code'] = user_locale
        return await handler(event, data)