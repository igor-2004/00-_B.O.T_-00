# Скрипт, который запускается перед gunicorn:
from server import prepare_webhook
from scheduler import start_scheduler
from bot import bot

if __name__ == "__main__":
    prepare_webhook()
    start_scheduler()
    print("Server setup done.")
