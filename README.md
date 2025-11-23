(обновлённый — включаю инструкцию: создание файла секретов на Render)

# Telegram Bot (Render deployment)

Внимание: НЕ храните BOT_TOKEN в публичном репозитории. Используйте либо переменные окружения Render, либо приватный файл на смонтированном диске (инструкция ниже).

## Переменные / файл секретов
Можно задавать конфигурацию двумя способами (рекомендуется 1 или 2):

1) Самый безопасный: задать Environment Variables в Render:
   - BOT_TOKEN
   - OWNER_ID
   - CHANNEL_ID
   - WEBHOOK_URL
   - DB_PATH (рекомендуется /data/bot_database.db)

2) Если НЕ хотите использовать Env Vars в Render UI: создайте приватный файл на смонтированном диске (например /data/.bot_secrets) с содержимым:
BOT_TOKEN=your_bot_token_here OWNER_ID=123456789 CHANNEL_ID=-100.... WEBHOOK_URL=https://your-service.onrender.com DB_PATH=/data/bot_database.db

и установите права доступа (chmod 600). Файл добавлен в .gitignore — не коммитьте его.

## Локально
1. Создайте виртуальное окружение:
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

2. Установите зависимости:
pip install -r requirements.txt

3. Установите переменные окружения локально (пример):
export BOT_TOKEN="твой_токен"
export OWNER_ID="твой_telegram_id"
export CHANNEL_ID="-100...."
export WEBHOOK_URL="https://abcd1234.ngrok.io"
export DB_PATH="./data/bot_database.db"

Или создайте локально файл data/.bot_secrets (см. формат выше).

4. Создайте папку data:
mkdir -p data

5. Запустите сервер:
python server.py

6. (При использовании ngrok)
ngrok http 5000
и укажите полученный URL в WEBHOOK_URL.

## Развёртывание на Render (без Env Vars — вариант с файлом секретов)
1. На Render создайте Web Service и подключите репозиторий.
2. Attach Disk (Storage) → добавьте диск (чтобы использовать /data).
3. Деплой. После первого деплоя (или во время работы сервиса) откройте Render Shell (в панели сервиса) и выполните:
mkdir -p /data cat > /data/.bot_secrets <<'EOF' BOT_TOKEN=your_bot_token_here OWNER_ID=123456789 CHANNEL_ID=-1001234567890 WEBHOOK_URL=https://your-service.onrender.com DB_PATH=/data/bot_database.db EOF chmod 600 /data/.bot_secrets

После этого перезапустите сервис (или redeploy).
Теперь бот прочитает секреты из /data/.bot_secrets и Env Vars в Render можно не задавать.

4. Start Command:
bash -lc "python3 server_setup.py & exec gunicorn server:app --bind 0.0.0.0:$PORT --workers 1"

## Проверка
- Откройте диалог с ботом: /start
- Попробуйте отправить фото и проверьте, что оно дошло до канала.
- Логи Render → смотрим ошибки (webhook, права бота, DB).
