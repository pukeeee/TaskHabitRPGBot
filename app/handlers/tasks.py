from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone
import random
import os
from app.l10n import Message
from database.repositories import (addTask, deleteTask, editTaskInDB, getTaskById,
    markTaskAsCompleted, getUncompletedTask, getCompletedTask, getUserDB, checkTasksCount
)
from app.fsm import UserState, TaskState
from app.keyboards import (startReplyKb, todoReplyKB, taskListKB, addTaskReplyKB,
    editTasks, delTasks, completeTasksKB, completedTasksKB, delCompletedTasks, setTaskComplexity
)
from .exp_calc import taskExpCalc


router = Router()
router.name = 'tasks'



@router.message(UserState.todo)
async def todo_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "taskListButton"):
        await taskList(message, language_code)
        
    elif message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))
        
    elif message.text == Message.get_message(language_code, "statisticButton"):
        stat = await getUserDB(message.from_user.id)
        
        start_date = datetime.fromtimestamp(stat.start_date, tz=timezone.utc)
        formatted_start_date = start_date.strftime("%d.%m.%y")
        days_counter = (datetime.now(tz=timezone.utc) - start_date).days
        all_tasks_count = stat.all_tasks_count
        
        await message.answer(Message.get_message(language_code, "taskStatistic").format(start_date = formatted_start_date,
                                                                                    days_counter = days_counter,
                                                                                    all_tasks_count = all_tasks_count))
        
    elif message.text == Message.get_message(language_code, "addTaskButton"):
        await state.set_state(TaskState.addTask)
        await message.answer(Message.get_message(language_code, "createTask"), parse_mode=ParseMode.HTML,
                            reply_markup = await addTaskReplyKB(language_code))
        
    elif message.text == Message.get_message(language_code, "doneTasksButton"):
        text = await getCompletedTasks(language_code, message.from_user.id)
        await message.answer(text, reply_markup = await completedTasksKB(language_code))



async def taskList(message: Message, language_code: str):
    taskListMessage = await getUncompletedTasks(language_code, message.from_user.id)
    await message.answer(taskListMessage, reply_markup = await taskListKB(language_code))



async def getUncompletedTasks(language_code: str, tg_id):
    taskList = list(await getUncompletedTask(tg_id))
    message = Message.get_message(language_code, "taskslist")
    if not taskList:
        message += "\n\n🚽\n\n"
    else:
        message += "\n\n"
        for task in taskList:
            message += f"{task.complexity}  <b>{task.task}</b>  |   + {task.experience_points} ✨\n"
        message += "\n"
    message += Message.get_message(language_code, "taskListMessage")
    return message



async def getCompletedTasks(language_code: str, tg_id):
    taskList = list(await getCompletedTask(tg_id))
    message = Message.get_message(language_code, "completedTasks")
    if not taskList:
        message += "\n\n🚽\n\n"
    else:
        message += "\n\n"
        for task in taskList:
            done_date = datetime.fromtimestamp(task.done_date, tz=timezone.utc).strftime("%d.%m")
            message += f"▫️ <i>{done_date}</i>:  <b>{task.task}</b>\n"
        message += "\n"
    message += Message.get_message(language_code, "completedTasksMessage")
    return message



@router.callback_query(F.data == "editTasks")
async def editTaskList(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "editTask"),
                                    reply_markup = await editTasks(callback.from_user.id))
    await callback.answer()



@router.callback_query(F.data == "deleteTasks")
async def deleteTaskList(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteTask"),
                                    reply_markup = await delTasks(callback.from_user.id))
    await callback.answer()



@router.callback_query(F.data == "completeTasks")
async def completeTasks(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "completeTasks"),
                                    reply_markup = await completeTasksKB(callback.from_user.id))
    await callback.answer()



@router.message(TaskState.addTask)
async def addTask_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))

    elif message.text == Message.get_message(language_code, "backToTaskButton"):
        await state.set_state(UserState.todo)
        await message.answer(Message.get_message(language_code, "todoStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await todoReplyKB(language_code))
    
    elif message.text.startswith("/"):
        return
    
    else:
        text = message.text.strip()
        if len(text) > 100:
            await message.answer(Message.get_message(language_code, "taskLength"))
            return
        else:
            limit = await checkTasksCount(message.from_user.id)
            if limit == False:
                await message.answer(Message.get_message(language_code, "taskLimitReached"))
            else:
                await message.answer(Message.get_message(language_code, "taskExp"), reply_markup = await setTaskComplexity())
                await state.update_data(task_text = text)
                await state.set_state(TaskState.setExp)
            
            # newTask = await addTask(message.from_user.id, message.text)
            # if newTask == False:
            #     await message.answer(Message.get_message(language_code, "taskLimitReached"))
            # else:
            #     await message.answer(Message.get_message(language_code, "addTask"))



@router.callback_query(TaskState.setExp)
async def setTaskExpHandler(callback: CallbackQuery, state: FSMContext, language_code: str):
    complexity = callback.data
    
    taskData = await saveTask(complexity, state, language_code)
    
    await addTask(callback.from_user.id, taskData["taskText"], taskData["taskExp"], complexity)
    await state.clear()
    await state.set_state(TaskState.addTask)
    await callback.message.answer(Message.get_message(language_code, "addTask"))
    await callback.answer("✅")
    


async def saveTask(complexity, state: FSMContext, language_code: str):
    task_data = await state.get_data()
    taskText = task_data.get("task_text")
    
    taskExp = await taskExpCalc(complexity)
    
    return {"taskText": taskText, "taskExp": taskExp}



@router.message(TaskState.setExp)
async def setExpExceptions(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))

    elif message.text == Message.get_message(language_code, "backToTaskButton"):
        await state.set_state(UserState.todo)
        await message.answer(Message.get_message(language_code, "todoStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await todoReplyKB(language_code))

    


@router.callback_query(F.data.startswith("deltask_"))
async def delete_task(callback: CallbackQuery, state: FSMContext, language_code: str):
    await deleteTask(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteTask"),
                                    reply_markup = await delTasks(callback.from_user.id))



@router.callback_query(F.data.startswith("delCompletedTask_"))
async def delete_completed_task(callback: CallbackQuery, state: FSMContext, language_code: str):
    await deleteTask(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteTask"),
                                    reply_markup = await delCompletedTasks(callback.from_user.id))



@router.callback_query(F.data.startswith("edittask_"))
async def edit_task(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.answer("✅")
    taskId = callback.data.split("_")[1]
    task = await getTaskById(taskId)
    await state.set_state(TaskState.taskEdit)
    await state.update_data(taskId = taskId)
    await callback.message.edit_text(text = f"Current text: {task}\n\nPlease enter new text for your task:")



@router.callback_query(F.data.startswith("completetask_"))
async def delete_task(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.answer(Message.get_message(language_code, "taskCompleted"))
    await markTaskAsCompleted(callback.data.split("_")[1], callback.from_user.id)
    await callback.message.edit_text(text = Message.get_message(language_code, "completeTasks"),
                                    reply_markup = await completeTasksKB(callback.from_user.id))



@router.callback_query(F.data == "backToTaskList")
async def backToTaskList_handler(callback: CallbackQuery, state: FSMContext, language_code: str):
    taskListMessage = await getUncompletedTasks(language_code, callback.from_user.id)
    await callback.message.edit_text(text = taskListMessage, reply_markup = await taskListKB(language_code))
    await callback.answer()



async def todo_exception(message, state, language_code):
    if message.text == Message.get_message(language_code, "taskListButton"):
        await taskList(message, language_code)
        await state.set_state(UserState.todo)
        return True
    
    elif message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))
        return True
    
    elif message.text == Message.get_message(language_code, "statisticButton"):
        stat = await getUserDB(message.from_user.id)
        
        start_date = datetime.fromtimestamp(stat.start_date, tz=timezone.utc)
        formatted_start_date = start_date.strftime("%d.%m.%y")
        days_counter = (datetime.now(tz=timezone.utc) - start_date).days
        all_tasks_count = stat.all_tasks_count
        
        await message.answer(Message.get_message(language_code, "taskStatistic").format(start_date = formatted_start_date,
                                                                                    days_counter = days_counter,
                                                                                    all_tasks_count = all_tasks_count))
        
    elif message.text == Message.get_message(language_code, "addTaskButton"):
        await state.set_state(TaskState.addTask)
        await message.answer(Message.get_message(language_code, "createTask"), parse_mode=ParseMode.HTML,
                            reply_markup = await addTaskReplyKB(language_code))
        
    elif message.text == Message.get_message(language_code, "doneTasksButton"):
        text = await getCompletedTasks(language_code, message.from_user.id)
        await message.answer(text, reply_markup = await completedTasksKB(language_code))
    
    return False



@router.message(TaskState.taskEdit)
async def editTask(message: Message, state: FSMContext, language_code: str):
    if await todo_exception(message, state, language_code):
        return
    
    text = message.text.strip()
    if len(text) > 100:
        await message.answer(Message.get_message(language_code, "taskLength"))
        return
    else:
        await message.answer(Message.get_message(language_code, "taskExp"), reply_markup = await setTaskComplexity())
        await state.update_data(task_text = text)
        await state.set_state(TaskState.editExp)
        # data = await state.get_data()
        # taskId = data['taskId']
        # await editTaskInDB(taskId, text)
        # await state.set_state(UserState.todo)

        # taskListMessage = await getUncompletedTasks(language_code, message.from_user.id)
        # await message.answer(taskListMessage, reply_markup = await taskListKB(language_code))



@router.message(TaskState.editExp)
async def _(message: Message, state: FSMContext, language_code: str):
    if await todo_exception(message, state, language_code):
        return


@router.callback_query(TaskState.editExp)
async def editTaskExpHandler(callback: CallbackQuery, state: FSMContext, language_code: str):
    complexity = callback.data
    
    taskData = await saveTask(complexity, state, language_code)
    data = await state.get_data()
    await editTaskInDB(data["taskId"], taskData["taskText"], taskData["taskExp"], complexity)
    await state.clear()
    await state.set_state(UserState.todo)
    taskListMessage = await getUncompletedTasks(language_code, callback.from_user.id)
    await callback.message.edit_text(taskListMessage, reply_markup = await taskListKB(language_code))



@router.callback_query(F.data == "deleteCompletedTasks")
async def deleteCompletedTasks(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteTask"),
                                    reply_markup = await delCompletedTasks(callback.from_user.id))
    await callback.answer()



@router.callback_query(F.data == "backToCompletedTasksList")
async def backToCompletedTasksList(callback: CallbackQuery, language_code: str):
    text = await getCompletedTasks(language_code, callback.from_user.id)
    await callback.message.edit_text(text = text, reply_markup = await completedTasksKB(language_code))
    await callback.answer()



