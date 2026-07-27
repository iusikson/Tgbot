import os
import telebot
from yt_dlp import YoutubeDL

# Ініціалізація бота
BOT_TOKEN = "8600085658:AAFxYgvTDaQ9ZZzPogxJxaLB-PbEuYzk5PI"
bot = telebot.TeleBot(BOT_TOKEN)

# Папка для тимчасового збереження відео
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привіт! Надішли мені посилання на відео з TikTok, і я завантажу його для тебе.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    # Перевірка, чи це посилання на TikTok
    if "tiktok.com" not in url:
        bot.reply_to(message, "Будь ласка, надішли коректне посилання на TikTok.")
        return

    status_msg = bot.reply_to(message, "⏳ Завантажую відео, зачекай трохи...")

    # Налаштування yt-dlp для завантаження без водяного знаку
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Витягуємо інформацію та завантажуємо файл
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Відправляємо відео користувачу
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, reply_to_message_id=message.message_id)

        # Видаляємо тимчасовий файл з сервера
        os.remove(filename)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Не вдалося завантажити відео. Можливо, воно приватне або видалене.", message.chat.id, status_msg.message_id)
        print(f"Помилка: {e}")

# Запуск бота
if __name__ == '__main__':
    print("Бот успішно запущений...")
    bot.infinity_polling()
