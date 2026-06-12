from telebot import TeleBot, types
from dotenv import load_dotenv
import os
from PyDictionary import PyDictionary

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = TeleBot(BOT_TOKEN, threaded=False)

# --- PyDictionary برای گرفتن تعریف ---
dictionary = PyDictionary()

user_state = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Get Definition") # تغییر نام دکمه برای وضوح بیشتر
    bot.send_message(
        message.chat.id,
        "Hello,\nI'm your English Dictionary Bot. Please select 'Get Definition' and then send an English word.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Get Definition")
def choose_mode(message):
    user_id = message.from_user.id
    user_state[user_id] = "Definition"
    bot.reply_to(message, "✅ Mode set to Definition. Now send me an English word.")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.from_user.id
    user_text = message.text.strip() # حذف فاصله های اضافی

    mode = user_state.get(user_id)

    if mode != "Definition":
        bot.reply_to(message, "Please select 'Get Definition' first from the options.")
        return

    bot.send_chat_action(message.chat.id, "typing")

    # --- استفاده از PyDictionary برای گرفتن تعریف ---
    try:
        meanings = dictionary.meaning(user_text)

        if not meanings:
            bot.reply_to(message, f"Sorry, I couldn't find a definition for '{user_text}'. Please check the spelling.")
            return

        # فرمت دهی تعریف انگلیسی
        response_text = f"**Word:** {user_text}\n\n**Definition(s):**\n"
        for part_of_speech, def_list in meanings.items():
            if def_list:
                response_text += f"*{part_of_speech}:*\n"
                for definition in def_list:
                    response_text += f"- {definition}\n"
                response_text += "\n" # فاصله بین بخش های مختلف کلمه

        bot.reply_to(message, response_text, parse_mode="Markdown")

    except Exception as e:
        print(f"Error using PyDictionary: {e}")
        bot.reply_to(message, "❌ An error occurred while trying to find the definition.")

bot.polling()
