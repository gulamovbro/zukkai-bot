import telebot
from groq import Groq
import os

# Render muhiti uchun tokenlarni "Environment Variables"dan olamiz
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "Assalomu alaykum! ZukkAI Renderda muvaffaqiyatli ishga tushdi. 🎓")

@bot.message_handler(func=lambda message: True)
def talk_to_ai(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen ZukkAI repetitorisan. O'zbek tilida javob ber."},
                {"role": "user", "content": message.text}
            ],
            model="llama3-8b-8192",
        )
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Xatolik yuz berdi.")

if __name__ == "__main__":
    print("Bot ishlamoqda...")
    bot.infinity_polling()
  
