import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from threading import Thread
from flask import Flask

# 1. Створюємо веб-сервер для обходу сну хостингу Render
app = Flask('')

@app.route('/')
def home():
    return "Бот працює стабільно!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Ініціалізація бота (ВСТАВТЕ СВІЙ ТОКЕН НИЖЧЕ)
BOT_TOKEN = "8600085658:AAFxYgvTDaQ9ZZzPogxJxaLB-PbEuYzk5PI" 
bot = telebot.TeleBot(BOT_TOKEN)

# Папка для тимчасового збереження відео на сервері
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 3. Обробка стартової команди
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Привіт! Надішли мені посилання на відео з TikTok в особисті повідомлення. "
        "Я завантажу його без водяного знаку і додам кнопку, щоб ти міг зручно скинути його другу! 🚀"
    )

# 4. Основна логіка завантаження та надсилання відео користувачу
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    # Перевірка на посилання з TikTok
    if "tiktok.com" not in url:
        bot.reply_to(message, "Будь ласка, надішли коректне посилання на TikTok.")
        return

    status_msg = bot.reply_to(message, "⏳ Завантажую відео без водяного знаку, зачекай трохи...")

    # Налаштування yt-dlp для скачування чистого файлу mp4
        ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',  # Змінили тут (прибрали DOWNLOAD_DIR)
        'quiet': True,
    }


    try:
        # Завантажуємо відео на диск сервера
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Створюємо інлайн-кнопку для надійного пересилання у будь-який чат
        markup = types.InlineKeyboardMarkup()
        share_button = types.InlineKeyboardButton(
            text="Поділитися з другом ↩️",
            switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat(
                query="",
                allow_user_chats=True,
                allow_group_chats=True
            )
        )
        markup.add(share_button)

        # Відправляємо завантажене відео користувачу разом із кнопкою
        with open(filename, 'rb') as video:
            bot.send_video(
                message.chat.id, 
                video, 
                reply_markup=markup, 
                reply_to_message_id=message.message_id
            )

        # Видаляємо тимчасовий файл з хостингу, щоб не забивати пам'ять
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            "❌ Не вдалося завантажити відео. Можливо, воно приватне, видалене або TikTok змінив алгоритми захисту.", 
            message.chat.id, 
            status_msg.message_id
        )
        print(f"Помилка завантаження: {e}")

# 5. Запуск усього процесу
if __name__ == '__main__':
    print("Бот успішно запускається на сервері...")
    keep_alive()  # Запускаємо Flask у фоновому потоці
    bot.infinity_polling()  # Запускаємо постійне опитування Telegram
