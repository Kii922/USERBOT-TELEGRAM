from pyrogram import Client, filters
from pyrogram.types import Message
from auth import authorize


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
`/groups remove all` — Hapus SEMUA grup (perlu konfirmasi)
`/groups on <chat_id>` — Aktifkan grup
`/groups off <chat_id>` — Nonaktifkan grup

**Topics (Grup Forum):**
`/settopic` — Set topic target (kirim di dalam topic)
`/groups topics <chat_id>` — Lihat daftar topic di grup
`/groups topic <chat_id> <topic_id>` — Set topic via ID
`/groups topic <chat_id> 0` — Reset ke General

**Jadwal Otomatis:**
`/schedule list` — Lihat daftar jadwal pesan (nomor 1,2,3...)
`/schedule add <HH:MM> <pesan>` — Tambah jadwal baru
`/schedule test <nomor>` — Test trigger jadwal secara manual
`/schedule on <nomor>` — Aktifkan jadwal
`/schedule off <nomor>` — Nonaktifkan jadwal
`/schedule remove <nomor>` — Hapus jadwal

**Contoh Penggunaan Jadwal:**
```
/schedule add 08:00 Pagi, ada promo nih! 🎉
/schedule add 12:30 Siang! Jangan lupa makan
/schedule add 18:00 Malam, ada diskon 50%
```
Bot akan kirim pesan ke semua grup target pada jam yang ditentukan setiap hari.
Format: `HH:MM` (24 jam), contoh: `09:30`, `18:45`

**User Registration (Owner Only):**
`/register @username` — Register user baru dengan role 'user'
`/register @username admin` — Register user sebagai 'admin'
`/unregister @username` — Hapus user dari registrasi
`/users` — Lihat daftar semua user terdaftar
`/users promote @username` — Jadikan user sebagai admin
`/users demote @username` — Cabut admin privilege
`/users ban @username` — Nonaktifkan user
`/users unban @username` — Aktifkan user kembali

**Catatan:**
• Gunakan **nomor urutan** (1,2,3...) untuk remove/on/off, bukan ID
• Nomor akan selalu reset 1,2,3 meski ada yang dihapus
• Gunakan `/schedule test <nomor>` untuk test tanpa tunggu jam aslinya
• Hanya user yang terdaftar yang bisa menggunakan command

**Info:**
`/help` — Tampilkan panduan ini
`/status` — Lihat status bot

**Tips:**
• Kirim perintah di **Saved Messages** untuk privasi
• Delay antar pesan otomatis (anti-spam)
• Gunakan /groups scan untuk menambahkan semua grup otomatis
• Untuk grup forum, set topic dulu supaya pesan masuk ke topic yang benar
• Jadwal akan berjalan otomatis setiap hari pada jam yang ditentukan
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
    @authorize()
    async def handle_status(client: Client, message: Message):
        from database import get_active_groups, get_all_groups, get_all_users

        all_groups = await get_all_groups()
        active_groups = await get_active_groups()
        all_users = await get_all_users()

        await message.reply(
            f"**Status Bot**\n\n"
            f"**Grup Target:**\n"
            f"Total: {len(all_groups)}\n"
            f"Aktif: {len(active_groups)}\n"
            f"Nonaktif: {len(all_groups) - len(active_groups)}\n\n"
            f"**User Registered:**\n"
            f"Total: {len(all_users)}\n\n"
            f"Bot berjalan normal."
        )
