from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class LanguageMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, (Message, CallbackQuery)):
            language_code = event.from_user.language_code or "en"
            data["language_code"] = language_code
        return await handler(event, data)