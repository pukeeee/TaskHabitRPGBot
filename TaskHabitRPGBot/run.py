import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis 
from app.middlewares import LanguageMiddleware
from database.models import async_main
from app.handlers.main import router
from app.handlers.profile import profile
from app.handlers.tasks import task
from app.handlers.habits import habit
from config import TOKEN

async def main():
    redis = Redis(host = "localhost", port = 6379, db = 0)
    storage = RedisStorage(redis)
    
    await async_main()
    bot = Bot(token = TOKEN, 
            default = DefaultBotProperties(parse_mode = ParseMode.HTML))
    dp = Dispatcher(storage = storage)
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.include_router(profile)
    dp.include_router(habit)
    dp.include_router(task)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass