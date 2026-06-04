import asyncio
import logging
import sys
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_NAME
from database import init_db
from handlers import register_all_handlers

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    # Validasi konfigurasi
    if not API_ID or not API_HASH:
        logger.error(
            "API_ID dan API_HASH belum diatur!\n"
            "1. Buka https://my.telegram.org\n"
            "2. Buat aplikasi dan dapatkan API_ID + API_HASH\n"
            "3. Copy .env.example ke .env dan isi credential-nya"
        )
        sys.exit(1)

    # Inisialisasi database
    await init_db()
    logger.info("Database siap.")

    # Buat Pyrogram client (userbot)
    app = Client(
        name=SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
    )

    # Register semua command handlers
    register_all_handlers(app)

    # Jalankan bot
    logger.info("Memulai Promo Bot...")
    logger.info("Kirim /help di Saved Messages untuk melihat perintah.")

    await app.start()
    logger.info("Bot berjalan! Tekan Ctrl+C untuk berhenti.")

    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot dihentikan.")
