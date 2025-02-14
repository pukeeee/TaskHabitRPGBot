from sqlalchemy.ext.asyncio import AsyncSession
from database.models import async_session
from contextlib import asynccontextmanager


class BaseRepository:
    """
    Базовый класс-репозиторий для работы с асинхронными сессиями SQLAlchemy.
    Позволяет автоматически управлять сессией и транзакциями.
    """
    
    
    def __init__(self):
        """
        Инициализирует объект, но не создает сессию сразу.
        """
        self._session: AsyncSession | None = None  # Переменная для хранения сессии
        self._transaction_in_progress: bool = False  # Флаг для отслеживания состояния транзакции
    
    
    async def __aenter__(self):
        """
        Асинхронный контекстный менеджер для работы с сессией.
        Использование: `async with BaseRepository() as repo:`
        """
        self._session = async_session()  # Создание новой сессии
        return self  # Возвращает сам объект, чтобы можно было обращаться к `self.session`
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Закрытие сессии при выходе из контекстного менеджера.
        Если произошла ошибка (exc_type != None), выполняется откат изменений (rollback).
        Если ошибок нет, выполняется коммит (commit).
        """
        if self._session:
            try:
                if exc_type:
                    await self._session.rollback()  # Откат, если была ошибка
                else:
                    await self._session.commit()  # Фиксируем изменения в БД
            finally:
                await self._session.close()  # Закрываем сессию после работы
                self._session = None  # Очищаем переменную
                self._transaction_in_progress = False  # Сбрасываем флаг транзакции
    
    
    
    @property
    def session(self) -> AsyncSession:
        """
        Свойство для получения текущей сессии.
        Если сессия не инициализирована, выбрасывается ошибка.
        """
        if not self._session:
            raise RuntimeError("Session not initialized. Use 'async with' context")  
        return self._session  # Возвращаем сессию, если она активна
    
    
    
    @asynccontextmanager
    async def begin(self):
        """
        Контекстный менеджер для работы с транзакциями.
        Позволяет использовать `async with repo.begin():`, чтобы вручную управлять транзакциями.
        """
        if not self._session:
            raise RuntimeError("Session not initialized")  # Проверка на наличие сессии
        
        if not self._transaction_in_progress:
            self._transaction_in_progress = True  # Устанавливаем флаг начала транзакции
            async with self._session.begin() as transaction:  # Начинаем транзакцию
                try:
                    yield  # Выполняем код внутри `async with repo.begin():`
                except Exception:
                    await transaction.rollback()  # В случае ошибки делаем откат
                    raise  # Пробрасываем исключение дальше
                finally:
                    self._transaction_in_progress = False  # Сбрасываем флаг транзакции
        else:
            yield  # Если транзакция уже запущена, продолжаем её использовать без создания новой