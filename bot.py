import telebot
import subprocess
import os
import uuid

# КОНФИГУРАЦИЯ
API_TOKEN = '8508924205:AAGdYk-QItcDbLntib2N0nAhlAxxzynQy4s'
FFMPEG_PATH = r"ffmpeg_tool\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Отправь мне прямую ссылку на видео Sora, и я скачаю его и отправлю тебе!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    if not url.startswith('http'):
        bot.reply_to(message, "Это не похоже на ссылку. Пришли URL!")
        return

    msg = bot.reply_to(message, "Начинаю обработку... Это может занять пару минут.")
    
    file_id = str(uuid.uuid4())
    output_name = f"video_{file_id}.mp4"

    # Команда FFmpeg для очистки
    cmd = [
        FFMPEG_PATH,
        '-i', url,
        '-vf', 'crop=in_w:in_h-60:0:0',
        '-c:v', 'libx264',
        '-crf', '23', # Чуть выше сжатие для быстрой отправки в Телеграм
        '-map_metadata', '-1',
        output_name
    ]

    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_name):
            with open(output_name, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="Вот твое чистое видео!")
            os.remove(output_name) # Удаляем файл после отправки
        else:
            bot.reply_to(message, "Сбой обработки. Проверь ссылку.")
            print(process.stderr)
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

print("Бот запущен...")
bot.infinity_polling()
