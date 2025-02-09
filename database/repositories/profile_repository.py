from database.repository import BaseRepository
from database.models import User, Profile, Statistic
from sqlalchemy import select, update, delete, desc, and_, func
import time
from typing import Optional, List, Tuple

class ProfileRepository(BaseRepository):
    async def set_user(self, tg_id: int) -> Optional[User]:
        async with self.begin():
            user = await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )
            if not user:
                unix_time = int(time.time())
                user = User(tg_id=tg_id, start_date=unix_time)
                self.session.add(user)
            return user



    async def get_user(self, tg_id: int) -> Optional[User]:
        async with self.begin():
            return await self.session.scalar(
                select(User).where(User.tg_id == tg_id)
            )



    async def get_profile(self, tg_id: int) -> Optional[Profile]:
        async with self.begin():
            user = await self.get_user(tg_id)
            if user:
                return await self.session.scalar(
                    select(Profile).where(Profile.user == user.id)
                )
            return None



    async def change_name(self, tg_id: int, new_name: str) -> None:
        async with self.begin():
            user = await self.get_user(tg_id)
            if user:
                await self.session.execute(
                    update(Profile)
                    .where(Profile.user == user.id)
                    .values(user_name=new_name)
                )



    async def save_character(self, tg_id: int, user_name: str, avatar: str) -> None:
        async with self.begin():
            # Убираем префикс из имени файла аватара, но сохраняем расширение
            # (например, "1_Dark Knight.png" -> "Dark Knight.png")
            avatar_name = avatar.split('_', 1)[1] if '_' in avatar else avatar
            print(f"Saving to DB - original avatar: {avatar}, cleaned avatar: {avatar_name}")
            
            user = await self.get_user(tg_id)
            if user:
                profile = await self.session.scalar(
                    select(Profile).where(Profile.user == user.id)
                )
                if profile:
                    profile.user_name = user_name
                    profile.avatar = avatar_name
                    print(f"Updated profile - user_name: {profile.user_name}, avatar: {profile.avatar}")
                else:
                    new_profile = Profile(
                        user=user.id,
                        user_name=user_name,
                        avatar=avatar_name
                    )
                    self.session.add(new_profile)
                    print(f"Created new profile - user_name: {user_name}, avatar: {avatar_name}")



    async def get_leaderboard(self) -> List[Tuple[str, int]]:
        async with self.begin():
            result = await self.session.execute(
                select(Profile.user_name, User.experience)
                .join(User, Profile.user == User.id)
                .order_by(desc(User.experience))
                .limit(10)
            )
            return result.all()
    
    
    
    async def get_all_active_users(self) -> List[int]:
        async with self.begin():
            result = await self.session.execute(
                select(User.tg_id).where(User.is_active == True)
            )
            return result.scalars().all()



################################################
"""Функции-обертки для обратной совместимости"""
################################################

async def setUser(tg_id: int) -> Optional[User]:
    async with ProfileRepository() as repo:
        return await repo.set_user(tg_id)

async def getUserDB(tg_id: int) -> Optional[User]:
    async with ProfileRepository() as repo:
        return await repo.get_user(tg_id)

async def getProfileDB(tg_id: int) -> Optional[Profile]:
    async with ProfileRepository() as repo:
        return await repo.get_profile(tg_id)

async def changeNameDB(tg_id: int, new_name: str) -> None:
    async with ProfileRepository() as repo:
        await repo.change_name(tg_id, new_name)

async def saveUserCharacter(tg_id: int, user_name: str, avatar: str) -> None:
    async with ProfileRepository() as repo:
        await repo.save_character(tg_id, user_name, avatar)

async def getLeaderboard() -> List[Tuple[str, int]]:
    async with ProfileRepository() as repo:
        return await repo.get_leaderboard()

async def get_all_active_users() -> List[int]:
    async with ProfileRepository() as repo:
        return await repo.get_all_active_users()