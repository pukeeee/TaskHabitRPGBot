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
    getUserDB,
    getProfileDB,
    resetHabit
)
from app.fsm import UserState, UserRPG
from app.keyboards import (
    startReplyKb
)
from config import IMG_FOLDER

# import logging
# logging.basicConfig(level=logging.INFO)

router = Router()
router.name = 'commands'



@router.message(CommandStart())
async def startCommand(message: Message, language_code: str, state: FSMContext):
    print(f"Start command called with language: {language_code}")
    
    await setUser(message.from_user.id)
    profile = await getProfileDB(message.from_user.id)
    print(f"User profile: {profile}")

    if profile:
        # Получаем текст приветствия
        text = L10nMessage.get_message(language_code, "start")
        print(f"Localized start message:")
        print(f"Language: {language_code}")
        print(f"Message ID: start")
        print(f"Retrieved text: {text}")
        
        # Получаем клавиатуру
        keyboard = await startReplyKb(language_code)
        print(f"Reply keyboard: {keyboard}")
        
        # Отправляем сообщение
        await message.answer(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        await state.set_state(UserState.startMenu)
    else:
        new_user_text = L10nMessage.get_message(language_code, "newCharacter")
        print(f"New user message: {new_user_text}")
        
        await state.set_state(UserRPG.setName)
        await message.answer(
            text=new_user_text,
            parse_mode=ParseMode.HTML
        )



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