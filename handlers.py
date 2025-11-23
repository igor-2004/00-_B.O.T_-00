import telebot
from telebot import types
from config import DB_PATH, CHANNEL_ID, OWNER_ID
from db import add_submission, get_submissions_last_seconds, add_admin, remove_admin, list_admins, is_admin
from utils import main_keyboard, sendphoto_menu, album_control_kb, set_state, get_state, clear_state
import time

# Регистрация всех хэндлеров
def register_handlers(bot: telebot.TeleBot):
    @bot.message_handler(commands=['start'])
    def cmd_start(msg):
        kb = main_keyboard()
        bot.send_message(msg.chat.id, "Привет! Добро пожаловать. Используй меню.", reply_markup=kb)

    @bot.message_handler(func=lambda m: m.text == "🔗 Ссылка на канал")
    def cmd_channel_link(msg):
        if CHANNEL_ID:
            bot.send_message(msg.chat.id, f"Ссылка на канал: https://t.me/your_channel_username (замени в README)", reply_markup=main_keyboard())
        else:
            bot.send_message(msg.chat.id, "CHANNEL_ID не настроен.", reply_markup=main_keyboard())

    @bot.message_handler(func=lambda m: m.text == "📸 Отправить фото")
    def cmd_send_photo(msg):
        bot.send_message(msg.chat.id, "Выберите режим отправки:", reply_markup=sendphoto_menu())

    @bot.message_handler(func=lambda m: m.text == "Одиночное фото")
    def single_photo_mode(msg):
        set_state(msg.chat.id, "mode", "single")
        bot.send_message(msg.chat.id, "Отправь фотографию (одну) и, если нужно, подпись (текст) после фото.", reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: m.text == "Альбомное фото")
    def album_mode(msg):
        set_state(msg.chat.id, "mode", "album")
        set_state(msg.chat.id, "album_files", [])
        bot.send_message(msg.chat.id, "Отправляй до 10 фото подряд. Нажми 'Готово' когда закончишь.", reply_markup=album_control_kb())

    @bot.message_handler(func=lambda m: m.text == "Отмена")
    def cancel(msg):
        clear_state(msg.chat.id)
        bot.send_message(msg.chat.id, "Отменено.", reply_markup=main_keyboard())

    @bot.message_handler(content_types=['photo'])
    def photos_handler(msg):
        mode = get_state(msg.chat.id, "mode")
        if not mode:
            bot.send_message(msg.chat.id, "Чтобы отправить фото — нажми 'Отправить фото' в меню.", reply_markup=main_keyboard())
            return

        # Получаем file_id самой крупной версии
        file_id = msg.photo[-1].file_id

        if mode == "single":
            # Возможно пользователь пришлёт текст-описание отдельным сообщением; чтобы упростить — сразу публикуем
            caption = msg.caption or ""
            # Отправляем в канал
            target = CHANNEL_ID or bot.owner_id
            sent = bot.send_photo(target, file_id, caption=build_caption(msg.from_user, caption, kind="Фото (один)"))
            # Сохраняем запись в БД
            add_submission(DB_PATH, msg.from_user.id, "single", [file_id], caption)
            bot.send_message(msg.chat.id, "Фото отправлено. Спасибо! ✅", reply_markup=main_keyboard())
            clear_state(msg.chat.id)

        elif mode == "album":
            files = get_state(msg.chat.id, "album_files") or []
            files.append(file_id)
            set_state(msg.chat.id, "album_files", files)
            bot.send_message(msg.chat.id, f"Добавлено фото #{len(files)}. Отправьте ещё или нажмите 'Готово'.", reply_markup=album_control_kb())

    @bot.message_handler(func=lambda m: m.text == "Готово")
    def album_done(msg):
        files = get_state(msg.chat.id, "album_files") or []
        if not files:
            bot.send_message(msg.chat.id, "Нет добавленных фото. Отправьте что-нибудь или нажмите Отмена.", reply_markup=main_keyboard())
            return
        media = []
        for fid in files:
            media.append(types.InputMediaPhoto(media=fid))
        # Первый элемент может содержать подпись
        caption = ""
        # Отправляем в канал
        target = CHANNEL_ID or bot.owner_id
        bot.send_media_group(target, media)
        add_submission(DB_PATH, msg.from_user.id, "album", files, "")
        bot.send_message(msg.chat.id, "Альбом отправлен. Спасибо! ✅", reply_markup=main_keyboard())
        clear_state(msg.chat.id)

    def build_caption(user, text, kind="Фото"):
        nick = f"@{user.username}" if user.username else f"{user.first_name or ''}"
        header = f"{kind}\n—\n{nick}\n—\n⬇️ Клиент ⬇️\n\n"
        if text:
            header += text + "\n\n"
        # internal id в БД можно получить, но упростим: не подставляем
        return header

    # ========== Админ-команды ==========
    @bot.message_handler(commands=['admin'])
    def admin_menu(msg):
        if not is_admin(DB_PATH, msg.from_user.id) and msg.from_user.id != OWNER_ID:
            bot.reply_to(msg, "Доступ запрещён.")
            return
        bot.send_message(msg.chat.id, "Панель админа:", reply_markup=types.ReplyKeyboardMarkup(keyboard=[
            [types.KeyboardButton("Статистика 24ч")],
            [types.KeyboardButton("Список админов")],
            [types.KeyboardButton("Добавить админа")],
            [types.KeyboardButton("Удалить админа")],
            [types.KeyboardButton("Назад")]
        ], resize_keyboard=True))

    @bot.message_handler(func=lambda m: m.text == "Статистика 24ч")
    def stats_24h(msg):
        if not is_admin(DB_PATH, msg.from_user.id) and msg.from_user.id != OWNER_ID:
            bot.reply_to(msg, "Доступ запрещён.")
            return
        rows = get_submissions_last_seconds(DB_PATH, 24*3600)
        bot.send_message(msg.chat.id, f"За 24 часа отправлено: {len(rows)} записей.", reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: m.text == "Список админов")
    def list_admins_h(msg):
        if not is_admin(DB_PATH, msg.from_user.id) and msg.from_user.id != OWNER_ID:
            bot.reply_to(msg, "Доступ запрещён.")
            return
        admins = list_admins(DB_PATH)
        await_text = "\n".join(str(a) for a in admins) or "Пусто"
        bot.send_message(msg.chat.id, "Админы:\n" + await_text)

    @bot.message_handler(func=lambda m: m.text == "Добавить админа")
    def add_admin_cmd(msg):
        if msg.from_user.id != OWNER_ID:
            bot.reply_to(msg, "Только владелец может добавлять админов.")
            return
        set_state(msg.chat.id, "await_admin_add", True)
        bot.send_message(msg.chat.id, "Отправь user_id пользователя для добавления админом.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Отмена"))

    @bot.message_handler(func=lambda m: get_state(m.chat.id, "await_admin_add") is True)
    def do_add_admin(msg):
        if msg.text == "Отмена":
            clear_state(msg.chat.id)
            bot.send_message(msg.chat.id, "Отменено.", reply_markup=main_keyboard())
            return
        try:
            uid = int(msg.text.strip())
            add_admin(DB_PATH, uid)
            bot.send_message(msg.chat.id, f"Добавлен админ: {uid}", reply_markup=main_keyboard())
        except Exception as e:
            bot.send_message(msg.chat.id, "Ошибка: введи корректный user_id (число).")
        finally:
            clear_state(msg.chat.id)

    @bot.message_handler(func=lambda m: m.text == "Удалить админа")
    def remove_admin_cmd(msg):
        if msg.from_user.id != OWNER_ID:
            bot.reply_to(msg, "Только владелец может удалять админов.")
            return
        set_state(msg.chat.id, "await_admin_remove", True)
        bot.send_message(msg.chat.id, "Отправь user_id пользователя для удаления из админов.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Отмена"))

    @bot.message_handler(func=lambda m: get_state(m.chat.id, "await_admin_remove") is True)
    def do_remove_admin(msg):
        if msg.text == "Отмена":
            clear_state(msg.chat.id)
            bot.send_message(msg.chat.id, "Отменено.", reply_markup=main_keyboard())
            return
        try:
            uid = int(msg.text.strip())
            remove_admin(DB_PATH, uid)
            bot.send_message(msg.chat.id, f"Удалён админ: {uid}", reply_markup=main_keyboard())
        except Exception as e:
            bot.send_message(msg.chat.id, "Ошибка: введи корректный user_id (число).")
        finally:
            clear_state(msg.chat.id)
