import os
from flask import Flask, request
import telebot
from bot import bot
from config import WEBHOOK_URL, WEBHOOK_PATH, BOT_TOKEN
from scheduler import start_scheduler

app = Flask(__name__)

WEBHOOK_BASE = WEBHOOK_PATH.rstrip('/')
WEBHOOK_FULL = f"{WEBHOOK_BASE}/{BOT_TOKEN}"

@app.route('/', methods=['GET'])
def index():
    return 'OK', 200

@app.route(WEBHOOK_FULL, methods=['POST'])
def webhook():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    except Exception as e:
        print("Webhook processing error:", e)
        return '', 500

def prepare_webhook():
    """Установит webhook на значение WEBHOOK_URL+WEBHOOK_FULL, если WEBHOOK_URL задан."""
    if not WEBHOOK_URL:
        print("WEBHOOK_URL не задан, пропускаю установку webhook.")
        return
    webhook_url = WEBHOOK_URL.rstrip('/') + WEBHOOK_FULL
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print("Webhook set to", webhook_url)
    except Exception as e:
        print("Error setting webhook:", e)

if __name__ == '__main__':
    # Для локальной разработки (ngrok) можно запускать напрямую
    prepare_webhook()
    start_scheduler()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
