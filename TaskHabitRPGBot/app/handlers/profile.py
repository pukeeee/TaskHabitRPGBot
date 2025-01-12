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
                                saveUserCharacter, getProfileDB)
from app.fsm import UserState, UserRPG
import app.keyboards as kb
from config import IMG_FOLDER

profile = Router()



@profile.message(CommandStart())
async def startCommand(message: Message, language_code: str, state: FSMContext):
    await setUser(message.from_user.id)
    profile = await getProfileDB(message.from_user.id)

    if profile:
        await message.answer(
            Message.get_message(language_code, "start"),
            parse_mode = ParseMode.HTML,
            reply_markup = await kb.startReplyKb(language_code)
        )
        await state.set_state(UserState.startMenu)
    else:
        await state.set_state(UserRPG.setName)
        await message.answer(Message.get_message(language_code, "newCharacter"), parse_mode = ParseMode.HTML)



@profile.message(UserRPG.setName)
async def setName_handler(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    
    if len(new_name) > 25:
        await message.answer(Message.get_message(language_code, "nameLength"))
        return
    await state.update_data(new_name = new_name)

    await state.set_state(UserRPG.setRace)
    await message.answer(Message.get_message(language_code, "race"), reply_markup = await kb.regRase())



@profile.callback_query(F.data.startswith ("raseFolder_"), UserRPG.setRace)
async def setRace_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    folder_name = callback.data[len("raseFolder_"):]
    
    await state.update_data(selected_race_folder = folder_name)
    await state.set_state(UserRPG.setSex)
    await callback.message.edit_text(text = Message.get_message(language_code, "sex"), parse_mode = ParseMode.HTML, 
                                    reply_markup=await kb.regSex(state))
    await callback.answer()



@profile.callback_query(F.data.startswith("sexFolder_"), UserRPG.setSex)
async def setSex_handler(callback: types.CallbackQuery, state: FSMContext, language_code: str):
    folder_name = callback.data[len("sexFolder_"):]

    await state.update_data(selected_sex_folder = folder_name)
    await state.set_state(UserRPG.setClass)
    await callback.message.edit_text(text = Message.get_message(language_code, "class"), reply_markup = await kb.regClass(state))
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
    await send_avatar(callback, img_files, current_index, class_folder_path, state)
    await callback.answer()



def get_img_files(class_folder_path):
    return [f for f in os.listdir(class_folder_path) if f.endswith('.png')]



async def send_avatar(callback: CallbackQuery, img_files: list, current_index: int,
                        class_folder_path: str, state: FSMContext):
    photo_path = os.path.join(class_folder_path, img_files[current_index])
    photo = FSInputFile(photo_path)
    media = types.InputMediaPhoto(media = photo, caption = f"👾 {current_index + 1} / {len(img_files)}")
    await callback.message.edit_media(media = media, reply_markup = await kb.avatarNavigationKB())
    await state.update_data(selected_img = img_files[current_index])



@profile.callback_query(F.data == "prev_gif")
async def prev_avatar(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)
    class_folder_path = data.get('class_folder_path', '')

    current_index = (current_index - 1) % len(img_files)
    await state.update_data(current_index = current_index)
    await send_avatar(callback, img_files, current_index, class_folder_path, state)
    await callback.answer()



@profile.callback_query(F.data == "next_gif")
async def next_avatar(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)
    class_folder_path = data.get('class_folder_path', '')

    current_index = (current_index + 1) % len(img_files)
    await state.update_data(current_index = current_index)
    await send_avatar(callback, img_files, current_index, class_folder_path, state)
    await callback.answer()



@profile.callback_query(F.data == "done_gif")
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
    await callback.message.edit_text(text = Message.get_message(language_code, "characterAdded"), parse_mode = ParseMode.HTML)
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
    if len(new_name) > 25:
        await message.answer(Message.get_message(language_code, "nameLength"))
        return
    await message.answer(Message.get_message(language_code, "nameChanged"))
    await changeNameDB(message.from_user.id, new_name)
    await state.clear()
    await state.set_state(UserState.startMenu) 



@profile.callback_query(F.data == "changeAvatar")
async def changeAvatar_handler(callback: CallbackQuery, state: FSMContext, language_code: str):
    profile = await getProfileDB(callback.from_user.id)
    await state.update_data(new_name = profile.user_name)
    await state.set_state(UserRPG.setRace)
    await callback.message.answer(Message.get_message(language_code, "changeAvatar"), reply_markup = await kb.regRase())
