import telebot
from telebot import types
from dotenv import load_dotenv
import os
import nltk
from nltk.corpus import wordnet

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
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

@bot.message_handler(content_types=["text", "photo", "document", "sticker", "video", "audio"])
def handle_text(message):

    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Just send your *English word*, Don't send photo, file, etc")
        return

    user_id = message.from_user.id
    user_text = message.text.strip().lower()
    
    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        return

    if user_text == 'get definition':
        user_state[user_id] = "Definition"
        bot.send_message(message.chat.id, "Mode activated! Now, send me the word you want to define.")
        return


    mode = user_state.get(user_id)

    if mode == "Definition":
        bot.send_chat_action(message.chat.id, "typing")

        try:
            synsets = wordnet.synsets(user_text)
        except Exception as e:
            print(f"Error during synset lookup for '{user_text}': {e}")
            bot.send_message(message.chat.id, "An internal error occurred.")
            return     

        if not synsets:
            error_msg = f"Sorry, I couldn't find a definition for '{user_text}'."
            if message.reply_to_message and message.reply_to_message.from_user.is_bot:
                bot.send_message(message.chat.id, error_msg, reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, error_msg)
            return


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
                pos_map = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb', 's': 'Adjective Satellite'}
                display_pos = pos_map.get(pos, pos.upper())

                response_text += f"*{display_pos}:*\n"
                for i, definition in enumerate(def_list[:]):
                    response_text += f"{i+1}. {definition}\n"
                response_text += "\n"

        if not definitions_found:
             bot.send_message(message.chat.id, f"Sorry, I couldn't find any definitions for '{user_text}'.")
        else:
            if message.reply_to_message and message.reply_to_message.from_user.is_bot:
                bot.send_message(message.chat.id, response_text, parse_mode="Markdown", reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, response_text, parse_mode="Markdown")

    else:
        if message.chat.type == "private":
            bot.send_message(message.chat.id, "Please use the 'Get Definition' button to start.")


if __name__ == '__main__':
    print("Bot is starting...")
    bot.polling(none_stop=True)
