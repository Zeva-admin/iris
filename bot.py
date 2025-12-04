import logging
import json
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8408758709:AAEKcsEWhocVn-z9CLcFdcqA2k0pI8IO0Mw"
DATA_FILE = "data.json"

# Загружаем данные из файла
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Сохраняем данные в файл
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_nicks = load_data()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Главное меню клавиатуры
main_menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/list"), KeyboardButton("/find")],
        [KeyboardButton("/remove"), KeyboardButton("/stats")]
    ],
    resize_keyboard=True
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот вместо Iris.\n"
        "Добавь ник командой: +ник Aboo\n",
        reply_markup=main_menu
    )

# Добавление ника
async def add_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith("+ник"):
        parts = text.split(" ", 1)
        if len(parts) == 2:
            game_nick = parts[1].strip()
            user_id = str(update.message.from_user.id)
            user_name = update.message.from_user.username or update.message.from_user.first_name
            user_nicks[user_id] = {"name": user_name, "game_nick": game_nick}
            save_data(user_nicks)
            await update.message.reply_text(f"✅ Ник '{game_nick}' сохранён для {user_name}", reply_markup=main_menu)
        else:
            await update.message.reply_text("❌ Укажи ник после команды, например: +ник Aboo", reply_markup=main_menu)

# Список ников
async def list_nicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_nicks:
        await update.message.reply_text("Список пуст", reply_markup=main_menu)
        return

    msg = "🎮 Игровые ники:\n\n"
    for uid, u in user_nicks.items():
        msg += f"• [{u['game_nick']} ({u['name']})](tg://user?id={uid})\n"

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu)

# Удаление ника
async def remove_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in user_nicks:
        del user_nicks[user_id]
        save_data(user_nicks)
        await update.message.reply_text("🗑 Ник удалён.", reply_markup=main_menu)
    else:
        await update.message.reply_text("❌ У тебя нет сохранённого ника.", reply_markup=main_menu)

# Поиск ника
async def find_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Используй: /find <игровой_ник>", reply_markup=main_menu)
        return
    search = " ".join(context.args).lower()
    results = [(uid, u) for uid, u in user_nicks.items() if search in u["game_nick"].lower()]
    if results:
        msg = "🔍 Найдено:\n\n"
        for uid, u in results:
            msg += f"• [{u['game_nick']} ({u['name']})](tg://user?id={uid})\n"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu)
    else:
        await update.message.reply_text("❌ Ник не найден.", reply_markup=main_menu)

# Статистика
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(user_nicks)
    await update.message.reply_text(f"📊 Всего сохранённых ников: {count}", reply_markup=main_menu)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_nicks))
    app.add_handler(CommandHandler("remove", remove_nick))
    app.add_handler(CommandHandler("find", find_nick))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_nick))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
