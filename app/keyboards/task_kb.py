from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.l10n import Message
from database.repositories import getUncompletedTask, getCompletedTask



async def todoReplyKB(language_code: str) -> ReplyKeyboardMarkup:
    taskListButton = Message.get_message(language_code, "taskListButton")
    backToMain = Message.get_message(language_code, "homeButton")
    statistic = "Statistic"
    addTaskButton = Message.get_message(language_code, "addTaskButton")
    doneTasksButton = Message.get_message(language_code, "doneTasksButton")
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=addTaskButton)],
            [KeyboardButton(text=doneTasksButton), KeyboardButton(text=taskListButton)],
            [KeyboardButton(text=statistic), KeyboardButton(text=backToMain)]
        ],
        resize_keyboard=True
    )



async def addTaskReplyKB(language_code: str) -> ReplyKeyboardMarkup:
    backToMain = Message.get_message(language_code, "homeButton")
    backToTask = Message.get_message(language_code, "backToTaskButton")
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=backToTask)],
            [KeyboardButton(text=backToMain)]
        ],
        resize_keyboard=True
    )



async def taskListKB(language_code: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=Message.get_message(language_code, "editTaskButton"),
            callback_data="editTasks"
        ),
        InlineKeyboardButton(
            text=Message.get_message(language_code, "deleteTaskButton"),
            callback_data="deleteTasks"
        )
    )
    keyboard.row(InlineKeyboardButton(
        text="Mark as completed",
        callback_data="completeTasks"
    ))
    return keyboard.as_markup()



async def delTasks(tg_id: int) -> InlineKeyboardMarkup:
    tasks = await getUncompletedTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for task in tasks:
        keyboard.add(InlineKeyboardButton(
            text=task.task,
            callback_data=f"deltask_{task.id}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToTaskList"
    ))
    return keyboard.adjust(1).as_markup()



async def delCompletedTasks(tg_id: int) -> InlineKeyboardMarkup:
    tasks = await getCompletedTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for task in tasks:
        keyboard.add(InlineKeyboardButton(
            text=task.task,
            callback_data=f"delCompletedTask_{task.id}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToCompletedTasksList"
    ))
    return keyboard.adjust(1).as_markup()



async def editTasks(tg_id: int) -> InlineKeyboardMarkup:
    tasks = await getUncompletedTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for task in tasks:
        keyboard.add(InlineKeyboardButton(
            text=task.task,
            callback_data=f"edittask_{task.id}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToTaskList"
    ))
    return keyboard.adjust(1).as_markup()



async def completeTasksKB(tg_id: int) -> InlineKeyboardMarkup:
    tasks = await getUncompletedTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for task in tasks:
        keyboard.add(InlineKeyboardButton(
            text=task.task,
            callback_data=f"completetask_{task.id}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToTaskList"
    ))
    return keyboard.adjust(1).as_markup()



async def completedTasksKB(language_code: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=Message.get_message(language_code, "deleteTaskButton"), callback_data="deleteCompletedTasks")]
        ]
    )
    return keyboard