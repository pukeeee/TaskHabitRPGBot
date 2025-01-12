from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext

from app.messages import Message
from database.requests import (setUser, deleteTask, addTask, getUserDB, 
                                addHabit, deleteHabit, getTaskById, 
                                editTaskInDB, markHabitAsCompleted, changeNameDB,
                                getProfileDB, resetHabit)
from app.fsm import UserState, HabitState, TaskState, UserRPG
import app.keyboards as kb


habit = Router()


@habit.message(UserState.habits)
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
    elif message.text == "Today habits":
        await message.answer(Message.get_message(language_code, "todayHabits"), parse_mode=ParseMode.HTML, 
                                                reply_markup = await kb.todayHabits(message.from_user.id, language_code))



@habit.callback_query(F.data.startswith("delhabit_"))
async def delete_habit(callback: CallbackQuery, language_code: str):
    await callback.answer("Habit deleted successfully ✅")
    await deleteHabit(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "habitsList"), 
                                    reply_markup = await kb.delHabits(callback.from_user.id))



async def handle_special_commands(message: Message, state: FSMContext, language_code: str):
    if message.text == "🏠 Home":
        await state.set_state(UserState.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await kb.startReplyKb(language_code))
        return True
    elif message.text == "🔙 Habit":
        await state.set_state(UserState.habits)
        await message.answer(Message.get_message(language_code, "habitStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await kb.habitsReplyKB(language_code))
        return True
    return False



@habit.message(HabitState.habitText)
async def addHabit_handler(message: Message, state: FSMContext, language_code: str):
    if await handle_special_commands(message, state, language_code):
        return
    await state.update_data(habit_text = message.text)
    await state.set_state(HabitState.choosingDays)
    await message.answer(Message.get_message(language_code, "habitDays"), reply_markup = await kb.selectWeekdaysKB(language_code))



@habit.message(HabitState.choosingDays)
async def addHabitDays(message: Message, state: FSMContext, language_code: str):
    if await handle_special_commands(message, state, language_code):
        return



@habit.message(HabitState.setExp)
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
    habit_text = habit_data.get("habit_text")
    selected_days = habit_data.get("selected_days", [])
    habit_days = daysToBinary(selected_days)
    
    await addHabit(message.from_user.id, habit_text, habit_days, habit_experience)
    await message.answer("Your habit has been successfully created!\nEnter new habit or press button to go back")
    await state.clear()
    await state.set_state(HabitState.habitText) 



def daysToBinary(selected_days):
    days_position = {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thu': 3,
        'fri': 4,
        'sat': 5,
        'sun': 6
    }
    
    binary_list = ['0'] * 7
    for day in selected_days:
        if day in days_position:
            binary_list[days_position[day]] = '1'
    return ''.join(binary_list)



@habit.callback_query(F.data.startswith("habitDays_"))
async def daysSelection(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = callback.data
    if data == "habitDays_done":
        user_data = await state.get_data()
        selected_days = user_data.get("selected_days", [])
        await state.update_data(habit_days=selected_days)
        await callback.message.edit_text(text = "Дни недели сохранены.")
        await state.set_state(HabitState.setExp)
        await callback.message.answer("Enter exp (10-100)")
    else:
        day = data.replace("habitDays_", "")
        user_data = await state.get_data()
        selected_days = user_data.get("selected_days", [])
        if day in selected_days:
            selected_days.remove(day)
        else:
            selected_days.append(day)
        await state.update_data(selected_days = selected_days)
        await callback.message.edit_reply_markup(reply_markup = await kb.selectWeekdaysKB(language_code, selected_days)
        )
    await callback.answer()



@habit.callback_query(F.data.startswith("completedHabit_"))
async def completeTodayHabit(callback: CallbackQuery, language_code: str):
    habitId = callback.data.split("_")[1]
    await markHabitAsCompleted(habitId, callback.from_user.id)
    await callback.answer("Привычка отмечена как выполненная ✅")
    await callback.message.edit_text(text = Message.get_message(language_code, "todayHabits"), parse_mode = ParseMode.HTML, 
                                                reply_markup = await kb.todayHabits(callback.from_user.id, language_code))