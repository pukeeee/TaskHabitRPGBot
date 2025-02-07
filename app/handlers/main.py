from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
import random
import os
from app.l10n import Message as L10nMessage
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



@router.message(CommandStart())
async def startCommand(message: Message, language_code: str, state: FSMContext):
    await setUser(message.from_user.id)
    profile = await getProfileDB(message.from_user.id)

    if profile:
        await message.answer(
            L10nMessage.get_message(language_code, "start"),
            parse_mode = ParseMode.HTML,
            reply_markup = await startReplyKb(language_code)
        )
        await state.set_state(UserState.startMenu)
        
    else:
        await state.set_state(UserRPG.setName)
        await message.answer(L10nMessage.get_message(language_code, "newCharacter"), parse_mode = ParseMode.HTML)
        


@router.message(Command("donate"))
async def donateComand(message: Message, command: CommandObject, language_code: str):
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.answer(L10nMessage.get_message(language_code, "donate"), parse_mode=ParseMode.HTML)
        return
    
    amount = int(command.args)
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=L10nMessage.get_message(language_code, "invoiceTitle"),
        description=L10nMessage.get_message(language_code, "invoiceDescription"),
        prices=prices,
        provider_token="",
        payload=f"{amount}_stars",
        currency="XTR"
    )



@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)



@router.message(F.successful_payment)
async def on_successfull_payment(message: Message, language_code: str):
    # await message.answer(message.successful_payment.telegram_payment_charge_id)
    await message.answer(L10nMessage.get_message(language_code, "donateTy"),message_effect_id="5159385139981059251")



@router.message(Command("reset_habits"))
async def reset_habits(message: Message):
    if message.from_user.id == 514373294:
        await resetHabit()
        await message.answer("✅ Привычки успешно сброшены!")
        
    else:
        await message.answer("No no no no buddy\nWrong way") 



@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("dev: @pukeee")


@router.message(Command("info"))
async def info_message(message: Message, state: FSMContext, language_code: str):
    current_state = await state.get_state()

    if current_state == UserState.todo.state:
        await message.answer(L10nMessage.get_message(language_code, "taskTrackerInfo"))
    elif current_state == UserState.startMenu.state:
        await message.answer(L10nMessage.get_message(language_code, "homeInfo"))
    elif current_state == UserState.habits.state:
        await message.answer(L10nMessage.get_message(language_code, "habitTrackerInfo"))


###############
"""Main page"""
###############


@router.message(UserState.startMenu)
async def main_process(message: Message, state: FSMContext, language_code: str):
    if message.text == L10nMessage.get_message(language_code, "habitTrackerButton"):
        await state.set_state(UserState.habits)
        await message.answer(L10nMessage.get_message(language_code, "habitStart"), 
                            reply_markup = await habitsReplyKB(language_code))

    elif message.text == L10nMessage.get_message(language_code, "taskTrackerButton"):
        await state.set_state(UserState.todo)
        await message.answer(L10nMessage.get_message(language_code, "todoStart"), 
                            reply_markup = await todoReplyKB(language_code))

    elif message.text == L10nMessage.get_message(language_code, "profileButton"):
        user = await getUserDB(message.from_user.id)
        profile = await getProfileDB(message.from_user.id)
        
        user_name = profile.user_name
        userExperience = user.experience // 1000
        experience = user.experience
        avatar_file = os.path.join(IMG_FOLDER, profile.race, profile.sex, profile.clas, profile.avatar)
        photo = FSInputFile(avatar_file)
        
        profile_message = L10nMessage.get_message(language_code, "profile").format(user_name = user_name,
                                                                                userExperience = userExperience,
                                                                                experience = experience)
        
        await message.answer_photo(photo = photo,
                                    caption = profile_message,
                                    parse_mode = ParseMode.HTML,
                                    reply_markup = await profileInLineKB(language_code))