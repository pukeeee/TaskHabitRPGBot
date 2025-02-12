from database.repository import BaseRepository
from database.models import User, Habit, Statistic
from sqlalchemy import select, update, delete, and_, func
import time
from typing import List, Optional

class HabitRepository(BaseRepository):
    async def add_habit(self, tg_id: int, habit_text: str, 
                       habit_days: str, habit_experience: int) -> None:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if user:
                unix_time = int(time.time())
                new_habit = Habit(
                    name=habit_text,
                    days_of_week=habit_days,
                    experience_points=habit_experience,
                    user=user.id,
                    created_date=unix_time
                )
                self.session.add(new_habit)

    
    
    async def check_habits_count(self, tg_id: int) -> bool:
        user = await self.session.scalar(select(User).where(User.tg_id == tg_id))
        habits_count = await self.session.scalar(select(func.count(Habit.id)).where(Habit.user == user.id))

        return False if habits_count >= 4 else True



    async def edit_habit(self, habit_id: int, new_habit_text: str, 
                        habit_days: str, new_habit_experience: int) -> bool:
        async with self.begin():
            habit = await self.session.scalar(
                select(Habit).where(Habit.id == habit_id)
            )
            if habit:
                habit.name = new_habit_text
                habit.days_of_week = habit_days
                habit.experience_points = new_habit_experience
                return True
            return False

    async def get_habits(self, tg_id: int) -> List[Habit]:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if user:
                result = await self.session.scalars(
                    select(Habit).where(Habit.user == user.id)
                )
                return result.all()
            return []

    async def get_habit_by_id(self, habit_id: int) -> Optional[str]:
        async with self.begin():
            return await self.session.scalar(
                select(Habit.name).where(Habit.id == habit_id)
            )

    async def get_today_habits(self, tg_id: int) -> List[Habit]:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if user:
                result = await self.session.scalars(
                    select(Habit).where(
                        and_(Habit.user == user.id, Habit.status == False)
                    )
                )
                return result.all()
            return []

    async def delete_habit(self, habit_id: int) -> None:
        async with self.begin():
            await self.session.execute(
                delete(Habit).where(Habit.id == habit_id)
            )

    async def mark_completed(self, habit_id: int, tg_id: int) -> None:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if not user:
                raise ValueError(f"User with tg_id={tg_id} not found")

            habit = await self.session.scalar(
                select(Habit).where(Habit.id == habit_id)
            )
            if not habit:
                raise ValueError(f"Habit with id={habit_id} not found")

            user.all_habits_count += 1
            user.experience += habit.experience_points
            habit.status = True

            today_unix = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")))
            statistic = await self.session.scalar(
                select(Statistic).where(
                    and_(
                        Statistic.user_id == user.id,
                        Statistic.date == today_unix
                    )
                )
            )

            if statistic:
                statistic.habits_count += 1
            else:
                new_statistic = Statistic(
                    user_id=user.id,
                    date=today_unix,
                    habits_count=1
                )
                self.session.add(new_statistic)

    async def reset_habits(self) -> None:
        async with self.begin():
            await self.session.execute(
                update(Habit)
                .where(Habit.status == True)
                .values(status=False)
            )


# Функции-обертки для обратной совместимости
async def addHabit(tg_id: int, habit_text: str, habit_days: str, 
                  habit_experience: int) -> None:
    async with HabitRepository() as repo:
        await repo.add_habit(tg_id, habit_text, habit_days, habit_experience)



async def checkHabitsCount(tg_id: int) -> bool:
    async with HabitRepository() as repo:
        return await repo.check_habits_count(tg_id)



async def editHabit(habit_id: int, new_habit_text: str, habit_days: str, 
                   new_habit_experience: int) -> bool:
    async with HabitRepository() as repo:
        return await repo.edit_habit(habit_id, new_habit_text, habit_days, 
                                   new_habit_experience)



async def getHabits(tg_id: int) -> List[Habit]:
    async with HabitRepository() as repo:
        return await repo.get_habits(tg_id)



async def getHabitById(habit_id: int) -> Optional[str]:
    async with HabitRepository() as repo:
        return await repo.get_habit_by_id(habit_id)

async def getTodayHabits(tg_id: int) -> List[Habit]:
    async with HabitRepository() as repo:
        return await repo.get_today_habits(tg_id)

async def deleteHabit(habit_id: int) -> None:
    async with HabitRepository() as repo:
        await repo.delete_habit(habit_id)

async def markHabitAsCompleted(habit_id: int, tg_id: int) -> None:
    async with HabitRepository() as repo:
        await repo.mark_completed(habit_id, tg_id)

async def resetHabit() -> None:
    async with HabitRepository() as repo:
        await repo.reset_habits() 