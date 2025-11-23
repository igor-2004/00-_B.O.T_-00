import os
from pathlib import Path

# Путь к файлу секретов (используйте этот файл, если НЕ хотите задавать env vars в Render)
DEFAULT_SECRETS_FILE = os.environ.get("SECRETS_FILE", "/data/.bot_secrets")

def load_secrets_file(path):
    """Прочитать простой KEY=VALUE файл в словарь. Игнорируются строки, начинающиеся с #."""
    d = {}
    p = Path(path)
    if not p.exists():
        return d
    try:
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    d[k.strip()] = v
    except Exception as e:
        print(f"Cannot read secrets file {path}: {e}")
    return d

# Сначала читаем файл секретов (если есть)
_secrets = load_secrets_file(DEFAULT_SECRETS_FILE)

def _get(key, default=None):
    # Сначала окружение, затем файл секретов, затем default
    return os.environ.get(key) or _secrets.get(key) or default

# Обязательные: BOT_TOKEN должен быть установлен либо в env, либо в файле секретов
BOT_TOKEN = _get("8073733884:AAHenpjcO50sjxINpqRCK5O7iUrJCEUBN-I")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set! Set it in environment variables or in /data/.bot_secrets file.")

# CHANNEL_ID: канал/чат для публикации (например -1001234567890). По умолчанию 0 (не настроен).
try:
    CHANNEL_ID = int(_get("CHANNEL_ID", "-1001958513038"))
except ValueError:
    CHANNEL_ID = 0

# ID владельца/админа (Telegram user id)
try:
    OWNER_ID = int(_get("OWNER_ID", "1184497918"))
except ValueError:
    OWNER_ID = 0

# Путь к sqlite (рекомендуется: /data/bot_database.db на Render)
DB_PATH = _get("DB_PATH", "/data/bot_database.db")

# WEBHOOK: публичный URL без пути
WEBHOOK_URL = _get("WEBHOOK_URL", "https://bots-00.onrender.com")

# Путь приёма вебхуков
WEBHOOK_PATH = _get("WEBHOOK_PATH", "/webhook")

# Прочие настройки
try:
    SEND_COOLDOWN_SECONDS = int(_get("SEND_COOLDOWN_SECONDS", str(30 * 60)))
except ValueError:
    SEND_COOLDOWN_SECONDS = 30 * 60

USE_OVERLAY_ON_IMAGE = _get("USE_OVERLAY_ON_IMAGE", "False").lower() in ("1", "true", "yes")
