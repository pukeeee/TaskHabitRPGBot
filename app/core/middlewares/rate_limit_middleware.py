from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import asyncio
from redis.asyncio import Redis
import time


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов пользователей.
    Использует Redis для хранения общего счетчика запросов.
    """
    def __init__(self, redis_connection: Redis):
        """
        Инициализация middleware с подключением к Redis
        Args:
            redis_connection: Объект подключения к Redis
        """
        self.redis = redis_connection
        
        # Общие настройки лимита для всех типов запросов
        self.max_requests = 1  # Максимальное количество запросов
        self.window_seconds = 1  # Временное окно в секундах
    
    async def check_limit(self, key: str) -> bool:
        """
        Проверяет, не превышен ли общий лимит запросов для пользователя
        
        Args:
            key: Уникальный ключ для пользователя
            
        Returns:
            bool: True если запрос разрешен, False если превышен лимит
        """
        try:
            # Увеличиваем общий счетчик запросов в Redis
            requests = await self.redis.incr(key)
            
            # Для первого запроса устанавливаем время жизни ключа
            if requests == 1:
                # По истечении window_seconds ключ будет автоматически удален
                await self.redis.expire(key, self.window_seconds)
            
            # Разрешаем запрос, если счетчик не превышает лимит
            return requests <= self.max_requests
            
        except Exception as e:
            # В случае ошибки Redis логируем и пропускаем запрос
            print(f"Redis error in check_limit: {e}")
            return True

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработчик каждого входящего запроса
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Входящее событие (сообщение или колбэк)
            data: Дополнительные данные события
            
        Returns:
            Any: Результат обработки запроса или None если превышен лимит
        """
        # Получаем ID пользователя из события
        user_id = event.from_user.id
        
        # Формируем общий ключ для всех типов запросов пользователя
        key = f"rate_limit:user:{user_id}"
        
        # Проверяем, не превышен ли лимит запросов
        is_allowed = await self.check_limit(key)
        
        if not is_allowed:
            # Если лимит превышен, отправляем сообщение пользователю
            if isinstance(event, Message):
                # Для обычных сообщений отправляем ответ в чат
                await event.answer(
                    "Too many requests, please wait 1 seconds ⛔️",
                    parse_mode=None  # Отключаем парсинг HTML/Markdown
                )
            else:
                # Для колбэков показываем всплывающее уведомление
                await event.answer(
                    "Too many requests, please wait 1 seconds ⛔️"
                )
            return  # Прерываем обработку запроса
        
        # Если лимит не превышен, передаем управление следующему обработчику
        return await handler(event, data) 