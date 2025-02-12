from database.repository import BaseRepository
from database.models import User, Task, Statistic
from sqlalchemy import select, update, delete, and_, func
import time
from typing import List, Optional

class TaskRepository(BaseRepository):
    async def get_uncompleted_tasks(self, tg_id: int) -> List[Task]:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if user:
                result = await self.session.scalars(
                    select(Task).where(
                        and_(Task.user == user.id, Task.status == False)
                    )
                )
                return result.all()
            return []
    


    async def get_completed_tasks(self, tg_id: int) -> List[Task]:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if user:
                result = await self.session.scalars(
                    select(Task)
                    .where(and_(Task.user == user.id, Task.status == True))
                    .order_by(Task.done_date.desc())
                )
                return result.all()
            return []



    async def add_task(self, tg_id: int, text: str, taskExp: int, complexity: str) -> bool:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if user:
                self.session.add(Task(task=text, user=user.id, complexity = complexity, experience_points = taskExp))
                return True
            return False

    
    
    async def check_tasks_count(self, tg_id: int) -> bool:
        user = await self.session.scalar(select(User).where(User.tg_id == tg_id))
        tasks_count = await self.session.scalar(select(func.count(Task.id)).where(Task.user == user.id))

        return False if tasks_count >= 10 else True
    


    async def delete_task(self, task_id: int) -> None:
        async with self.begin():
            await self.session.execute(
                delete(Task).where(Task.id == task_id)
            )



    async def edit_task(self, task_id: int, new_text: str, taskExp: int, complexity: str) -> None:
        # async with self.begin():
        #     await self.session.execute(
        #         update(Task)
        #         .where(Task.id == task_id)
        #         .values(task=new_text)
        #     )
        async with self.begin():
            task = await self.session.scalar(
                select(Task).where(Task.id == task_id)
            )
            if task:
                task.name = new_text
                task.experience_points = taskExp
                task.complexity = complexity
                return True
            return False



    async def get_task_by_id(self, task_id: int) -> Optional[str]:
        async with self.begin():
            return await self.session.scalar(
                select(Task.task).where(Task.id == task_id)
            )



    async def mark_completed(self, task_id: int, tg_id: int) -> None:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if not user:
                return

            task = await self.session.scalar(
                select(Task).where(Task.id == task_id)
            )
            if not task:
                return

            unix_time = int(time.time())
            user.all_tasks_count += 1
            user.experience += task.experience_points
            task.status = True
            task.done_date = unix_time

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
                statistic.tasks_count += 1
            else:
                new_statistic = Statistic(
                    user_id=user.id,
                    date=today_unix,
                    tasks_count=1
                )
                self.session.add(new_statistic)



################################################
"""Функции-обертки для обратной совместимости"""
################################################


async def getUncompletedTask(tg_id: int) -> List[Task]:
    async with TaskRepository() as repo:
        return await repo.get_uncompleted_tasks(tg_id)

async def getCompletedTask(tg_id: int) -> List[Task]:
    async with TaskRepository() as repo:
        return await repo.get_completed_tasks(tg_id)

async def addTask(tg_id: int, text: str, complexity: str, taskExp: int) -> bool:
    async with TaskRepository() as repo:
        return await repo.add_task(tg_id, text, complexity, taskExp)

async def checkTasksCount(tg_id: int) -> bool:
    async with TaskRepository() as repo:
        return await repo.check_tasks_count(tg_id)


async def deleteTask(task_id: int) -> None:
    async with TaskRepository() as repo:
        await repo.delete_task(task_id)

async def editTaskInDB(task_id: int, new_text: str, taskExp: int, complexity: str) -> None:
    async with TaskRepository() as repo:
        await repo.edit_task(task_id, new_text, taskExp, complexity)

async def getTaskById(task_id: int) -> Optional[str]:
    async with TaskRepository() as repo:
        return await repo.get_task_by_id(task_id)

async def markTaskAsCompleted(task_id: int, tg_id: int) -> None:
    async with TaskRepository() as repo:
        await repo.mark_completed(task_id, tg_id) 