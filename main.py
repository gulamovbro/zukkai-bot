import telebot
from groq import Groq
import os
import base64
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

SYSTEM_INSTRUCTION = """
Sen ZukkAI ismli o'zbek repetitorisan. 
Sizga rasm yoki matn ko'rinishida topshiriq yuboriladi.
Vazifang: Masalani tahlil qilish va uni BOSQICHMA-BOSQICH o'zbek tilida tushuntirib yechish.
Matematika, Fizika, Kimyo va Biologiya qonuniyatlariga tayanib javob ber.
"""

# 2. RASMNI ENKODLASH FUNKSIYASI
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Men endi rasmdagi misollarni ham yechaman. 📸\n\nMisolni rasmga olib yuboring yoki matn ko'rinishida yozing!")

# 3. RASMLI XABARLARNI QABUL QILISH
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    processing_msg = bot.reply_to(message, "Rasmni ko'ryapman, tahlil qilishga biroz vaqt bering... 🔍")
    
    try:
        # Rasmni yuklab olish
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        base64_image = encode_image("image.jpg")

        # Vision AI ga yuborish
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SYSTEM_INSTRUCTION},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )

        ai_reply = chat_completion.choices[0].message.content
        bot.edit_message_text(ai_reply, message.chat.id, processing_msg.message_id)

    except Exception as e:
        bot.edit_message_text("Rasmni tahlil qilishda xatolik bo'ldi. Iltimos, rasm aniq ekanligini tekshiring.", message.chat.id, processing_msg.message_id)

# 4. MATNLI XABARLARNI QABUL QILISH
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    processing_msg = bot.reply_to(message, "O'ylayapman... 🤔")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": message.text}
            ],
            model="llama3-8b-8192",
        )
        ai_reply = chat_completion.choices[0].message.content
        bot.edit_message_text(ai_reply, message.chat.id, processing_msg.message_id)
    except Exception as e:
        bot.edit_message_text("Xatolik yuz berdi.", message.chat.id, processing_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    keep_alive()
    bot.infinity_polling()
                
