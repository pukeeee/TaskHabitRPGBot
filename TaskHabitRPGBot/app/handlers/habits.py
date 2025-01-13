from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext

from app.messages import Message
from database.requests import (setUser, getUserDB, 
                                addHabit, editHabit, 
                                editTaskInDB, markHabitAsCompleted, changeNameDB,
                                getProfileDB, resetHabit, deleteHabit, getHabitById)
from app.fsm import UserState, HabitState, TaskState, UserRPG
import app.keyboards as kb


habit = Router()


@habit.message(UserState.habits)
async def habit_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == "My habits":
        await message.answer(Message.get_message(language_code, "habitsList"), reply_markup = await kb.habitsList(message.from_user.id))
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



@habit.callback_query(F.data == "deleteHabits")
async def deleteHabitsList(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = "tap to delete", reply_markup = await kb.deleteHabits(callback.from_user.id))
    await callback.answer()



@habit.callback_query(F.data == "editHabits")
async def editHabitsList(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = "tap to edit", reply_markup = await kb.editHabits(callback.from_user.id))
    await callback.answer()



@habit.callback_query(F.data == "backToHabitsList")
async def backToHabitsList(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "habitsList"), 
                                    reply_markup = await kb.habitsList(callback.from_user.id))
    await callback.answer()


@habit.callback_query(F.data.startswith("delhabit_"))
async def delete_habit(callback: CallbackQuery, language_code: str):
    await callback.answer("Habit deleted successfully ✅")
    await deleteHabit(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "habitsList"), 
                                    reply_markup = await kb.deleteHabits(callback.from_user.id))



@habit.callback_query(F.data.startswith("edithabit_"))
async def edit_habit(callback: CallbackQuery, language_code: str, state: FSMContext):
    await callback.answer("The habit to be edited is selected ✅")
    habitId = callback.data.split("_")[1]
    await getHabitById(habitId)
    await state.update_data(habitId = habitId)
    await state.set_state(HabitState.edithabitText)
    await callback.message.edit_text(text = "Type new habit")



@habit.message(HabitState.edithabitText)
async def editHabitText(message: Message, state: FSMContext, language_code: str):
    new_habit_text = message.text.strip()
    await state.update_data(new_habit_text = new_habit_text)
    await state.set_state(HabitState.editDays)
    await message.answer(Message.get_message(language_code, "habitDays"), reply_markup = await kb.selectWeekdaysKB(language_code))



@habit.message(HabitState.editExp)
async def editHabitExp(message: Message, state: FSMContext, language_code: str):
    try:
        new_habit_experience = int(message.text)
        if not 10 <= new_habit_experience <= 100:
            await message.answer("Experience must be between 10 and 100")
            return
    except ValueError:
        await message.answer("Enter a valid number")
        return
    
    habit_data = await state.get_data()
    habitId = habit_data.get("habitId")
    new_habit_text = habit_data.get("new_habit_text")
    selected_days = habit_data.get("selected_days", [])
    habit_days = daysToBinary(selected_days)
    
    await editHabit(habitId, new_habit_text, habit_days, new_habit_experience)
    await message.answer("Your habit has been successfully edited!\nEnter new habit or press button to go back")
    await state.clear()
    await state.set_state(UserState.habits) 



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
    current_state = await state.get_state()
    
    if data == "habitDays_done":
        user_data = await state.get_data()
        selected_days = user_data.get("selected_days", [])
        
        if not selected_days:
            await callback.answer("Выберите хотя бы один день недели!", show_alert=True)
            return
        
        if current_state == HabitState.choosingDays.state:
            await state.update_data(habit_days = selected_days)
            await callback.message.edit_text(text = "Дни недели сохранены.")
            await state.set_state(HabitState.setExp)
            await callback.message.answer("Enter exp (10-100)")
        elif current_state == HabitState.editDays.state:
            await state.update_data(habit_days = selected_days)
            await callback.message.edit_text(text = "Дни недели для редактируемой привычки обновлены.")
            await state.set_state(HabitState.editExp)
            await callback.message.answer("Введите новый опыт для привычки (10-100)")

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