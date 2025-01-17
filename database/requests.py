from database.models import async_session
from database.models import User, Task, Habit, Profile, Statistic
from sqlalchemy import select, update, delete, desc, and_
import time

#############
"""Profile"""
#############

async def setUser(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            unix_time = int(time.time())
            session.add(User(tg_id = tg_id, start_date = unix_time))
            await session.commit()
        return user



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



async def getLeaderboard():
    async with async_session() as session:
        users = await session.execute(
                                    select(Profile.user_name, User.experience)
                                    .join(User, Profile.user == User.id)
                                    .order_by(desc(User.experience))
                                    .limit(10)
                                )
        return users.all()

###########
"""Tasks"""
###########

async def getUncompletedTask(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        tasks = await session.scalars(select(Task).where(and_(Task.user == user.id,
                                                            Task.status == False)))
        return tasks
    
    
    
async def getCompletedTask(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        tasks = await session.scalars(select(Task).where(and_(Task.user == user.id,Task.status == True)
                                                        ).order_by(Task.done_date.desc()))
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



async def markTaskAsCompleted(taskId, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        task = await session.scalar(select(Task).where(Task.id == taskId))
        
        unix_time = int(time.time())
        user.all_tasks_count += 1
        task.status = True
        task.done_date = unix_time
        
        today_unix = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")))
        
        statistic = await session.scalar(
            select(Statistic).where(
                Statistic.user_id == user.id,
                Statistic.date == today_unix
            )
        )
        
        if statistic:
            statistic.tasks_count += 1
        else:
            new_statistic = Statistic(
                user_id = user.id,
                date = today_unix,
                tasks_count = 1
            )
            session.add(new_statistic)

        await session.commit()




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



async def editHabit(habitId, new_habit_text, habit_days, new_habit_experience):
    async with async_session() as session:
        habit = await session.scalar(select(Habit).where(Habit.id == habitId))
        if habit:
            habit.name = new_habit_text
            habit.days_of_week = habit_days
            habit.experience_points = new_habit_experience
            await session.commit()
            return True
        else:
            return False



async def getHabits(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        habits = await session.scalars(select(Habit).where(Habit.user == user.id))
        return habits



async def getHabitById(habitId):
    async with async_session() as session:
        habit = await session.scalar(select(Habit.name).where(Habit.id == habitId))
        return habit



async def getTodayHabits(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        habits = await session.scalars(select(Habit).where(and_(Habit.user == user.id,
                                                                Habit.status == False)))
        return habits



async def deleteHabit(habitId):
    async with async_session() as session:
        await session.execute(delete(Habit).where(Habit.id == habitId))
        await session.commit()



async def markHabitAsCompleted(habitId, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        statistic = await session.scalar(select(Statistic).where(Statistic.user_id == user.id))
        if not user:
            raise ValueError(f"User with tg_id={tg_id} not found")
        habit = await session.scalar(select(Habit).where(Habit.id == habitId))
        if not habit:
            raise ValueError(f"Habit with id={habitId} not found")
        
        user.all_habits_count += 1
        user.experience += habit.experience_points
        habit.status = True
        
        today_unix = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")))
        
        statistic = await session.scalar(
            select(Statistic).where(
                Statistic.user_id == user.id,
                Statistic.date == today_unix
            )
        )
        
        if statistic:
            statistic.habits_count += 1
        else:
            new_statistic = Statistic(
                user_id = user.id,
                date = today_unix,
                habits_count = 1
            )
            session.add(new_statistic)
        
        await session.commit()



async def resetHabit():
    async with async_session() as session:
        reset = update(Habit).where(Habit.status == True).values(status = False)
        await session.execute(reset)
        await session.commit()