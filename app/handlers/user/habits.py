from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone
from app.l10n.l10n import Message
from database.repositories import (
    addHabit,
    editHabit,
    deleteHabit,
    getHabits,
    getHabitById,
    getTodayHabits,
    markHabitAsCompleted,
    getUserDB,
    checkHabitsCount
)
from app.states import User, Habit
from app.keyboards import (
    habitsReplyKB,
    addHabitReplyKB,
    habitsList,
    deleteHabits,
    editHabits,
    selectWeekdaysKB,
    todayHabits,
    startReplyKb, setHabitComplexity
)
from app.core.utils.exp_calc import habitExpCalc


router = Router()
router.name = 'habits'


@router.message(User.habits)
async def habit_handler(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "habitListButton"):
        habitListMessage = await getHabitListMessage(language_code, message.from_user.id)
        await message.answer(habitListMessage, reply_markup = await habitsList(message.from_user.id, language_code))
    
    elif message.text == Message.get_message(language_code, "addHabitButton"):
        await state.set_state(Habit.habitText)
        await message.answer(Message.get_message(language_code, "addHabit"), reply_markup = await addHabitReplyKB(language_code))
    
    elif message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(User.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))
        return
    
    elif message.text == Message.get_message(language_code, "statisticButton"):
        stat = await getUserDB(message.from_user.id)
        
        start_date = datetime.fromtimestamp(stat.start_date, tz=timezone.utc)
        formatted_start_date = start_date.strftime("%d.%m.%y")
        days_counter = (datetime.now(tz=timezone.utc) - start_date).days
        all_habits_count = stat.all_habits_count
        
        await message.answer(Message.get_message(language_code, "habitStatistic").format(start_date = formatted_start_date,
                                                                                    days_counter = days_counter,
                                                                                    all_tasks_count = all_habits_count))
    
    elif message.text == Message.get_message(language_code, "todayHabitsButton"):
        await message.answer(Message.get_message(language_code, "todayHabits"), parse_mode=ParseMode.HTML, 
                                                reply_markup = await todayHabits(message.from_user.id, language_code))



async def getHabitListMessage(language_code: str, tg_id):
    habitList = list(await getHabits(tg_id))
    message = Message.get_message(language_code, "habitsList")
    if not habitList:
        message += "\n\n🚽\n\n"
        
    else:
        message += "\n\n"
        for habit in habitList:
            habitExp = f"{habit.experience_points}✨"
            message += f"<code>{habit.complexity:<2} + {habitExp:<5}</code> |   <b>{habit.name}</b>\n"
        message += "\n"
    message += Message.get_message(language_code, "habitMessage")
    
    return message



@router.callback_query(F.data == "deleteHabits")
async def deleteHabitsList(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteHabit"), reply_markup = await deleteHabits(callback.from_user.id))
    await callback.answer()



@router.callback_query(F.data == "editHabits")
async def editHabitsList(callback: CallbackQuery, language_code: str):
    await callback.message.edit_text(text = Message.get_message(language_code, "editHabit"), reply_markup = await editHabits(callback.from_user.id))
    await callback.answer()



@router.callback_query(F.data == "backToHabitsList")
async def backToHabitsList(callback: CallbackQuery, language_code: str):
    habitListMessage = await getHabitListMessage(language_code, callback.from_user.id)
    await callback.message.edit_text(text = habitListMessage, 
                                    reply_markup = await habitsList(callback.from_user.id, language_code))
    await callback.answer()


@router.callback_query(F.data.startswith("delhabit_"))
async def delete_habit(callback: CallbackQuery, language_code: str):
    await callback.answer("✅")
    await deleteHabit(callback.data.split("_")[1])
    await callback.message.edit_text(text = Message.get_message(language_code, "deleteHabit"), 
                                    reply_markup = await deleteHabits(callback.from_user.id))



@router.callback_query(F.data.startswith("edithabit_"))
async def edit_habit(callback: CallbackQuery, language_code: str, state: FSMContext):
    await callback.answer("✏️")
    habitId = callback.data.split("_")[1]
    await getHabitById(habitId)
    await state.update_data(habitId = habitId)
    await state.set_state(Habit.editHabitText)
    await callback.message.edit_text(text = Message.get_message(language_code, "habitEditText"))



@router.message(Habit.editHabitText)
async def editHabitText(message: Message, state: FSMContext, language_code: str):
    if await habitExceptions(message, state, language_code):
        return
    
    text = message.text.strip()
    if len(text) > 100:
        await message.answer(Message.get_message(language_code, "habitLength"))
        
    else:
        await state.update_data(habit_text = text)
        await state.set_state(Habit.editDays)
        await message.answer(Message.get_message(language_code, "habitDays"), reply_markup = await selectWeekdaysKB(language_code))



@router.message(Habit.editDays)
async def editHabitDays(message: Message, state: FSMContext, language_code: str):
    if await habitExceptions(message, state, language_code):
        return





async def habitExceptions(message: Message, state: FSMContext, language_code: str):
    if message.text == Message.get_message(language_code, "homeButton"):
        await state.clear()
        await state.set_state(User.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))
        return True
    
    elif message.text == Message.get_message(language_code, "backToHabitButton"):
        await state.clear()
        await state.set_state(User.habits)
        await message.answer(Message.get_message(language_code, "habitStart"), parse_mode=ParseMode.HTML, 
                            reply_markup = await habitsReplyKB(language_code))
        return True
    
    elif message.text == Message.get_message(language_code, "habitListButton"):
        habitListMessage = await getHabitListMessage(language_code, message.from_user.id)
        await message.answer(habitListMessage, reply_markup = await habitsList(message.from_user.id, language_code))
        await state.clear()
        await state.set_state(User.habits)
        return True
    
    elif message.text == Message.get_message(language_code, "addHabitButton"):
        await state.set_state(Habit.habitText)
        await message.answer(Message.get_message(language_code, "addHabit"), reply_markup = await addHabitReplyKB(language_code))
        await state.clear()
        await state.set_state(User.habits)
        return True
    
    elif message.text == Message.get_message(language_code, "homeButton"):
        await state.set_state(User.startMenu)
        await message.answer(Message.get_message(language_code, "homePage"), reply_markup = await startReplyKb(language_code))
        await state.clear()
        await state.set_state(User.habits)
        return True
    
    elif message.text == Message.get_message(language_code, "statisticButton"):
        await message.answer("Not available now", parse_mode=ParseMode.HTML)
        await state.clear()
        await state.set_state(User.habits)
        return True
    
    elif message.text == Message.get_message(language_code, "todayHabitsButton"):
        await message.answer(Message.get_message(language_code, "todayHabits"), parse_mode=ParseMode.HTML, 
                                                reply_markup = await todayHabits(message.from_user.id, language_code))
        await state.clear()
        await state.set_state(User.habits)
        return True
    
    return False



@router.message(Habit.habitText)
async def addHabit_handler(message: Message, state: FSMContext, language_code: str):
    if await habitExceptions(message, state, language_code):
        return
    
    text = message.text.strip()

    limit = await checkHabitsCount(message.from_user.id)
    
    if limit is None:
        await message.answer("Произошла ошибка при проверке лимита привычек. Пожалуйста, попробуйте позже.")
        return
    
    if limit == False:
        await message.answer(Message.get_message(language_code, "habitLimitReached"))
        
    else:
        if len(text) > 100:
            await message.answer(Message.get_message(language_code, "habitLength"))
        else:
            await state.update_data(habit_text = text)
            await state.set_state(Habit.choosingDays)
            await message.answer(Message.get_message(language_code, "habitDays"), reply_markup = await selectWeekdaysKB(language_code))



@router.message(Habit.choosingDays)
async def addHabitDays(message: Message, state: FSMContext, language_code: str):
    if await habitExceptions(message, state, language_code):
        return



@router.callback_query(Habit.setExp)
async def addHabitExp_callback(callback: CallbackQuery, state: FSMContext, language_code: str):
    if await habitExceptions(callback.message, state, language_code):
        return
    
    complexity = callback.data
    await processHabitExp(callback.from_user.id, complexity, state, language_code, callback.message)



@router.message(Habit.setExp)
async def addHabitExp_message(message: Message, state: FSMContext, language_code: str):
    if await habitExceptions(message, state, language_code):
        return
    
    if message.text in ["🟩", "🟨", "🟪", "🟥"]:
        complexity = message.text
        await processHabitExp(message.from_user.id, complexity, state, language_code, message)
    else:
        await message.answer("Пожалуйста, выберите сложность из предложенных кнопок.")


async def processHabitExp(user_id: int, complexity: str, state: FSMContext, language_code: str, message: Message, is_edit: bool = False):
    habitData = await saveHabit(complexity, state, language_code)
    
    if not habitData.get("habitText") or not habitData.get("habitDays") or not habitData.get("habitExp"):
        await message.answer("Ошибка: данные привычки не найдены. Пожалуйста, попробуйте снова.")
        return
    
    if is_edit:
        habit_data = await state.get_data()
        habitId = habit_data.get("habitId")
        await editHabit(habitId, habitData["habitText"], habitData["habitDays"], habitData["habitExp"], complexity)
        await state.clear()
    else:
        await addHabit(user_id, habitData["habitText"], habitData["habitDays"], habitData["habitExp"], complexity)
        await state.clear()
    
    await message.answer(Message.get_message(language_code, "habitCreated" if not is_edit else "habitEdited"))
    await state.clear()
    await state.set_state(Habit.habitText)



async def saveHabit(complexity, state: FSMContext, language_code: str):
    habit_data = await state.get_data()
    habitText = habit_data.get("habit_text")
    selected_days = habit_data.get("selected_days", [])
    habitDays = daysToBinary(selected_days)
    
    days = len(selected_days)
    
    habitExp = await habitExpCalc(complexity, days)
    
    return {
        "habitText": habitText, "habitDays": habitDays, "habitExp": habitExp
    }



@router.callback_query(Habit.editExp)
async def editHabitExp_callback(callback: CallbackQuery, state: FSMContext, language_code: str):
    if await habitExceptions(callback.message, state, language_code):
        return
    
    complexity = callback.data
    habitData = await saveHabit(complexity, state, language_code)
    
    if not habitData:
        await callback.message.answer("Ошибка: данные привычки не найдены. Пожалуйста, попробуйте снова.")
        return
    
    habit_data = await state.get_data()
    habitId = habit_data.get("habitId")
    
    if not habitId:
        await callback.message.answer("Ошибка: ID привычки не найден. Пожалуйста, попробуйте снова.")
        return
    
    await editHabit(habitId, habitData["habitText"], habitData["habitDays"], habitData["habitExp"], complexity)
    habitListMessage = await getHabitListMessage(language_code, callback.from_user.id)
    await callback.message.edit_text(habitListMessage, reply_markup = await habitsList(callback.from_user.id, language_code))
    await state.clear()
    await state.set_state(User.habits)



@router.message(Habit.editExp)
async def editHabitExp_message(message: Message, state: FSMContext, language_code: str):
    if await habitExceptions(message, state, language_code):
        return
    
    if message.text in ["🟩", "🟨", "🟪", "🟥"]:
        complexity = message.text
        await processHabitExp(message.from_user.id, complexity, state, language_code, message, is_edit=True)
    else:
        await message.answer("Пожалуйста, выберите сложность из предложенных кнопок.")



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



@router.callback_query(F.data.startswith("habitDays_"))
async def daysSelection(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = callback.data
    current_state = await state.get_state()
    
    if data == "habitDays_done":
        user_data = await state.get_data()
        selected_days = user_data.get("selected_days", [])
        
        if not selected_days:
            await callback.answer("⛔️")
            return
        
        if current_state == Habit.choosingDays.state:
            await state.update_data(habit_days = selected_days)
            await callback.answer("✅")
            # await callback.message.edit_text(text = Message.get_message(language_code, "habitDaysSave"))
            await state.set_state(Habit.setExp)
            await callback.message.edit_text(Message.get_message(language_code, "habitExp"), reply_markup = await setHabitComplexity())
        elif current_state == Habit.editDays.state:
            await state.update_data(habit_days = selected_days)
            await callback.answer("✅")
            # await callback.message.edit_text(text = Message.get_message(language_code, "habitDaysSave"))
            await state.set_state(Habit.editExp)
            await callback.message.edit_text(Message.get_message(language_code, "habitExp"), reply_markup = await setHabitComplexity())

    else:
        day = data.replace("habitDays_", "")
        user_data = await state.get_data()
        selected_days = user_data.get("selected_days", [])
        if day in selected_days:
            selected_days.remove(day)
        else:
            selected_days.append(day)
        await state.update_data(selected_days = selected_days)
        await callback.message.edit_reply_markup(reply_markup = await selectWeekdaysKB(language_code, selected_days)
        )
        
    await callback.answer()



@router.callback_query(F.data.startswith("completedHabit_"))
async def completeTodayHabit(callback: CallbackQuery, language_code: str):
    habitId = callback.data.split("_")[1]
    habitExp = callback.data.split("_")[2]
    await markHabitAsCompleted(habitId, callback.from_user.id)
    habitText = Message.get_message(language_code, "habitCompleted")
    await callback.answer(f"{habitText} +{habitExp} ✨")
    await callback.message.edit_text(text = Message.get_message(language_code, "todayHabits"), parse_mode = ParseMode.HTML, 
                                                reply_markup = await todayHabits(callback.from_user.id, language_code))