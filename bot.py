# from telebot import TeleBot, types
# from dotenv import load_dotenv
# import os
# import nltk
# from nltk.corpus import wordnet

# # دانلود دیتابیس wordnet (در صورت عدم وجود)
# try:
#     nltk.data.find('corpora/wordnet')
# except LookupError:
#     nltk.download('wordnet')

# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")

# bot = TeleBot(BOT_TOKEN, threaded=False)

# user_state = {}

# @bot.message_handler(commands=["start"])
# def send_welcome(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     markup.add("Get Definition")
#     bot.send_message(
#         message.chat.id,
#         "Hello,\nI'm your English Dictionary Bot. Please select 'Get Definition' and then send an English word.",
#         reply_markup=markup
#     )

# @bot.message_handler(func=lambda message: message.text == "Get Definition")
# def choose_mode(message):
#     user_id = message.from_user.id
#     user_state[user_id] = "Definition"
#     bot.reply_to(message, "✅ Mode set to Definition. Now send me an English word.")

# @bot.message_handler(content_types=["text"])
# def handle_text(message):
#     user_id = message.from_user.id
#     user_text = message.text.strip().lower() # کلمه را کوچک می‌کنیم برای جستجوی بهتر

#     mode = user_state.get(user_id)

#     if mode != "Definition":
#         bot.reply_to(message, "Please select 'Get Definition' first from the options.")
#         return

#     bot.send_chat_action(message.chat.id, "typing")

#     # --- جستجوی کلمه با استفاده از NLTK (WordNet) ---
#     synsets = wordnet.synsets(user_text)
    
#     if not synsets:
#         bot.reply_to(message, f"Sorry, I couldn't find a definition for '{user_text}'. Please check the spelling.")
#         return

#     # استخراج تعاریف و دسته‌بندی بر اساس نوع کلمه (POS)
#     definitions_dict = {}
#     for syn in synsets:
#         pos = syn.pos()
#         definition = syn.definition()
#         if pos not in definitions_dict:
#             definitions_dict[pos] = []
#         if definition not in definitions_dict[pos]:
#             definitions_dict[pos].append(definition)

#     # فرمت دهی خروجی
#     response_text = f"📖 **Word:** {user_text}\n\n"
#     for pos, def_list in definitions_dict.items():
#         response_text += f"*{pos}:*\n"
#         for i, definition in enumerate(def_list[:3]): # نمایش حداکثر 3 تعریف برای هر نوع
#             response_text += f"{i+1}. {definition}\n"
#         response_text += "\n"

#     bot.reply_to(message, response_text, parse_mode="Markdown")

# bot.polling()
import telebot
from telebot import types
from dotenv import load_dotenv
import os
import nltk
from nltk.corpus import wordnet

# --- تنظیمات اولیه ربات ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# --- دانلود داده‌های NLTK (WordNet) ---
# اضافه کردن مسیر فعلی به path برای جلوگیری از خطا در محیط‌های محدود
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

def download_nltk_data():
    try:
        nltk.data.find('corpora/wordnet')
        print("WordNet corpus already downloaded.")
    except LookupError:
        print("WordNet corpus not found. Downloading...")
        # دانلود در حالت بیصدا (quiet) برای جلوگیری از نمایش پیام‌های طولانی در لاگ
        nltk.download('wordnet', quiet=True)
        print("WordNet corpus downloaded successfully.")

# اجرای تابع دانلود هنگام اجرای اسکریپت
download_nltk_data()

# --- مدیریت وضعیت کاربر ---
# user_state: 'Definition' | None
user_state = {}

# --- دستور /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_definition = types.KeyboardButton('Get Definition')
    markup.add(btn_definition)
    bot.reply_to(message, "Welcome! Please use the button below to get a definition.", reply_markup=markup)

# --- پردازش پیام‌های متنی ---
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.from_user.id
    user_text = message.text.strip().lower() # کلمه را کوچک می‌کنیم برای جستجوی بهتر

    # بررسی وضعیت کاربر
    mode = user_state.get(user_id)

    if mode == "Get Definition":
        # نمایش وضعیت "در حال تایپ" به کاربر
        bot.send_chat_action(message.chat.id, "typing")

        # --- جستجوی کلمه با استفاده از NLTK (WordNet) ---
        try:
            synsets = wordnet.synsets(user_text)
        except Exception as e:
            print(f"Error during synset lookup for '{user_text}': {e}")
            bot.reply_to(message, f"An internal error occurred while searching for '{user_text}'. Please try again later.")
            return
            
        if not synsets:
            bot.reply_to(message, f"Sorry, I couldn't find a definition for '{user_text}'. Please check the spelling.")
            return

        # استخراج تعاریف و دسته‌بندی بر اساس نوع کلمه (POS)
        definitions_dict = {}
        for syn in synsets:
            pos = syn.pos() # part of speech (e.g., 'n' for noun, 'v' for verb)
            definition = syn.definition()
            
            # اضافه کردن به دیکشنری فقط در صورتی که قبلا اضافه نشده باشد
            if pos not in definitions_dict:
                definitions_dict[pos] = []
            if definition not in definitions_dict[pos]:
                definitions_dict[pos].append(definition)

        # فرمت دهی خروجی با Markdown
        response_text = f"📖 **Word:** {user_text}\n\n"
        definitions_found = False
        for pos, def_list in definitions_dict.items():
            # نمایش حداکثر 3 تعریف برای هر نوع کلمه
            if def_list:
                definitions_found = True
                # تبدیل POS code به نام کاملتر (اختیاری)
                pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb'}
                display_pos = pos_map.get(pos, pos.upper()) # اگر در map نبود، خودش را نمایش بده

                response_text += f"*{display_pos}:*\n"
                for i, definition in enumerate(def_list[:3]):
                    response_text += f"{i+1}. {definition}\n"
                response_text += "\n"
        
        if not definitions_found:
             bot.reply_to(message, f"Sorry, I couldn't find any definitions for '{user_text}'.")
        else:
            bot.reply_to(message, response_text, parse_mode="Markdown")

    # اگر کاربر پیام را خارج از حالت "Definition" ارسال کند
    elif user_text == 'get definition':
        # اگر کاربر دوباره دکمه را بزند، حالت را تنظیم می‌کنیم
        user_state[user_id] = "Definition"
        bot.send_message(message.chat.id, "Okay, send me the word you want to define.")
    else:
        # اگر کاربر پیام را خارج از حالت "Definition" ارسال کند و متن آن هم دکمه نباشد
        # یک پیام راهنما ارسال می‌کنیم، نه reply، تا از خطا جلوگیری شود.
        bot.send_message(message.chat.id, "Please use the 'Get Definition' button or send 'Get Definition' again to start.")


# --- پردازش دکمه‌ها (اگر لازم بود) ---
# این بخش را در حال حاضر غیرفعال می‌کنیم چون با پیام متنی 'get definition' کار می‌کنیم
# @bot.callback_query_handler(func=lambda call: True)
# def handle_callback(call):
#     pass

# --- اجرای ربات ---
if __name__ == '__main__':
    print("Bot is starting...")
    # استفاده از polling برای اجرای ربات
    # threaded=False در constructor باعث می‌شود اینجا از polling استفاده کنیم
    bot.polling(none_stop=True)
