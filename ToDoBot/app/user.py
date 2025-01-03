from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from database.requests import setUser, deleteTask, addTask
import app.keyboards as kb
from app.messages import Message

router = Router()

@router.message(CommandStart())
async def startCommand(message: Message, language_code: str):
    await setUser(message.from_user.id)
    await message.answer(Message.get_message(language_code, "start"), reply_markup = await kb.replyKb())

@router.callback_query(F.data.startswith("task_"))
async def delete_task(callback: CallbackQuery):
    await callback.answer("Task completed successfully ✅")
    await deleteTask(callback.data.split("_")[1])
    await callback.message.delete()
    await callback.message.answer("My tasks:", reply_markup = await kb.tasks(callback.from_user.id))

@router.message(lambda message: message.text == "My tasks")
async def show_tasks(message: Message):
    await message.answer("My tasks:", reply_markup = await kb.tasks(message.from_user.id))

@router.message()
async def add_task(message: Message):
    if len(message.text) >= 100:
        await message.answer("Task is too lond. Max length is 100 characters")
        return
    if message.text == "My tasks":
        return
    await message.answer("Tast added ✅\n\nPress the 'My tasks' to see tasks")
    await addTask(message.from_user.id, message.text)
    # await message.answer("Send me your task", reply_markup = await kb.tasks(message.from_user.id))
    
