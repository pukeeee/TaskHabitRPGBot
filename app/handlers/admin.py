from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from app.l10n import Message as L10nMessage
from database.repositories import (
    get_all_active_users
)
from app.fsm import UserState, UserRPG, Admin
from app.keyboards import (
    startReplyKb, adminKb, broadcastTypeKeyboard, checkBroadcastKeyboard
)


router = Router()
router.name = 'admin'



@router.callback_query(F.data == "broadcast")
async def handle_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Choose broadcast type:", reply_markup = await broadcastTypeKeyboard())
    await callback.answer()


@router.callback_query(F.data == "broadcast_text")
async def start_text_broadcast(callback: CallbackQuery, state: FSMContext):
    """Начало создания текстовой рассылки"""
    await callback.message.edit_text("Send message text:")
    await state.set_state(Admin.broadcast_text)
    await callback.answer()



@router.callback_query(F.data == "broadcast_pic")
async def start_pic_broadcast(callback: CallbackQuery, state: FSMContext):
    """Начало создания рассылки с картинкой"""
    await callback.message.edit_text("Send message text first:")
    await state.set_state(Admin.broadcast_text)
    await state.update_data(with_picture=True)
    await callback.answer()



@router.message(Admin.broadcast_text)
async def handle_broadcast_text(message: Message, state: FSMContext):
    """Обработка текста рассылки"""
    broadcast_text = message.html_text

    if len(broadcast_text) > 500:
        await message.answer("Message is too long. Please shorten it.")
        return

    await state.update_data(broadcast_text=broadcast_text)
    
    data = await state.get_data()
    if data.get("with_picture"):
        await state.set_state(Admin.broadcast_pic)
        await message.answer("Now send the picture:")
    else:
        keyboard = await checkBroadcastKeyboard()
        await message.answer(
            f"⬇️ Check broadcast text ⬇️\n\n{broadcast_text}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )



@router.message(Admin.broadcast_pic)
async def handle_broadcast_pic(message: Message, state: FSMContext):
    """Обработка картинки для рассылки"""
    if not message.photo:
        await message.answer("Please send a picture")
        return

    photo = message.photo[-1]
    file_id = photo.file_id
    
    await state.update_data(broadcast_picture=file_id)
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text")
    
    keyboard = await checkBroadcastKeyboard()
    await message.answer_photo(
        photo=file_id,
        caption=f"⬇️ Check broadcast text ⬇️\n\n{broadcast_text}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )



@router.callback_query(F.data == "send_broadcast")
async def send_broadcast(callback: CallbackQuery, state: FSMContext):
    """Отправка рассылки всем пользователям"""
    try:
        data = await state.get_data()
        broadcast_text = data.get("broadcast_text")
        broadcast_picture = data.get("broadcast_picture")
        
        users = await get_all_active_users()
        sent_count = 0
        error_count = 0

        for user_id in users:
            try:
                if broadcast_picture:
                    await callback.bot.send_photo(
                        chat_id=user_id,
                        photo=broadcast_picture,
                        caption=broadcast_text,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await callback.bot.send_message(
                        chat_id=user_id,
                        text=broadcast_text,
                        parse_mode=ParseMode.HTML
                    )
                sent_count += 1
            except Exception as e:
                print(f"Error sending broadcast to {user_id}: {e}")
                error_count += 1

        # Отправляем новое сообщение со статистикой вместо редактирования
        await callback.message.delete()  # Удаляем сообщение с превью
        await callback.message.answer(
            f"Broadcast completed!\n"
            f"✅ Successfully sent: {sent_count}\n"
            f"❌ Errors: {error_count}"
        )
        
        await state.clear()
        await callback.answer()
        
    except Exception as e:
        print(f"Error in broadcast: {e}")
        await callback.answer("Error sending broadcast", show_alert=True)



@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Отмена рассылки"""
    await state.clear()
    await callback.message.edit_text("Broadcast cancelled")
    await callback.answer()



@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    """Возвращение в главное меню админа"""
    await state.set_state(Admin.admin)
    
    await callback.message.edit_text("Admin panel", reply_markup = await adminKb())
    await callback.answer()