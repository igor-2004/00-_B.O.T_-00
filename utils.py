from telebot import types
from datetime import datetime

# Простейшее хранение состояний в памяти (для простоты).
# На проде/нескольких инстансах — используйте Redis.
_states = {}

def set_state(user_id:int, key:str, value):
    _states.setdefault(user_id, {})[key] = value

def get_state(user_id:int, key:str, default=None):
    return _states.get(user_id, {}).get(key, default)

def clear_state(user_id:int):
    if user_id in _states:
        del _states[user_id]

# Клавиатуры
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🔗 Ссылка на канал"))
    kb.add(types.KeyboardButton("📸 Отправить фото"))
    kb.add(types.KeyboardButton("🔁 Проверить подписку"))
    return kb

def sendphoto_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("Одиночное фото"))
    kb.add(types.KeyboardButton("Альбомное фото"))
    kb.add(types.KeyboardButton("Отмена"))
    return kb

def album_control_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("Готово")
    kb.add("Отмена")
    return kb

def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Статистика 24ч")
    kb.add("Список админов")
    kb.add("Добавить админа")
    kb.add("Удалить админа")
    kb.add("Назад")
    return kb
