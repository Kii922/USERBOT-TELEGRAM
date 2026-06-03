import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials (dari https://my.telegram.org)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Timezone
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jakarta")

# Delay antar pengiriman pesan (detik)
MIN_DELAY = int(os.getenv("MIN_DELAY", "3"))
MAX_DELAY = int(os.getenv("MAX_DELAY", "7"))

# Data directory (untuk session & database)
DATA_DIR = os.getenv("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Database
DB_PATH = os.getenv("DB_PATH", os.path.join(DATA_DIR, "promo_bot.db"))

# Session name (disimpan di data dir supaya persistent)
SESSION_NAME = os.path.join(DATA_DIR, "promo_userbot")
