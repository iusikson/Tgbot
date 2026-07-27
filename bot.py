import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Бот працює стабільно!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Ініціалізація бота
BOT_TOKEN = "8600085658:AAHrPZ-GeclqqsXw-7b3GNVd0ul9frwN2so"  # <--- ВСТАВ НОВИЙ ТОКЕН ВІД BOTFATHER
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Надішли мені посилання на TikTok, і я завантажу відео без водяного знаку! 🚀")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    if "tiktok.com" not in url:
        bot.reply_to(message, "Будь ласка, надішли коректне посилання на TikTok.")
        return

    status_msg = bot.reply_to(message, "⏳ Обходжу захист TikTok та завантажую відео...")

    ydl_opts = {
        'format': 'worst',  # Стабільний мобільний формат для обходу бану IP хостингів
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'extractor_args': {'tiktok': {'webpage_skip': ['player_response']}}
    }

    filename = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        markup = types.InlineKeyboardMarkup()
        share_button = types.InlineKeyboardButton(
            text="Поділитися з другом ↩️",
            url=f"https://t.me{url}&text=Переглянь%20це%20відео%20з%20TikTok!"
        )
        markup.add(share_button)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, reply_markup=markup, reply_to_message_id=message.message_id)

        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Не вдалося завантажити це відео. TikTok заблокував запит.", message.chat.id, status_msg.message_id)
        print(f"Помилка: {e}")
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

if __name__ == '__main__':
    print("Бот успішно запускається...")
    
    # ПРИМУСОВО ВИДАЛЯЄМО ВСІ ЗАВИСЛІ ВЕБХУКИ ТА ЧЕРГИ ПЕРЕД СТАРТОМ
    bot.delete_webhook(drop_pending_updates=True)
    
    keep_alive()
    bot.infinity_polling()
