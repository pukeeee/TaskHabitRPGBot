from database.models import async_session
from database.models import User, Task
from sqlalchemy import select, update, delete, desc

async def setUser(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()

async def getTask(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        tasks = await session.scalars(select(Task).where(Task.user == user.id))
        return tasks

async def addTask(tg_id, task):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Task(task = task, user = user.id))
        await session.commit()

async def deleteTask(taskId):
    async with async_session() as session:
        await session.execute(delete(Task).where(Task.id == taskId))
        await session.commit()