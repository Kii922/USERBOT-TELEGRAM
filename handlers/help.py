from pyrogram import Client, filters
from pyrogram.types import Message


HELP_TEXT = """**Telegram Promo Bot — Panduan**

**Kirim Pesan:**
`/send <pesan>` — Kirim teks ke semua grup target
Reply media + `/send` — Forward media ke semua grup
Reply media + `/send <caption>` — Forward media + caption baru
`/sendpreview <pesan>` — Preview pesan sebelum kirim

**Manage Grup Target:**
`/groups list` — Lihat daftar grup target
`/groups scan` — Scan otomatis semua grup yang kamu ikuti
`/groups add` — Tambah grup (kirim di dalam grup/topic)
`/groups add <chat_id>` — Tambah grup via ID
`/groups add <chat_id> <topic_id>` — Tambah + set topic
`/groups remove <chat_id>` — Hapus grup dari target
`/groups on <chat_id>` — Aktifkan grup
`/groups off <chat_id>` — Nonaktifkan grup

**Topics (Grup Forum):**
`/settopic` — Set topic target (kirim di dalam topic)
`/groups topics <chat_id>` — Lihat daftar topic di grup
`/groups topic <chat_id> <topic_id>` — Set topic via ID
`/groups topic <chat_id> 0` — Reset ke General

**Info:**
`/help` — Tampilkan panduan ini
`/status` — Lihat status bot

**Tips:**
• Kirim perintah di **Saved Messages** untuk privasi
• Delay antar pesan otomatis (anti-spam)
• Gunakan /groups scan untuk menambahkan semua grup otomatis
• Untuk grup forum, set topic dulu supaya pesan masuk ke topic yang benar
"""


def register_help_handlers(app: Client):
    """Register handlers untuk help dan status."""

    @app.on_message(filters.command("help", prefixes="/") & filters.me)
    async def handle_help(client: Client, message: Message):
        await message.reply(HELP_TEXT)

    @app.on_message(filters.command("start", prefixes="/") & filters.me)
    async def handle_start(client: Client, message: Message):
        await message.reply(
            "**Selamat datang di Telegram Promo Bot!**\n\n"
            "Bot ini membantu kamu mengirim pesan promosi ke beberapa grup sekaligus.\n\n"
            "Ketik /help untuk melihat semua perintah yang tersedia."
        )

    @app.on_message(filters.command("status", prefixes="/") & filters.me)
    async def handle_status(client: Client, message: Message):
        from database import get_active_groups, get_all_groups

        all_groups = await get_all_groups()
        active_groups = await get_active_groups()

        await message.reply(
            f"**Status Bot**\n\n"
            f"Total grup target: {len(all_groups)}\n"
            f"Grup aktif: {len(active_groups)}\n"
            f"Grup nonaktif: {len(all_groups) - len(active_groups)}\n\n"
            f"Bot berjalan normal."
        )
