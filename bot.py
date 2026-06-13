# import telebot
# from telebot import types
# from dotenv import load_dotenv
# import os
# import nltk
# from nltk.corpus import wordnet

# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

# def download_nltk_data():
#     try:
#         nltk.data.find('corpora/wordnet')
#         print("WordNet corpus already downloaded.")
#     except LookupError:
#         print("WordNet corpus not found. Downloading...")
#         nltk.download('wordnet', quiet=True)
#         print("WordNet corpus downloaded successfully.")


# download_nltk_data()


# user_state = {}


# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     btn_definition = types.KeyboardButton('Get Definition')
#     markup.add(btn_definition)
#     bot.reply_to(message, "Welcome! Please use the button below to get a definition.", reply_markup=markup)

# @bot.message_handler(content_types=["text"])
# def handle_text(message):
#     user_id = message.from_user.id
#     user_text = message.text.strip().lower()
#     mode = user_state.get(user_id)

#     if mode == "Definition":
#         bot.send_chat_action(message.chat.id, "typing")


#         try:
#             synsets = wordnet.synsets(user_text)
#         except Exception as e:
#             print(f"Error during synset lookup for '{user_text}': {e}")
#             bot.reply_to(message, f"An internal error occurred while searching for '{user_text}'. Please try again later.")
#             return     
#         if not synsets:
#             bot.reply_to(message, f"Sorry, I couldn't find a definition for '{user_text}'. Please check the spelling.")
#             return

#         definitions_dict = {}
#         for syn in synsets:
#             pos = syn.pos() 
#             definition = syn.definition()
#             if pos not in definitions_dict:
#                 definitions_dict[pos] = []
#             if definition not in definitions_dict[pos]:
#                 definitions_dict[pos].append(definition)

#         response_text = f"📖 **Word:** {user_text}\n\n"
#         definitions_found = False
#         for pos, def_list in definitions_dict.items():
#             if def_list:
#                 definitions_found = True
#                 pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb'}
#                 display_pos = pos_map.get(pos, pos.upper()) # اگر در map نبود، خودش را نمایش بده

#                 response_text += f"*{display_pos}:*\n"
#                 for i, definition in enumerate(def_list[:3]):
#                     response_text += f"{i+1}. {definition}\n"
#                 response_text += "\n"
    
#         if not definitions_found:
#              bot.reply_to(message, f"Sorry, I couldn't find any definitions for '{user_text}'.")
#         else:
#             bot.reply_to(message, response_text, parse_mode="Markdown")


#     elif user_text == 'get definition':
#         user_state[user_id] = "Definition"
#         bot.send_message(message.chat.id, "Okay, send me the word you want to define.")
#     else:


#         bot.send_message(message.chat.id, "Please use the 'Get Definition' button or send 'Get Definition' again to start.")


# # --- پردازش دکمه‌ها (اگر لازم بود) ---
# # این بخش را در حال حاضر غیرفعال می‌کنیم چون با پیام متنی 'get definition' کار می‌کنیم
# # @bot.callback_query_handler(func=lambda call: True)
# # def handle_callback(call):
# #     pass

# # --- اجرای ربات ---
# if __name__ == '__main__':
#     print("Bot is starting...")
#     bot.polling(none_stop=True)
import telebot
from telebot import types
from dotenv import load_dotenv
import os
import nltk
from nltk.corpus import wordnet

# --- تنظیمات اولیه ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# تنظیم مسیر برای دانلود آفلاین NLTK
nltk.data.path.append(os.path.join(os.getcwd(), 'nltk_data'))

def download_nltk_data():
    try:
        nltk.data.find('corpora/wordnet')
        print("WordNet corpus already downloaded.")
    except LookupError:
        print("WordNet corpus not found. Downloading...")
        nltk.download('wordnet', quiet=True)
        print("WordNet corpus downloaded successfully.")

download_nltk_data()

user_state = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_definition = types.KeyboardButton('Get Definition')
    markup.add(btn_definition)
    bot.reply_to(message, "Welcome! Please use the button below to get a definition.", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.from_user.id
    user_text = message.text.strip().lower()
    mode = user_state.get(user_id)

    # --- ۱. فیلتر هوشمند برای جلوگیری از دخالت در گروه‌ها ---
    # اگر پیام کاربر یک Reply باشد...
    if message.reply_to_message:
        # ...و آن ریپلای به یک "کاربر معمولی" باشد (نه به خودِ ربات)، ربات باید ساکت بماند.
        if not message.reply_to_message.from_user.is_bot:
            return 

    # --- ۲. بررسی وضعیت کاربر (آیا در حالت تعریف کلمه است؟) ---
    if mode == "Definition":
        bot.send_chat_action(message.chat.id, "typing")

        try:
            synsets = wordnet.synsets(user_text)
        except Exception as e:
            print(f"Error during synset lookup for '{user_text}': {e}")
            # استفاده از send_message برای امنیت بیشتر در برابر خطای ۴۰۰
            bot.send_message(message.chat.id, "An internal error occurred. Please try again later.")
            return     

        if not synsets:
            error_msg = f"Sorry, I couldn't find a definition for '{user_text}'."
            # اگر کاربر به پیام ربات ریپلای کرده باشد، ربات هم پاسخ را ریپلای می‌کند
            if message.reply_to_message and message.reply_to_message.from_user.is_bot:
                bot.send_message(message.chat.id, error_msg, reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, error_msg)
            return

        # --- ۳. استخراج و ساختن پاسخ ---
        definitions_dict = {}
        for syn in synsets:
            pos = syn.pos() 
            definition = syn.definition()
            if pos not in definitions_dict:
                definitions_dict[pos] = []
            if definition not in definitions_dict[pos]:
                definitions_dict[pos].append(definition)

        response_text = f"📖 **Word:** {user_text}\n\n"
        definitions_found = False
        for pos, def_list in definitions_dict.items():
            if def_list:
                definitions_found = True
                pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb'}
                display_pos = pos_map.get(pos, pos.upper())

                response_text += f"*{display_pos}:*\n"
                for i, definition in enumerate(def_list[:3]):
                    response_text += f"{i+1}. {definition}\n"
                response_text += "\n"
    
        if not definitions_found:
             bot.send_message(message.chat.id, f"Sorry, I couldn't find any definitions for '{user_text}'.")
        else:
            # ارسال پاسخ نهایی با رعایت منطق ریپلای برای جلوگیری از خطای ۴۰۰
            if message.reply_to_message and message.reply_to_message.from_user.is_bot:
                bot.send_message(message.chat.id, response_text, parse_mode="Markdown", reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, response_text, parse_mode="Markdown")

    # --- ۴. مدیریت دکمه یا دستور فعال‌سازی ---
    elif user_text == 'get definition':
        user_state[user_id] = "Definition"
        bot.send_message(message.chat.id, "Okay, send me the word you want to define.")
    
    else:
        # در حالت عادی (اگر حالت Definition فعال نباشد)
        # برای جلوگیری از مزاحمت در گروه، اگر کاربر پیام عادی داد، ربات چیزی نمی‌گوید.
        # اما در چت خصوصی، راهنمایی می‌کند.
        if message.chat.type == "private":
            bot.send_message(message.chat.id, "Please use the 'Get Definition' button or send 'Get Definition' again to start.")

# --- اجرای ربات ---
if __name__ == '__main__':
    print("Bot is starting...")
    bot.polling(none_stop=True)
