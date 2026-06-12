from telebot import TeleBot, types
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
AVAL_AI_KEY = os.getenv("AVAL_AI_KEY")

bot = TeleBot(BOT_TOKEN, threaded=False)

client = OpenAI(
    api_key=AVAL_AI_KEY,
    base_url="https://api.avalai.ir/v1"
)

user_state = {}
user_chats = {}

SYSTEM_PROMPT_DEFINITION = """
You are a specialized English-to-Persian Dictionary Bot.
Your ONLY purpose is to provide the definition, pronunciation, and Persian translation of English words.

RULES:
1. If the user sends an English word, respond with:
   - Pronunciation (IPA)
   - Definition
   - Persian Translation
   - Example Sentence with translation
2. If the user asks anything else, refuse and say:
   'لطفاً فقط کلمه انگلیسی خود را ارسال کنید تا معنی آن را برای شما پیدا کنم.'
3. Be concise and direct.
"""

SYSTEM_PROMPT_TRANSLATE = """
You are a translation bot.
Translate the user's text from English to Persian.
Keep the meaning natural and accurate.
"""

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Definition", "Translate")
    bot.send_message(
        message.chat.id,
        "Hello,\nI'm English Dictionary Bot.\nPlease choose one option and then send your text.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text in ["Definition", "Translate"])
def choose_mode(message):
    user_id = message.from_user.id
    user_state[user_id] = message.text

    bot.reply_to(message, f"✅ Mode set to {message.text}. Now send your text.")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.from_user.id
    user_text = message.text

    mode = user_state.get(user_id)

    if mode not in ["Definition", "Translate"]:
        bot.reply_to(message, "Please choose Definition or Translate first.")
        return

    bot.send_chat_action(message.chat.id, "typing")

    try:
        if user_id not in user_chats:
            if mode == "Definition":
                user_chats[user_id] = [{"role": "system", "content": SYSTEM_PROMPT_DEFINITION}]
            else:
                user_chats[user_id] = [{"role": "system", "content": SYSTEM_PROMPT_TRANSLATE}]


        current_system = SYSTEM_PROMPT_DEFINITION if mode == "Definition" else SYSTEM_PROMPT_TRANSLATE
        if user_chats[user_id][0]["content"] != current_system:
            user_chats[user_id] = [{"role": "system", "content": current_system}]

        user_chats[user_id].append({"role": "user", "content": user_text})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=user_chats[user_id],
            temperature=0.2
        )

        ai_answer = response.choices[0].message.content
        user_chats[user_id].append({"role": "assistant", "content": ai_answer})

        if len(user_chats[user_id]) > 6:
            user_chats[user_id] = [user_chats[user_id][0]] + user_chats[user_id][-5:]

        bot.reply_to(message, ai_answer)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "❌ Error while processing your request.")



bot.polling()