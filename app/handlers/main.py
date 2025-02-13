from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
import random
import os
from app.l10n.l10n import Message as L10nMessage
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
    saveUserCharacter,
    getLeaderboard
)
from app.states import User
from app.keyboards import (
    startReplyKb,
    todoReplyKB,
    profileInLineKB,
    habitsReplyKB
)
from app.core.utils.config import IMG_FOLDER

# import logging
# logging.basicConfig(level=logging.INFO)

router = Router()
router.name = 'main'



@router.message(User.startMenu)
async def main_process(message: Message, state: FSMContext, language_code: str):
    if message.text == L10nMessage.get_message(language_code, "habitTrackerButton"):
        await state.set_state(User.habits)
        await message.answer(L10nMessage.get_message(language_code, "habitStart"), 
                           reply_markup=await habitsReplyKB(language_code))

    elif message.text == L10nMessage.get_message(language_code, "taskTrackerButton"):
        await state.set_state(User.todo)
        await message.answer(L10nMessage.get_message(language_code, "todoStart"), 
                           reply_markup=await todoReplyKB(language_code))

    elif message.text == L10nMessage.get_message(language_code, "profileButton"):
        tg_id = message.from_user.id
        profile_data = await profileMessage(message, state, language_code, tg_id)
        if profile_data:
            await message.answer_photo(
                photo=profile_data.photo,
                caption=profile_data.profile_message,
                parse_mode=ParseMode.HTML,
                reply_markup=await profileInLineKB(language_code)
            )
        else:
            await message.answer("Error loading profile")