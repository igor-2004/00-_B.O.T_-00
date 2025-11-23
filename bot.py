import telebot
from config import BOT_TOKEN, CHANNEL_ID, OWNER_ID, DB_PATH
from handlers import register_handlers
from db import init_db, ensure_owner_admin

# Создаём объект бота, НЕ запускаем polling здесь
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# Атрибуты, чтобы другие модули могли получить доступ
bot.channel_id = CHANNEL_ID
bot.owner_id = OWNER_ID
bot.db_path = DB_PATH

# Инициализация БД (если нужно)
init_db(DB_PATH)

# Убедиться, что владелец в списке админов
ensure_owner_admin(OWNER_ID)

# Регистрируем хэндлеры (в handlers.py)
register_handlers(bot)
