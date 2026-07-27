import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from threading import Thread
from flask import Flask

# 1. Фоновий сервер Flask для хостингу Render
app = Flask('')

@app.route('/')
def home():
    return "Бот працює стабільно!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Ініціалізація бота (ВСТАВ СВІЙ ТОКЕН НИЖЧЕ)
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА" 
bot = telebot.TeleBot(BOT_TOKEN)

# 3. Стартова команда
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Привіт! Надішли мені посилання на відео з TikTok. "
        "Я завантажу його без водяного знаку і додам кнопку для зручного пересилання другу! 🚀"
    )

# 4. Головна логіка завантаження відео
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    if "tiktok.com" not in url:
        bot.reply_to(message, "Будь ласка, надішли коректне посилання на TikTok.")
        return

    status_msg = bot.reply_to(message, "⏳ Завантажую відео без водяного знаку, зачекай трохи...")

    # Налаштування завантажувача
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
    }

    try:
        # Скачуємо чистий mp4-файл у корінь сервера
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Створюємо просту та безвідмовну кнопку "Поділитися"
        markup = types.InlineKeyboardMarkup()
        share_button = types.InlineKeyboardButton(
            text="Поділитися з другом ↩️",
            url=f"https://t.me{url}&text=Переглянь%20це%20відео%20з%20TikTok!"
        )
        markup.add(share_button)

        # Надсилаємо скачаний файл користувачу
        with open(filename, 'rb') as video:
            bot.send_video(
                message.chat.id, 
                video, 
                reply_markup=markup, 
                reply_to_message_id=message.message_id
            )

        # Видаляємо тимчасове сміття з сервера, щоб Render не лаявся
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            "❌ Не вдалося завантажити відео. Спробуйте інше посилання.", 
            message.chat.id, 
            status_msg.message_id
        )
        print(f"Помилка завантаження: {e}")

if __name__ == '__main__':
    print("Бот успішно запускається...")
    keep_alive()
    bot.infinity_polling()
