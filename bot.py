from telebot import TeleBot, types
from dotenv import load_dotenv
import os
import nltk
from nltk.corpus import wordnet

# دانلود دیتابیس wordnet (در صورت عدم وجود)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = TeleBot(BOT_TOKEN, threaded=False)

user_state = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Get Definition")
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
    user_text = message.text.strip().lower() # کلمه را کوچک می‌کنیم برای جستجوی بهتر

    mode = user_state.get(user_id)

    if mode != "Definition":
        bot.reply_to(message, "Please select 'Get Definition' first from the options.")
        return

    bot.send_chat_action(message.chat.id, "typing")

    # --- جستجوی کلمه با استفاده از NLTK (WordNet) ---
    synsets = wordnet.synsets(user_text)
    
    if not synsets:
        bot.reply_to(message, f"Sorry, I couldn't find a definition for '{user_text}'. Please check the spelling.")
        return

    # استخراج تعاریف و دسته‌بندی بر اساس نوع کلمه (POS)
    definitions_dict = {}
    for syn in synsets:
        pos = syn.pos()
        definition = syn.definition()
        if pos not in definitions_dict:
            definitions_dict[pos] = []
        if definition not in definitions_dict[pos]:
            definitions_dict[pos].append(definition)

    # فرمت دهی خروجی
    response_text = f"📖 **Word:** {user_text}\n\n"
    for pos, def_list in definitions_dict.items():
        response_text += f"*{pos}:*\n"
        for i, definition in enumerate(def_list[:3]): # نمایش حداکثر 3 تعریف برای هر نوع
            response_text += f"{i+1}. {definition}\n"
        response_text += "\n"

    bot.reply_to(message, response_text, parse_mode="Markdown")

bot.polling()