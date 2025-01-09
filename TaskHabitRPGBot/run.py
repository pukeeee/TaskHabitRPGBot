import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.middlewares import LanguageMiddleware
from database.models import async_main
from app.user import router
from config import TOKEN

"""поделючить redis"""

async def main():
    await async_main()
    bot = Bot(token = TOKEN, 
            default = DefaultBotProperties(parse_mode = ParseMode.HTML))
    dp = Dispatcher()
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass