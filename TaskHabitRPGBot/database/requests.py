from database.models import async_session
from database.models import User, Task, Habit
from sqlalchemy import select, update, delete, desc
import time

async def setUser(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()

async def getExp(tg_id):
    async with async_session() as session:
        experience = await session.scalar(select(User.experience).where(User.tg_id == tg_id))
        return experience

###########
"""Tasks"""
###########

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

async def editTaskInDB(taskId, newText):
    async with async_session() as session:
        edit = update(Task).where(Task.id == taskId).values(task = newText)
        await session.execute(edit)
        await session.commit()

async def getTaskById(taskId):
    async with async_session() as session:
        task = await session.scalar(select(Task.task).where(Task.id == taskId))
        return task

############
"""habits"""
############

async def addHabit(tg_id, habit_text, habit_days, habit_experience):
    async with async_session() as session:
        unix_time = int(time.time())
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        new_habit = Habit(
            name = habit_text,
            days_of_week = habit_days,
            experience_points = habit_experience,
            user = user.id,
            created_date = unix_time
        )
        session.add(new_habit)
        await session.commit()

async def getHabits(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        habits = await session.scalars(select(Habit).where(Habit.user == user.id))
        return habits

async def deleteHabit(habitId):
    async with async_session() as session:
        await session.execute(delete(Habit).where(Habit.id == habitId))
        await session.commit()