from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import random
import os
from app.messages import Message
from database.requests import (setUser, getUserDB,changeNameDB, 
                                saveUserCharacter, getProfileDB, getLeaderboard)
from app.fsm import UserState, UserRPG
from validators import emoji_specSign, letters, compiled_patterns
import app.keyboards as kb
from config import IMG_FOLDER

profile = Router()



@profile.message(UserRPG.setName)
async def setName_handler(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    is_valid, text = await name_validation(new_name, language_code)
    if not is_valid:
        await message.answer(text)
        
    else:
        await state.update_data(new_name = new_name)
        await state.set_state(UserRPG.setRace)
        await message.answer(Message.get_message(language_code, "race"), reply_markup = await kb.regRase())



@profile.callback_query(F.data.startswith ("raseFolder_"), UserRPG.setRace)
async def setRace_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    folder_name = callback.data[len("raseFolder_"):]
    
    await state.update_data(selected_race_folder = folder_name)
    await state.set_state(UserRPG.setSex)
    await callback.message.edit_text(text = Message.get_message(language_code, "sex"), parse_mode = ParseMode.HTML, 
                                    reply_markup = await kb.regSex(state))
    await callback.answer()



@profile.callback_query(F.data == "backToRace")
async def backToRace_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    await state.set_state(UserRPG.setRace)
    await callback.message.edit_text(Message.get_message(language_code, "race"), reply_markup = await kb.regRase())
    await callback.answer()



@profile.callback_query(F.data.startswith("sexFolder_"), UserRPG.setSex)
async def setSex_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    folder_name = callback.data[len("sexFolder_"):]

    await state.update_data(selected_sex_folder = folder_name)
    await state.set_state(UserRPG.setClass)
    await callback.message.edit_text(text = Message.get_message(language_code, "class"), reply_markup = await kb.regClass(state))
    await callback.answer()



@profile.callback_query(F.data == "backToSex")
async def backToRace_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    await state.set_state(UserRPG.setSex)
    await callback.message.edit_text(text = Message.get_message(language_code, "sex"), parse_mode = ParseMode.HTML, 
                                    reply_markup = await kb.regSex(state))
    await callback.answer()



@profile.callback_query(F.data.startswith("classFolder_"), UserRPG.setClass)
async def setClass_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    class_name = callback.data[len("classFolder_"):]
    await state.update_data(selected_class_folder = class_name)
    data = await state.get_data()
    selected_race_folder = data.get('selected_race_folder')
    selected_sex_folder = data.get('selected_sex_folder')
    class_folder_path = os.path.join(IMG_FOLDER, selected_race_folder, selected_sex_folder, class_name)
    img_files = get_img_files(class_folder_path)

    current_index = random.randint(0, len(img_files) - 1)
    await state.update_data(img_files = img_files, current_index = current_index, class_folder_path = class_folder_path)
    await send_avatar(callback, img_files, current_index, class_folder_path, state, language_code)
    await callback.answer()



@profile.callback_query(F.data == "backToClass")
async def backToRace_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    await state.set_state(UserRPG.setClass)
    await callback.message.delete()
    await callback.message.answer(text = Message.get_message(language_code, "class"), reply_markup = await kb.regClass(state))
    await callback.answer()



def get_img_files(class_folder_path):
    return [f for f in os.listdir(class_folder_path) if f.endswith('.png')]



async def send_avatar(callback: CallbackQuery, img_files: list, current_index: int,
                        class_folder_path: str, state: FSMContext, language_code: str):
    photo_path = os.path.join(class_folder_path, img_files[current_index])
    photo = FSInputFile(photo_path)
    media = types.InputMediaPhoto(media = photo, caption = f"👾 {current_index + 1} / {len(img_files)}")
    await callback.message.edit_media(media = media, reply_markup = await kb.avatarNavigationKB(language_code))
    await state.update_data(selected_img = img_files[current_index])



@profile.callback_query(F.data == "prev_img")
async def prev_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)
    class_folder_path = data.get('class_folder_path', '')

    current_index = (current_index - 1) % len(img_files)
    await state.update_data(current_index = current_index)
    await send_avatar(callback, img_files, current_index, class_folder_path, state, language_code)
    await callback.answer()



@profile.callback_query(F.data == "next_img")
async def next_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)
    class_folder_path = data.get('class_folder_path', '')

    current_index = (current_index + 1) % len(img_files)
    await state.update_data(current_index = current_index)
    await send_avatar(callback, img_files, current_index, class_folder_path, state, language_code)
    await callback.answer()



@profile.callback_query(F.data == "done_img")
async def done_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    user_name = data.get('new_name', '')
    selected_img = data.get('selected_img', '')
    race = data.get('selected_race_folder', '')
    sex = data.get('selected_sex_folder', '')
    clas = data.get('selected_class_folder', '')

    await saveUserCharacter(
        tg_id = callback.from_user.id,
        user_name = user_name,
        avatar = selected_img,
        race = race,
        sex = sex,
        clas = clas
    )
    await callback.message.delete()
    await callback.message.answer(text = Message.get_message(language_code, "characterAdded"), parse_mode = ParseMode.HTML)
    await callback.message.answer(Message.get_message(language_code, "start"), parse_mode = ParseMode.HTML, 
                                    reply_markup = await kb.startReplyKb(language_code))
    await state.clear()
    await state.set_state(UserState.startMenu)
    await callback.answer()



@profile.callback_query(F.data == "changeName")
async def changeName(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.answer(Message.get_message(language_code, "changeName"))
    await state.set_state(UserRPG.changeName)



@profile.message(UserRPG.changeName)
async def changeName(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    is_valid, text = await name_validation(new_name, language_code)
    if not is_valid:
        await message.answer(text)
    else:
        await message.answer(Message.get_message(language_code, "nameChanged"))
        await changeNameDB(message.from_user.id, new_name)
        await state.clear()
        await state.set_state(UserState.startMenu) 



async def name_validation(new_name: str, language_code: str) -> tuple[bool, str]:
    for pattern in compiled_patterns:
        if pattern.search(new_name):
            text = Message.get_message(language_code, "nameBad")
            return False, text 
    
    if len(new_name) < 3 or len(new_name) >= 15:
        text = Message.get_message(language_code, "nameLength")
        return False, text
    
    elif emoji_specSign.search(new_name):
        text = Message.get_message(language_code, "nameEmoji")
        return False, text
    
    elif not letters.match(new_name):
        text = Message.get_message(language_code, "nameLetters")
        return False, text
    
    else:
        return True, ""



@profile.callback_query(F.data == "changeAvatar")
async def changeAvatar_handler(callback: CallbackQuery, state: FSMContext, language_code: str):
    profile = await getProfileDB(callback.from_user.id)
    await state.update_data(new_name = profile.user_name)
    await state.set_state(UserRPG.setRace)
    await callback.message.answer(Message.get_message(language_code, "changeAvatar"), reply_markup = await kb.regRase())



@profile.callback_query(F.data == "leaderboard")
async def leaderboardMessage(callback: CallbackQuery, state: FSMContext, language_code: str):
    leaderboard = await generateLeaderboard()
    await callback.message.answer(leaderboard, parse_mode=ParseMode.HTML)



async def generateLeaderboard():
    leaderboard = await getLeaderboard()
    message = "<b>🏆 Leaderboard 🏆</b>\n\n"
    for index, (user_name, experience) in enumerate(leaderboard, start=1):
        message += f"{index}. {user_name}: {experience} XP\n"
    return message