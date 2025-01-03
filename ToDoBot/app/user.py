from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from database.requests import setUser, deleteTask, addTask
import app.keyboards as kb

user = Router()

@user.message(CommandStart())
async def startCommand(message: Message):
    await setUser(message.from_user.id)
    await message.answer("Welcom to ToDoBot!\nSend me your task", reply_markup = await kb.tasks(message.from_user.id))

@user.callback_query(F.data.startswith("task_"))
async def delete_task(callback: CallbackQuery):
    await callback.answer("Task completed!")
    await deleteTask(callback.data.split("_")[1])
    await callback.message.delete()
    await callback.message.answer("Send me your task", reply_markup = await kb.tasks(callback.from_user.id))

@user.message()
async def add_task(message: Message):
    if len(message.text) >= 100:
        await message.answer("Task is too lond. Max length is 100 characters")
        return
    await addTask(message.from_user.id, message.text)
    await message.answer("Task added!\nSend me your task", reply_markup=await kb.tasks(message.from_user.id))
