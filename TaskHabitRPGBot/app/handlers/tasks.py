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
                                getProfileDB, resetHabit, getTask)
from app.fsm import UserState, HabitState, TaskState, UserRPG
import app.keyboards as kb

task = Router()


@task.message(UserState.todo)
async def todo_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "taskListButton"):
        await taskList(message, language_code)
        
    elif message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))
        
    elif message.text == "Statistic":
        await message.answer("Not available now")
        
    elif message.text == Message.get_message(language_code, "addTaskButton"):
        await state.set_state(TaskState.addTask)
        await message.answer(Message.get_message(language_code, "createTask"), parse_mode=ParseMode.HTML,
                            reply_markup = await kb.addTaskReplyKB(language_code))
        
    elif message.text == Message.get_message(language_code, "doneTasksButton"):
        await message.answer("Not available now")



async def taskList(message: Message, language_code: str):
    taskListMessage = await getTaskListMessage(language_code, message.from_user.id)
    await message.answer(taskListMessage, reply_markup = await kb.taskListKB(language_code))



async def getTaskListMessage(language_code: str, tg_id):
    taskList = list(await getTask(tg_id))
    message = Message.get_message(language_code, "taskslist")
    if not taskList:
        message += "🚽\n"
    else:
        for task in taskList:
            message += f"▫️  {task.task}\n"
    message += Message.get_message(language_code, "taskListMessage")
    return message



@task.callback_query(F.data == "editTasks")
async def editTaskList(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "editTask"), reply_markup = await kb.editTasks(callback.from_user.id))



@task.callback_query(F.data == "deleteTasks")
async def deleteTaskList(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteTask"), reply_markup = await kb.delTasks(callback.from_user.id))




@task.message(TaskState.addTask)
async def addTask_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))

    elif message.text == Message.get_message(language_code, "backToTaskButton"):
        await state.set_state(UserState.todo)
        await message.answer(Message.get_message(language_code, "todoStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await kb.todoReplyKB(language_code))
    
    elif message.text.startswith("/"):
        return
    
    else:
        await message.answer(Message.get_message(language_code, "addTask"))
        await addTask(message.from_user.id, message.text)


@task.callback_query(F.data.startswith("deltask_"))
async def delete_task(callback: CallbackQuery, language_code: str):
    await callback.answer(Message.get_message(language_code, "deletTaskList"))
    await deleteTask(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteTask"), reply_markup = await kb.delTasks(callback.from_user.id))



@task.callback_query(F.data.startswith("edittask_"))
async def edit_task(callback: CallbackQuery, language_code: str, state: FSMContext):
    await callback.answer("✅")
    taskId = callback.data.split("_")[1]
    task = await getTaskById(taskId)
    await state.set_state(TaskState.taskEdit)
    await state.update_data(taskId = taskId)
    await callback.message.edit_text(text = f"Current text: {task}\n\nPlease enter new text for your task:")



@task.callback_query(F.data == "backToTaskList")
async def backToTaskList_handler(callback: CallbackQuery, language_code: str):
    taskListMessage = await getTaskListMessage(language_code, callback.from_user.id)
    await callback.message.edit_text(text = taskListMessage, reply_markup = await kb.taskListKB(language_code))


async def todo_exception(message, state, language_code):
    if message.text == Message.get_message(language_code, "taskListButton"):
        await message.answer(Message.get_message(language_code, "taskslist"), reply_markup = await kb.delTasks(message.from_user.id))
        await state.set_state(UserState.todo)
        return True
    
    elif message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))
        await state.set_state(UserState.todo)
        return True
    
    elif message.text == Message.get_message(language_code, "addTaskButton"):
        await state.set_state(TaskState.addTask)
        await message.answer(Message.get_message(language_code, "createTask"), parse_mode=ParseMode.HTML,
                            reply_markup = await kb.addTaskReplyKB(language_code))
        return True
    
    elif message.text == Message.get_message(language_code, "doneTasksButton"):
        await message.answer("Not available now")
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
    await message.answer("✅")
    
    taskListMessage = await getTaskListMessage(language_code, message.from_user.id)
    await message.answer(taskListMessage, reply_markup = await kb.taskListKB(language_code))


