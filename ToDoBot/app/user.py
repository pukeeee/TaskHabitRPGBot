from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command, CommandObject
from app.messages import Message
from database.requests import setUser, deleteTask, addTask
import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def startCommand(message: Message, language_code: str):
    await setUser(message.from_user.id)
    await message.answer(Message.get_message(language_code, "start"), reply_markup = await kb.replyKb(language_code))

@router.message(Command("donate"))
async def donateComand(message: Message, command: CommandObject, language_code: str):
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.answer(Message.get_message(language_code, "donate"))
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

@router.callback_query(F.data.startswith("task_"))
async def delete_task(callback: CallbackQuery):
    await callback.answer("Task completed successfully ✅")
    await deleteTask(callback.data.split("_")[1])
    await callback.message.delete()
    await callback.message.answer("My tasks:", reply_markup = await kb.tasks(callback.from_user.id))

# @router.message(lambda message: message.text == "My tasks")
# async def show_tasks(message: Message):
#     await message.answer("My tasks:", reply_markup = await kb.tasks(message.from_user.id))

@router.message()
async def add_task(message: Message, language_code: str):
    if message.text == Message.get_message(language_code, "taskListButton"):
        await message.answer("My tasks:", reply_markup = await kb.tasks(message.from_user.id))
        return
    if len(message.text) >= 100:
        await message.answer(Message.get_message(language_code, "taskLength"))
        return
    if message.text.startswith("/"):
        return
    await message.answer(Message.get_message(language_code, "addTask"))
    await addTask(message.from_user.id, message.text)
    
