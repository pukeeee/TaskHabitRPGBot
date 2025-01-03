import telebot
import requests
from telebot import types
from random import choice

bot = telebot.TeleBot("token")
weatherAPI = "token"

user_states = {}
STATE_HOME = "home"
STATE_WEATHER = "weather"
STATE_PASSWORD = "password"
STATE_PASSWORD_SPECIALS = "password_specials"

def home_page(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
    btn_weather = types.KeyboardButton("Weather")
    btn_password = types.KeyboardButton("Password")
    btn_home = types.KeyboardButton("Home")
    keyboard.add(btn_weather, btn_home, btn_password)
    bot.send_message(chat_id, "Click button below", reply_markup = keyboard)
    user_states[chat_id] = STATE_HOME

@bot.message_handler(commands=["start"])
def start_func(message):
    file = open("/Users/admin/Documents/Python/pet/firstTGbot/chery.jpeg", "rb")
    bot.send_photo(message.chat.id, file)
    bot.send_message(message.chat.id, "<b>Chinaaaaaazes</b>", parse_mode = "HTML")
    bot.send_message(message.chat.id, f"Privet {message.from_user.first_name}")
    bot.send_message(message.chat.id, f"Main bot functions:\n- Weather app\n- Password generator")
    home_page(message.chat.id)
    
@bot.message_handler(commands=["help"])
def help_func(message):
    bot.send_message(message.chat.id, "ДОПОМОГИ НЕ БУДЕ")

@bot.message_handler(commands=["site"])
def site_func(message):
    bot.send_message(message.chat.id, "<a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'>YouTube</a>", parse_mode='HTML', disable_web_page_preview=True)

@bot.message_handler(func = lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    
    state = user_states.get(chat_id, STATE_HOME)
    if state == STATE_HOME:
        if text == "Weather":
            bot.send_message(chat_id, "Weather app. Enter city name:")
            user_states[chat_id] = STATE_WEATHER
            bot.register_next_step_handler(message, weather_func)
        elif text == "Password":
            bot.send_message(chat_id, "Password generator app. Enter password length (1-99):")
            user_states[chat_id] = STATE_PASSWORD
            bot.register_next_step_handler(message, password_func)
        elif text == "Home":
            bot.send_message(chat_id, "You are already there")
        else:
            bot.send_message(chat_id, "Please click button")
    elif text == "Home":
        home_page(chat_id)
    else:
        bot.send_message(chat_id, "Choose 'Home' button to go home page")

def weather_func(message):
    city = message.text.strip()
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weatherAPI}&units=metric")
    data = response.json()
    temp = data["main"]["temp"]
    weather_desc = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    weather_message = (
        f"Weather in {city}:\n"
        f"Temperature: {temp}°C\n"
        f"Description: {weather_desc}\n"
        f"Humidity: {humidity}%\n"
        f"Wind speed: {wind_speed} m/s"
    )
    bot.reply_to(message, weather_message, reply_markup = anotherCityCreateInLineKeyboard())

def password_func(message):
    try:
        pswrdlength = int(message.text.strip())
        if 1 <= pswrdlength <= 99:
            user_states[message.chat.id] = {"state": STATE_PASSWORD_SPECIALS, "pswrdlength": pswrdlength}
            bot.send_message(message.chat.id, "Add special characters to the password?", reply_markup = specCharsCreateInLineKeyboard())
        else:
            bot.send_message(message.chat.id, "Enter a valid number between 1 and 99:")
            bot.register_next_step_handler(message, password_func)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number")
        bot.register_next_step_handler(message, password_func)

def handleSpecialCharacters(chat_id, specsign):
    if specsign in ["yes", "no"]:
        pswrdlength = user_states[chat_id]["pswrdlength"]
        password = pswrdgen(pswrdlength, specsign)
        bot.send_message(chat_id, f"Your password:")
        bot.send_message(chat_id, {password}, reply_markup = passwordCreateInlineKeyboard())
    else:
        bot.send_message(chat_id, "Invalid input. Please try again.")

def pswrdgen(pswrdlength, specsign):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    specchars = "!#$%&*+-/=?_~"
    if specsign == "yes":
        chars += specchars
    return ''.join(choice(chars) for _ in range(pswrdlength))  

@bot.callback_query_handler(func = lambda call: True)
def button_click(call):
    chat_id = call.message.chat.id
    if call.data == "recreate":
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id - 1)
        bot.send_message(call.message.chat.id, "Enter the password length (1-99):")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, password_func)
    elif call.data == "delete":
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id - 1)
    elif call.data == "yesAnswer":
        handleSpecialCharacters(chat_id, "yes")
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
    elif call.data == "noAnswer":
        handleSpecialCharacters(chat_id, "no")
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
    elif call.data == "anotherCity":
        bot.send_message(call.message.chat.id, "Weather app. Enter city name:")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, weather_func)

def passwordCreateInlineKeyboard():
    keyboard = types.InlineKeyboardMarkup()
    recreateButton = types.InlineKeyboardButton("Recreate", callback_data = "recreate")
    keyboard.add(recreateButton)
    deleteButton = types.InlineKeyboardButton("Delete", callback_data = "delete")
    keyboard.add(deleteButton)
    return keyboard

def specCharsCreateInLineKeyboard():
    keyboard = types.InlineKeyboardMarkup()
    yesAnswer = types.InlineKeyboardButton("Yes", callback_data = "yesAnswer")
    keyboard.add(yesAnswer)
    noAnswer = types.InlineKeyboardButton("No", callback_data = "noAnswer")
    keyboard.add(noAnswer)
    return keyboard

def anotherCityCreateInLineKeyboard():
    keyboard = types. InlineKeyboardMarkup()
    anotherCity = types.InlineKeyboardButton("Try another city", callback_data = "anotherCity")
    keyboard.add(anotherCity)
    return keyboard

if __name__ == "__main__":
    bot.infinity_polling()