import telebot
from telebot import types
import os
import yt_dlp
import tempfile

bot = telebot.TeleBot("token")

@bot.message_handler(commands=["start"])
def start_func(message):
    bot.send_message(message.chat.id, "wassuup\nSend me a link to the Tiktok or Reels videos\n\nAND I WILL DOWNLOAD IT FOR YOU")

@bot.message_handler(content_types=["text"])
def handle_message(message):
    chat_id = message.chat.id
    url = message.text
    if "tiktok" in url or "instagram" in url:
        bot.send_message(chat_id, "Downloading...\nPlease wait")
        bot.send_message(chat_id, "Please")
        downloadTiktokReels(url, chat_id)
    else:
        bot.send_message(chat_id, "I can only download videos from Tiktok and Reels!")

def downloadTiktokReels(url, chat_id):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'best',
                'outtmpl': temp_dir + '/%(title)s.%(ext)s',
                'nocheckcertificate': True,
                'nooverwrites': True,
                'noprogress': True,
                'cachedir': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            for file in os.listdir(temp_dir):
                with open(f"{temp_dir}/{file}", "rb") as video:
                    file_path = os.path.join(temp_dir, file)
                    with open(file_path, "rb") as video:
                        bot.send_video(chat_id, video, supports_streaming=True)
    except Exception as e:
        errorMessage = f"Error: {e}"
        bot.send_message(chat_id, errorMessage)

@bot.message_handler(content_types=["document", "photo", "video"])
def anyFile(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Check this", url="https://www.youtube.com/watch?v=OEFen30FAxo&ab_channel=%D0%95%D0%B2%D0%B3%D0%B5%D0%BD%D0%B8%D0%B9%D0%A7%D0%B5%D1%80%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2")
    markup.row(btn1)
    bot.reply_to(message, "Oh no no no no no, u sent me shiiiit", reply_markup = markup)

if __name__ == "__main__":
    bot.infinity_polling()