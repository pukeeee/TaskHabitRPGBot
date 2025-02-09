from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.types.input_file import FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import random
import os
from config import LEVEL
from app.l10n import Message as L10nMessage
from database.repositories import (
    setUser,
    getUserDB,
    changeNameDB,
    saveUserCharacter,
    getProfileDB,
    getLeaderboard
)
from app.fsm import UserState, UserRPG
from validators import emoji_specSign, letters, compiled_patterns
from app.keyboards import (
    startReplyKb,
    profileInLineKB,
    avatarNavigationKB,
    profileSettngsKB
)
from config import IMG_FOLDER
from PIL import Image
import io

router = Router()
router.name = 'profiles'

# Создадим кэш для файлов
IMAGE_CACHE = {}

async def load_image(filepath: str) -> BufferedInputFile:
    """Загружает изображение в память или берет из кэша"""
    if filepath not in IMAGE_CACHE:
        # Открываем и оптимизируем изображение
        with Image.open(filepath) as img:
            # Конвертируем в RGB если изображение в RGBA
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Создаем буфер для сохранения оптимизированного изображения
            buffer = io.BytesIO()
            # Сохраняем с оптимизацией качества (quality=70 дает хороший баланс между размером и качеством)
            img.save(buffer, format='JPEG', quality=70, optimize=True)
            content = buffer.getvalue()
            IMAGE_CACHE[filepath] = content
            
    return BufferedInputFile(IMAGE_CACHE[filepath], filename=os.path.basename(filepath))



@router.message(UserRPG.setName)
async def setName_handler(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    is_valid, text = await name_validation(new_name, language_code)
    if not is_valid:
        await message.answer(text)
        
    else:
        await state.update_data(new_name = new_name)
        await state.set_state(UserRPG.setAvatar)
        # await message.answer(L10nMessage.get_message(language_code, "race"))
        await setAvatar(message, state, language_code)



@router.message(UserRPG.setAvatar)
async def setAvatar(message: Message, state: FSMContext, language_code: str):
    # Проверяем существование директории
    if not os.path.exists(IMG_FOLDER):
        print(f"Directory not found: {IMG_FOLDER}")
        await message.answer("Error: Images directory not found")
        return
        
    # Получаем список всех файлов из IMG_FOLDER
    try:
        img_files = [f for f in os.listdir(IMG_FOLDER) if f.startswith('1_') and f.endswith('.png')]
        print(f"Found images: {img_files}")
    except Exception as e:
        print(f"Error listing directory: {e}")
        await message.answer("Error: Cannot list images")
        return
    
    if not img_files:
        await message.answer("No avatars found!")
        return
    
    # Выбираем случайный индекс для первого показа
    current_index = random.randint(0, len(img_files) - 1)
    selected_file = img_files[current_index]
    photo_path = os.path.join(IMG_FOLDER, selected_file)
    
    # Проверяем существование файла
    if not os.path.isfile(photo_path):
        print(f"File not found: {photo_path}")
        await message.answer("Error: Image file not found")
        return
        
    print(f"Trying to send photo: {photo_path}")
    
    try:
        await state.update_data(
            img_files=img_files,
            current_index=current_index
        )
        
        photo = await load_image(photo_path)
        character_name = selected_file.split('_', 1)[1].replace('.png', '')
        
        await message.answer_photo(
            photo=photo,
            caption=f"👾 {character_name}\n{current_index + 1} / {len(img_files)}",
            reply_markup=await avatarNavigationKB(language_code)
        )
    except Exception as e:
        print(f"Error sending photo: {e}")
        print(f"Full photo path: {os.path.abspath(photo_path)}")
        await message.answer("Error: Cannot send photo")



async def send_avatar(callback: CallbackQuery, img_files: list, current_index: int,
                     state: FSMContext, language_code: str):
    photo_path = os.path.join(IMG_FOLDER, img_files[current_index])
    photo = await load_image(photo_path)
    
    character_name = img_files[current_index].split('_', 1)[1].replace('.png', '')
    
    media = types.InputMediaPhoto(
        media=photo,
        caption=f"👾 {character_name}\n{current_index + 1} / {len(img_files)}"
    )
    
    current_file = img_files[current_index]
    await state.update_data(selected_img=current_file)
    
    await callback.message.edit_media(
        media=media,
        reply_markup=await avatarNavigationKB(language_code)
    )



@router.callback_query(F.data == "prev_img")
async def prev_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)

    current_index = (current_index - 1) % len(img_files)
    await state.update_data(current_index=current_index)
    await send_avatar(callback, img_files, current_index, state, language_code)
    await callback.answer()



@router.callback_query(F.data == "next_img")
async def next_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    img_files = data.get('img_files', [])
    current_index = data.get('current_index', 0)

    current_index = (current_index + 1) % len(img_files)
    await state.update_data(current_index=current_index)
    await send_avatar(callback, img_files, current_index, state, language_code)
    await callback.answer()



@router.callback_query(F.data == "done_img")
async def done_avatar(callback: CallbackQuery, state: FSMContext, language_code: str):
    data = await state.get_data()
    user_name = data.get('new_name', '')
    selected_img = data.get('selected_img', '')
    
    print(f"Saving character with name: {user_name}, avatar: {selected_img}")  # Для отладки
    
    if not selected_img:
        print("No avatar selected!")
        await callback.answer("Please select an avatar first")
        return
    
    try:
        await saveUserCharacter(
            tg_id=callback.from_user.id,
            user_name=user_name,
            avatar=selected_img
        )
        
        await callback.message.delete()
        await callback.message.answer(
            text=L10nMessage.get_message(language_code, "characterAdded"), 
            parse_mode=ParseMode.HTML
        )
        await callback.message.answer(
            L10nMessage.get_message(language_code, "start"), 
            parse_mode=ParseMode.HTML,
            reply_markup=await startReplyKb(language_code)
        )
        await state.clear()
        await state.set_state(UserState.startMenu)
    except Exception as e:
        print(f"Error saving character: {e}")
        await callback.message.answer("Error saving character")
    
    await callback.answer()



@router.callback_query(F.data == "changeName")
async def changeName(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.answer(L10nMessage.get_message(language_code, "changeName"))
    await state.set_state(UserRPG.changeName)



@router.message(UserRPG.changeName)
async def changeName(message: Message, state: FSMContext, language_code: str):
    new_name = message.text.strip() 
    is_valid, text = await name_validation(new_name, language_code)
    if not is_valid:
        await message.answer(text)
    else:
        await message.answer(L10nMessage.get_message(language_code, "nameChanged"))
        await changeNameDB(message.from_user.id, new_name)
        await state.clear()
        await state.set_state(UserState.startMenu) 



async def name_validation(new_name: str, language_code: str) -> tuple[bool, str]:
    for pattern in compiled_patterns:
        if pattern.search(new_name):
            text = L10nMessage.get_message(language_code, "nameBad")
            return False, text 
    
    if len(new_name) < 3 or len(new_name) >= 15:
        text = L10nMessage.get_message(language_code, "nameLength")
        return False, text
    
    elif emoji_specSign.search(new_name):
        text = L10nMessage.get_message(language_code, "nameEmoji")
        return False, text
    
    elif not letters.match(new_name):
        text = L10nMessage.get_message(language_code, "nameLetters")
        return False, text
    
    else:
        return True, ""



@router.callback_query(F.data == "changeAvatar")
async def changeAvatar_handler(callback: CallbackQuery, state: FSMContext, language_code: str):
    profile = await getProfileDB(callback.from_user.id)
    await state.update_data(new_name=profile.user_name)
    await state.set_state(UserRPG.setAvatar)
    
    # Получаем список всех файлов из IMG_FOLDER
    img_files = [f for f in os.listdir(IMG_FOLDER) if f.startswith('1_') and f.endswith('.png')]
    
    if not img_files:
        await callback.message.answer("No avatars found!")
        return
    
    # Выбираем случайный индекс для первого показа
    current_index = random.randint(0, len(img_files) - 1)
    
    # Сохраняем данные в состояние
    await state.update_data(
        img_files=img_files,
        current_index=current_index
    )
    
    # Отправляем первую картинку
    photo_path = os.path.join(IMG_FOLDER, img_files[current_index])
    photo = await load_image(photo_path)
    
    # Получаем имя персонажа (часть после "_")
    character_name = img_files[current_index].split('_', 1)[1].replace('.png', '')
    
    # Удаляем предыдущее сообщение с профилем
    await callback.message.delete()
    
    # Отправляем новое сообщение с выбором аватара
    await callback.message.answer_photo(
        photo=photo,
        caption=f"👾 {character_name}\n{current_index + 1} / {len(img_files)}",
        reply_markup=await avatarNavigationKB(language_code)
    )
    
    await callback.answer()



@router.callback_query(F.data == "leaderboard")
async def leaderboardMessage(callback: CallbackQuery, state: FSMContext, language_code: str):
    leaderboard = await generateLeaderboard()
    await callback.message.answer(leaderboard, parse_mode = ParseMode.HTML)



async def generateLeaderboard():
    leaderboard = await getLeaderboard()
    message = "<b>🏆 Leaderboard 🏆</b>\n\n"
    for index, (user_name, experience) in enumerate(leaderboard, start=1):
        message += f"{index}. {user_name}: {experience} XP\n"
    return message



async def profileMessage(message: Message, state: FSMContext, language_code: str):
    user = await getUserDB(message.from_user.id)
    profile = await getProfileDB(message.from_user.id)
    
    user_name = profile.user_name
    level = (user.experience // 1000) + 1
    experience = user.experience

    # Определяем префикс для аватара в зависимости от уровня
    if level >= LEVEL[4]:
        avatar_prefix = str(LEVEL[4])
    elif level >= LEVEL[3]:
        avatar_prefix = str(LEVEL[3])
    elif level >= LEVEL[2]:
        avatar_prefix = str(LEVEL[2])
    else:
        avatar_prefix = str(LEVEL[1])

    # Получаем имя файла аватара из БД
    db_avatar = profile.avatar
    # Добавляем расширение .png, если его нет
    if not db_avatar.endswith('.png'):
        db_avatar += '.png'
    
    # Формируем имя файла с префиксом уровня
    avatar_filename = f"{avatar_prefix}_{db_avatar}"
    
    # Полный путь к файлу аватара
    avatar_file = os.path.join(IMG_FOLDER, avatar_filename)
    
    print(f"Loading avatar: {avatar_file}")  # Для отладки
    
    # Проверяем существование файла
    if not os.path.isfile(avatar_file):
        print(f"Avatar file not found: {avatar_file}")
        # Можно добавить fallback на дефолтную картинку
        return
    
    profile_message = L10nMessage.get_message(language_code, "profile").format(
        user_name=user_name,
        userLevel=level,
        experience=experience
    )
    
    try:
        photo = await load_image(avatar_file)
        await message.answer_photo(
            photo=photo,
            caption=profile_message,
            parse_mode=ParseMode.HTML,
            reply_markup=await profileInLineKB(language_code)
        )
    except Exception as e:
        print(f"Error loading avatar: {avatar_file}")
        print(f"Error details: {e}")



@router.callback_query(F.data == "profileSettings")
async def profileSettings(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_reply_markup(
        reply_markup = await profileSettngsKB(language_code)
    )
    await callback.answer()



@router.callback_query(F.data == "backToProfile")
async def backToProfile(callback: CallbackQuery, state: FSMContext, language_code: str):
    await callback.message.edit_reply_markup(
        reply_markup = await profileInLineKB(language_code)
    )
    await callback.answer()