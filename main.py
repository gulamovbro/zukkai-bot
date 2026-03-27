import telebot
from groq import Groq
import os
from flask import Flask
from threading import Thread

# 1. SOZLAMALAR
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask('')

# Render uchun kichik server (bot o'chmasligi uchun)
@app.route('/')
def home():
    return "ZukkAI repetitori faol!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. BOT KO'RSATMALARI (AI xarakteri)
SYSTEM_INSTRUCTION = """
Sen ZukkAI ismli professional o'zbek repetitorisan. 
Sening vazifang o'quvchilarga Matematika, Fizika, Kimyo va Biologiya fanlaridan yordam berish.

QOIDALARING:
1. Har doim O'zbek tilida, juda muloyim va rag'batlantiruvchi ohangda javob ber.
2. Hech qachon to'g'ridan-to'g'ri javobni srazu tashlama!
3. Masalani BOSQICHMA-BOSQICH (Step-by-step) tushuntir.
4. Har bir bosqichda nega bunday bo'layotganini sodda tilda izohla.
5. Agar formula kerak bo'lsa, uni alohida qatorda yoz.
6. Oxirida o'quvchidan "Tushunarlimi?" deb so'ra.
"""

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    welcome_text = (
        "Assalomu alaykum! Men **ZukkAI** — sizning shaxsiy repetitoringizman. 🎓\n\n"
        "Men sizga quyidagi fanlardan yordam bera olaman:\n"
        "🔹 Matematika\n"
        "🔹 Fizika\n"
        "🔹 Kimyo\n"
        "🔹 Biologiya\n\n"
        "Savolingizni yoki masalangizni yozing, birgalikda yechamiz! 👇"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_learning(message):
    # O'quvchiga kutish haqida xabar berish
    processing_msg = bot.reply_to(message, "Savolingizni tahlil qilyapman... 🤔")
    
    try:
        # AI (Llama 3) bilan muloqot
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": message.text}
            ],
            model="llama3-8b-8192",
            temperature=0.7 # Ijodkorlik va aniqlik balansi
        )
        
        ai_reply = chat_completion.choices[0].message.content
        
        # Javobni yuborish va "O'ylayapman" xabarini o'chirish
        bot.edit_message_text(ai_reply, message.chat.id, processing_msg.message_id)
        
    except Exception as e:
        print(f"Xato yuz berdi: {e}")
        bot.edit_message_text("Kechirasiz, tizimda biroz yuklama bor. Qaytadan yozib ko'ring. 😊", 
                             message.chat.id, processing_msg.message_id)

# 3. ISHGA TUSHIRISH
if __name__ == "__main__":bot.remove_webhook()
    keep_alive()
    print("ZukkAI repetitori ishga tushdi...")
    bot.infinity_polling()
      
