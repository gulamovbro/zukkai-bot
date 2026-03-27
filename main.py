import telebot
from groq import Groq
import os
import base64
import requests
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask('')

@app.route('/')
def home():
    return "ZukkAI Vision faol!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Tizim ko'rsatmasi
SYSTEM_PROMPT = "Sen ZukkAI ismli o'zbek repetitorisan. Matematika, fizika va boshqa fanlardan masalalarni o'zbek tilida bosqichma-bosqich yechib berasan."

def encode_image(image_content):
    return base64.b64encode(image_content).decode('utf-8')

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Men tayyorman. ✨\n\nMisolni rasmga olib yuboring yoki matn ko'rinishida yozing!")

# 2. RASMLI XABARLAR UCHUN
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = bot.reply_to(message, "Rasmni tahlil qilyapman... 🔍")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        response = requests.get(image_url)
        base64_image = encode_image(response.content)

        # Vision modeldan foydalanamiz
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{SYSTEM_PROMPT} Mana bu rasmdagi masalani yechib ber."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )
        bot.edit_message_text(chat_completion.choices[0].message.content, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"Xatolik: Rasmni tahlil qila olmadim. Qayta urinib ko'ring.", message.chat.id, status_msg.message_id)

# 3. MATNLI XABARLAR UCHUN
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    status_msg = bot.reply_to(message, "O'ylayapman... 🤔")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            model="llama-3.1-8b-instant",
        )
        bot.edit_message_text(chat_completion.choices[0].message.content, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("Kechirasiz, javob berishda xatolik yuz berdi.", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    keep_alive()
    bot.infinity_polling()
    
