import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Бот працює!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

BOT_TOKEN = "8600085658:AAFxYgvTDaQ9ZZzPogxJxaLB-PbEuYzk5PI"  # Замініть на свій токен
bot = telebot.TeleBot(BOT_TOKEN)

# ОБРОБКА В ЧАТІ З ЛЮДИНОЮ (INLINE MODE)
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(inline_query):
    url = inline_query.query

    if "tiktok.com" not in url:
        return

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False) # Не качаємо на диск, беремо відразу пряме посилання
            video_url = info.get('url')
            thumb_url = info.get('thumbnail')

        # Формуємо результат, який побачить користувач у чаті
        video_result = types.InlineQueryResultVideo(
            id='1',
            video_url=video_url,
            mime_type="video/mp4",
            thumbnail_url=thumb_url,
            title="Завантажити відео з TikTok"
        )

        bot.answer_inline_query(inline_query.id, [video_result], cache_time=1)
    except Exception as e:
        print(f"Inline помилка: {e}")

# ОБРОБКА В ОСОБИСТИХ ПОВІДОМЛЕННЯХ З БОТОМ (ЯК БУЛО)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Надішли мені посилання на TikTok в особисті, або просто згадай мене в будь-якому іншому чаті!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "tiktok.com" not in url:
        bot.reply_to(message, "Будь ласка, надішли коректне посилання на TikTok.")
        return

    status_msg = bot.reply_to(message, "⏳ Завантажую відео...")
    ydl_opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': 'downloads/%(id)s.%(ext)s', 'quiet': True}

    try:
        if not os.path.exists("downloads"): os.makedirs("downloads")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ Помилка завантаження.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()
