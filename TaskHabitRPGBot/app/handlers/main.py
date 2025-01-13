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
from config import IMG_FOLDER

# import logging
# logging.basicConfig(level=logging.INFO)

router = Router()



@router.message(Command("donate"))
async def donateComand(message: Message, command: CommandObject, language_code: str):
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.answer(Message.get_message(language_code, "donate"), parse_mode=ParseMode.HTML)
        return
    
    amount = int(command.args)
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=Message.get_message(language_code, "invoiceTitle"),
        description=Message.get_message(language_code, "invoiceDescription"),
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
    await message.answer(Message.get_message(language_code, "donateTy"),message_effect_id="5159385139981059251")



@router.message(Command("reset_habits"))
async def reset_habits(message: Message):
    if message.from_user.id == 514373294:
        await resetHabit()
        await message.answer("✅ Привычки успешно сброшены!")
    else:
        await message.answer("No no no no buddy\nWrong way") 



@router.message(Command("info"))
async def info_message(message: Message, state: FSMContext):
    pass

###############
"""Main page"""
###############


@router.message(UserState.startMenu)
async def main_process(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "habitTrackerButton"):
        await state.set_state(UserState.habits)
        await message.answer(Message.get_message(language_code, "habitStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await kb.habitsReplyKB(language_code))

    elif message.text == Message.get_message(language_code, "taskTrackerButton"):
        await state.set_state(UserState.todo)
        await message.answer(Message.get_message(language_code, "todoStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await kb.todoReplyKB(language_code))

    elif message.text == Message.get_message(language_code, "profileButton"):
        user = await getUserDB(message.from_user.id)
        profile = await getProfileDB(message.from_user.id)
        
        user_name = profile.user_name
        userExperience = user.experience // 1000
        experience = user.experience
        avatar_file = os.path.join(IMG_FOLDER, profile.race, profile.sex, profile.clas, profile.avatar)
        photo = FSInputFile(avatar_file)
        
        profile_message = Message.get_message(language_code, "profile").format(
                                                                                user_name = user_name,
                                                                                userExperience = userExperience,
                                                                                experience = experience
                                                                                )
        
        await message.answer_photo(
                                    photo = photo,
                                    caption = profile_message,
                                    parse_mode = ParseMode.HTML,
                                    reply_markup = await kb.profileInLineKB()
                                    )