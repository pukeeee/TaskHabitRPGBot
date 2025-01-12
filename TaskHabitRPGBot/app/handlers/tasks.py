from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
import random
import os
from app.messages import Message
from database.requests import (setUser, deleteTask, addTask, getUserDB, 
                                addHabit, deleteHabit, getTaskById, 
                                editTaskInDB, markHabitAsCompleted, changeNameDB,
                                getProfileDB, resetHabit)
from app.fsm import UserState, HabitState, TaskState, UserRPG
import app.keyboards as kb

task = Router()

@task.message(UserState.todo)
async def todo_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == "My tasks":
        await message.answer(Message.get_message(language_code, "taskslist"), reply_markup = await kb.delTasks(message.from_user.id))
    elif message.text == "🏠 Home":
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))
        return
    elif message.text == "Info":
        await message.answer(Message.get_message(language_code, "taskTrackerInfo"))
    elif message.text == "Edit task":
        await message.answer(Message.get_message(language_code, "editTask"), reply_markup = await kb.editTasks(message.from_user.id))
        return
    if message.text.startswith("/"):
        return
    if message.text != "My tasks" and message.text != "🏠 Home" and message.text != "Info" and message.text != "Edit task":
        await message.answer(Message.get_message(language_code, "addTask"))
        await addTask(message.from_user.id, message.text)



@task.callback_query(F.data.startswith("deltask_"))
async def delete_task(callback: CallbackQuery, language_code: str):
    await callback.answer(Message.get_message(language_code, "deletTaskList"))
    await deleteTask(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "taskslist"), reply_markup = await kb.delTasks(callback.from_user.id))



@task.callback_query(F.data.startswith("edittask_"))
async def edit_task(callback: CallbackQuery, language_code: str, state: FSMContext):
    await callback.answer("The task to be edited is selected ✅")
    taskId = callback.data.split("_")[1]
    task = await getTaskById(taskId)
    await state.set_state(TaskState.taskEdit)
    await state.update_data(taskId = taskId)
    await callback.message.edit_text(text = f"Current text: {task}\n\nPlease enter new text for your task:")



async def todo_exception(message, state, language_code):
    if message.text == "My tasks":
        await message.answer(Message.get_message(language_code, "taskslist"), reply_markup = await kb.delTasks(message.from_user.id))
        await state.set_state(UserState.todo)
        return True
    elif message.text == "🏠 Home":
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))
        await state.set_state(UserState.todo)
        return True
    elif message.text == "Info":
        await message.answer(Message.get_message(language_code, "taskTrackerInfo"))
        await state.set_state(UserState.todo)
        return True
    elif message.text == "Edit task":
        await message.answer(Message.get_message(language_code, "taskslist"), reply_markup = await kb.editTasks(message.from_user.id))
        await state.set_state(UserState.todo)
        return True
    return False



@task.message(TaskState.taskEdit)
async def editTask(message: Message, state: FSMContext, language_code: str):
    if await todo_exception(message, state, language_code):
        return
    newText = message.text
    data = await state.get_data()
    taskId = data['taskId']
    await editTaskInDB(taskId, newText)
    await state.set_state(UserState.todo)
    await message.answer("Task updated successfully!✅")
    await message.answer(Message.get_message(language_code, "taskslist"), reply_markup = await kb.editTasks(message.from_user.id))


