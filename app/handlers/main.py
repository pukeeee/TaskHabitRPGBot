from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
import random
import os
from app.l10n import Message as L10nMessage
from app.handlers.profiles import profileMessage
from database.repositories import (
    setUser,
    deleteTask,
    addTask,
    getUserDB,
    addHabit,
    deleteHabit,
    getTaskById,
    editTaskInDB,
    markHabitAsCompleted,
    changeNameDB,
    getProfileDB,
    resetHabit
)
from app.fsm import UserState, HabitState, TaskState, UserRPG
from app.keyboards import (
    startReplyKb,
    todoReplyKB,
    profileInLineKB,
    habitsReplyKB
)
from config import IMG_FOLDER

# import logging
# logging.basicConfig(level=logging.INFO)

router = Router()
router.name = 'main'



@router.message(UserState.startMenu)
async def main_process(message: Message, state: FSMContext, language_code: str):
    if message.text == L10nMessage.get_message(language_code, "habitTrackerButton"):
        await state.set_state(UserState.habits)
        await message.answer(L10nMessage.get_message(language_code, "habitStart"), 
                           reply_markup=await habitsReplyKB(language_code))

    elif message.text == L10nMessage.get_message(language_code, "taskTrackerButton"):
        await state.set_state(UserState.todo)
        await message.answer(L10nMessage.get_message(language_code, "todoStart"), 
                           reply_markup=await todoReplyKB(language_code))

    elif message.text == L10nMessage.get_message(language_code, "profileButton"):
        await profileMessage(message, state, language_code)