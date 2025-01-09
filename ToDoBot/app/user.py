from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from app.messages import Message
from database.requests import setUser, deleteTask, addTask, getExp, addHabit, deleteHabit, getTaskById, editTaskInDB
from app.fsm import UserState, HabitState, TaskState
import app.keyboards as kb

# import logging
# logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(CommandStart())
async def startCommand(message: Message, language_code: str, state: FSMContext):
    await setUser(message.from_user.id)
    await state.set_state(UserState.startMenu)
    await message.answer(Message.get_message(language_code, "start"), parse_mode=ParseMode.HTML, reply_markup = await kb.startReplyKb(language_code))

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

###############
"""Main page"""
###############

@router.message(UserState.startMenu)
async def main_process(message: Message, state: FSMContext, language_code: str):
    if message.text == "Habit Tracker":
        await state.set_state(UserState.habits)
        await message.answer(Message.get_message(language_code, "habitStart"), parse_mode=ParseMode.HTML, reply_markup = await kb.habitsReplyKB(language_code))
        return
    elif message.text == "Task Tracker":
        await state.set_state(UserState.todo)
        await message.answer(Message.get_message(language_code, "todoStart"), parse_mode=ParseMode.HTML, reply_markup = await kb.todoReplyKB(language_code))
        return
    elif message.text == "My profile":
        tg_id = message.from_user.id
        experience = await getExp(tg_id)
        userExperience = experience // 1000
        user_name = message.from_user.first_name
        animation = FSInputFile("/Users/admin/Documents/Python/zlp/ToDoBot/img/giphy.gif")
        profile_message = Message.get_message(language_code, "profile").format(
                                                                                    user_name = user_name,
                                                                                    userExperience = userExperience,
                                                                                    experience = experience
                                                                                    )
        await message.answer_animation(
                                        animation = animation,
                                        caption = profile_message,
                                        parse_mode = ParseMode.HTML
                                        )   

###########
"""Tasks"""
###########

@router.message(UserState.todo)
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
        await message.answer(Message.get_message(language_code, "taskslist"), reply_markup = await kb.editTasks(message.from_user.id)) # переделать на редактирование
    if len(message.text) >= 100:
        await message.answer(Message.get_message(language_code, "taskLength"))
        return
    if message.text.startswith("/"):
        return
    if message.text != "My tasks" and message.text != "🏠 Home" and message.text != "Info" and message.text != "Edit task":
        await message.answer(Message.get_message(language_code, "addTask"))
        await addTask(message.from_user.id, message.text)

@router.callback_query(F.data.startswith("deltask_"))
async def delete_task(callback: CallbackQuery, language_code: str):
    await callback.answer("Task completed successfully ✅")
    await deleteTask(callback.data.split("_")[1])
    await callback.message.delete()
    await callback.message.answer(Message.get_message(language_code, "deletTaskList"), reply_markup = await kb.delTasks(callback.from_user.id))

@router.callback_query(F.data.startswith("edittask_"))
async def edit_task(callback: CallbackQuery, language_code: str, state: FSMContext):
    await callback.answer("The task to be edited is selected ✅")
    await callback.message.delete()
    taskId = callback.data.split("_")[1]
    task = await getTaskById(taskId)
    await state.set_state(TaskState.taskEdit)
    await state.update_data(taskId = taskId)
    await callback.message.answer(f"Current text: {task}\n\nPlease enter new text for your task:")

@router.message(TaskState.taskEdit)
async def editTask(message: Message, state: FSMContext, language_code: str):
    newText = message.text
    data = await state.get_data()
    taskId = data['taskId']
    await editTaskInDB(taskId, newText)
    await state.set_state(UserState.todo)
    await message.answer("Task updated successfully!", reply_markup = await kb.delTasks(message.from_user.id))

############
"""habits"""
############

@router.message(UserState.habits)
async def habit_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == "My habits":
        await message.answer(Message.get_message(language_code, "habitsList"), reply_markup = await kb.delHabits(message.from_user.id))
    elif message.text == "Add habit":
        await state.set_state(HabitState.habitText)
        await message.answer(Message.get_message(language_code, "addHabit"), reply_markup = await kb.addHabitReplyKB(language_code))
    elif message.text == "🏠 Home":
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))
        return
    elif message.text == "Info":
        await message.answer(Message.get_message(language_code, "habitInfo"), parse_mode=ParseMode.HTML)
    elif message.text == "Info":
        await message.answer(Message.get_message(language_code, "todayHabits"), parse_mode=ParseMode.HTML)

@router.callback_query(F.data.startswith("delhabit_"))
async def delete_habit(callback: CallbackQuery, language_code: str):
    await callback.answer("Habit deleted successfully ✅")
    await deleteHabit(callback.data.split("_")[1])
    await callback.message.delete()
    await callback.message.answer(Message.get_message(language_code, "deletTaskList"), reply_markup = await kb.delTasks(callback.from_user.id))

async def handle_special_commands(message: Message, state: FSMContext, language_code: str):
    if message.text == "🏠 Home":
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup=await kb.startReplyKb(language_code))
        return True
    elif message.text == "🔙 Habit":
        await state.set_state(UserState.habits)
        await message.answer(Message.get_message(language_code, "habitStart"), parse_mode=ParseMode.HTML, reply_markup=await kb.habitsReplyKB(language_code))
        return True
    return False

@router.message(HabitState.habitText)
async def addHabit_handler(message: Message, state: FSMContext, language_code: str):
    if await handle_special_commands(message, state, language_code):
        return
    
    await state.update_data(habit_text = message.text)
    await state.set_state(HabitState.choosingDays)
    await message.answer("Enter days (1-7)")

@router.message(HabitState.choosingDays)
async def addHabitDays(message: Message, state: FSMContext, language_code: str):
    if await handle_special_commands(message, state, language_code):
        return
    
    await state.update_data(habit_days = message.text)
    await state.set_state(HabitState.setExp)
    await message.answer("Enter exp (10-100)")

@router.message(HabitState.setExp)
async def addHabitExp(message: Message, state: FSMContext, language_code: str):
    if await handle_special_commands(message, state, language_code):
        return
    
    try:
        habit_experience = int(message.text)
        if not 10 <= habit_experience <= 100:
            await message.answer("Experience must be between 10 and 100")
            return
    except ValueError:
        await message.answer("Enter a valid number")
        return
    
    habit_data = await state.get_data()
    await addHabit(message.from_user.id, habit_data.get("habit_text"), habit_data.get("habit_days"), habit_experience)
    await message.answer("Your habit has been successfully created!\nEnter new habit or press button to go back")
    await state.set_state(HabitState.habitText) 