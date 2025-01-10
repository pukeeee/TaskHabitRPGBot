from database.models import async_session
from database.models import User, Task, Habit, Profile
from sqlalchemy import select, update, delete, desc, and_
import time

###########
"""Profile"""
###########

async def setUser(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()



async def getUserDB(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user



async def getProfileDB(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user_id = user.id
        profile = await session.scalar(select(Profile).where(Profile.user == user_id))
        return profile



async def changeNameDB(tg_id, new_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        user_id = user.id
        edit = update(Profile).where(Profile.user == user_id).values(user_name = new_name)
        await session.execute(edit)
        await session.commit()



async def saveUserCharacter(tg_id: int, user_name: str, avatar: str, race: str, sex: str, clas: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            profile = await session.scalar(select(Profile).where(Profile.user == user.id))
            if profile:
                profile.user_name = user_name
                profile.avatar = avatar
                profile.race = race
                profile.sex = sex
                profile.clas = clas
            else:
                new_profile = Profile(
                    user=user.id,
                    user_name=user_name,
                    avatar=avatar,
                    race=race,
                    sex=sex,
                    clas=clas
                )
                session.add(new_profile)
            await session.commit()

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
"""Habits"""
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



async def getTodayHabits(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        habits = await session.scalars(select(Habit).where(and_(
                                                                Habit.user == user.id,
                                                                Habit.is_active == True)))
        return habits



async def deleteHabit(habitId):
    async with async_session() as session:
        await session.execute(delete(Habit).where(Habit.id == habitId))
        await session.commit()



async def markHabitAsCompleted(habitId):
    async with async_session() as session:
        edit = update(Habit).where(Habit.id == habitId).values(is_active = False)
        await session.execute(edit)
        await session.commit()