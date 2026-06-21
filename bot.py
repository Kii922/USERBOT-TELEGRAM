import asyncio
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_NAME
from database import init_db, get_active_schedules, update_schedule_sent
from handlers import register_all_handlers
from auth import set_owner_id
from sender import send_to_groups

# Set timezone ke Jakarta (UTC+7)
TIMEZONE = ZoneInfo("Asia/Jakarta")

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

# Suppress Pyrogram invalid peer errors (happen when group is deleted/inaccessible)
logging.getLogger("pyrogram.dispatcher").addFilter(
    lambda record: "Peer id invalid" not in str(record.getMessage())
)
logging.getLogger("asyncio").addFilter(
    lambda record: "Peer id invalid" not in str(record.getMessage())
)


async def schedule_checker(client: Client):
    """Background task untuk check dan execute scheduled messages."""
    logger.info("⏰ Schedule checker dimulai.")
    logger.info(f"🕐 Waktu sistem (Jakarta): {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
    last_executed = {}  # Untuk track jadwal yang sudah dijalankan hari ini

    while True:
        try:
            now = datetime.now(TIMEZONE)
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            
            schedules = await get_active_schedules()
            
            if schedules:
                logger.debug(f"⏰ Schedule check: {current_time} - Found {len(schedules)} active schedules")
            
            for schedule_id, message_text, schedule_time in schedules:
                # Buat unique key untuk track execution per hari
                execution_key = f"{schedule_id}_{current_date}"
                
                # Cek apakah waktu sesuai (toleransi untuk menghindari miss)
                try:
                    sched_hour, sched_min = map(int, schedule_time.split(":"))
                    curr_hour, curr_min = map(int, current_time.split(":"))
                    
                    # Cek apakah waktu match (sama atau 1 menit sebelumnya)
                    time_match = False
                    if sched_hour == curr_hour and sched_min == curr_min:
                        time_match = True
                    
                    if time_match:
                        # Cek apakah sudah dijalankan hari ini
                        if execution_key not in last_executed:
                            try:
                                logger.info(f"⏰ Menjalankan jadwal {schedule_id} ({schedule_time}): {message_text[:50]}")
                                
                                # Kirim pesan ke semua grup
                                result = await send_to_groups(client, message_text)
                                
                                # Update last sent time
                                await update_schedule_sent(schedule_id)
                                last_executed[execution_key] = True
                                
                                logger.info(f"✅ Jadwal {schedule_id} tereksekusi. {len(result.success)} grup berhasil, {len(result.failed)} gagal.")
                            except Exception as e:
                                logger.error(f"❌ Error saat execute jadwal {schedule_id}: {str(e)}")
                        
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing time untuk jadwal {schedule_id}: {schedule_time} - {str(e)}")
            
            # Sleep 10 detik untuk balance antara responsivitas dan resource
            await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"Error di schedule_checker: {str(e)}")
            await asyncio.sleep(10)


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

    # Start bot untuk get owner info
    await app.start()
    me = await app.get_me()
    owner_id = me.id
    logger.info(f"Bot Owner ID: {owner_id} (@{me.username or 'no username'})")
    
    # Set owner ID untuk authorization
    set_owner_id(owner_id)

    # Register semua command handlers
    register_all_handlers(app, owner_id)

    # Jalankan bot
    logger.info("Memulai Promo Bot...")
    logger.info("Kirim /help di Saved Messages untuk melihat perintah.")
    logger.info("Bot berjalan! Tekan Ctrl+C untuk berhenti.")
    logger.info(f"🕐 Waktu sistem: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')} (Asia/Jakarta)")
    logger.info(f"⏰ Timezone: UTC+7 (Asia/Jakarta)")

    # Jalankan schedule checker sebagai background task
    asyncio.create_task(schedule_checker(app))

    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot dihentikan.")
