import os
import telebot
from yt_dlp import YoutubeDL
from threading import Thread
from flask import Flask

# Створюємо веб-сервер для обходу сну Render
app = Flask('')

@app.route('/')
def home():
    return "Бот працює!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Ініціалізація бота
BOT_TOKEN = "8600085658:AAFxYgvTDaQ9ZZzPogxJxaLB-PbEuYzk5PI"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Надішли мені посилання на відео з TikTok, і я завантажу його для тебе.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    if "tiktok.com" not in url:
        bot.reply_to(message, "Будь ласка, надішли коректне посилання на TikTok.")
        return

    status_msg = bot.reply_to(message, "⏳ Завантажую відео, зачекай трохи...")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)

        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Не вдалося завантажити відео.", message.chat.id, status_msg.message_id)
        print(f"Помилка: {e}")

# Запуск бота разом із веб-сервером
if __name__ == '__main__':
    print("Бот успішно запущений...")
    keep_alive()  # Запуск фонового веб-сервера
    bot.infinity_polling()
