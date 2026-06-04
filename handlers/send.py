import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from sender import send_to_groups
from database import get_active_groups

logger = logging.getLogger(__name__)


def register_send_handlers(app: Client):
    """Register handlers untuk kirim pesan promosi."""

    @app.on_message(filters.command("send", prefixes="/") & filters.me)
    async def handle_send(client: Client, message: Message):
        """
        Kirim pesan ke semua grup target.
        /send <pesan>                 — Kirim teks
        Reply media + /send           — Forward media ke semua grup
        Reply media + /send <caption>  — Forward media dengan caption baru
        """
        groups = await get_active_groups()
        if not groups:
            await message.reply(
                "Belum ada grup target!\n"
                "Gunakan /groups scan atau /groups add untuk menambah grup."
            )
            return

        # Ambil teks pesan
        text = message.text.split(maxsplit=1)[1] if len(message.text.split(maxsplit=1)) > 1 else ""

        # Cek apakah reply ke media
        reply_msg = message.reply_to_message

        if not text and not reply_msg:
            await message.reply(
                "Cara penggunaan:\n"
                "• `/send Pesan promosi kamu di sini`\n"
                "• Reply media + `/send` untuk forward media\n"
                "• Reply media + `/send Caption baru` untuk ubah caption"
            )
            return

        # Konfirmasi
        target_count = len(groups)
        status_msg = await message.reply(
            f"Mengirim ke {target_count} grup...\nMohon tunggu."
        )

        # Progress callback untuk update status
        async def on_progress(chat_id, display, status, current, total):
            if current % 3 == 0 or current == total:
                try:
                    await status_msg.edit_text(
                        f"Mengirim... {current}/{total}\n"
                        f"Terakhir: {display} — {status}"
                    )
                except Exception:
                    pass

        # Kirim!
        result = await send_to_groups(
            client=client,
            text=text,
            reply_message=reply_msg,
            progress_callback=on_progress,
        )

        # Tampilkan hasil
        await status_msg.edit_text(result.summary())

    @app.on_message(filters.command("sendpreview", prefixes="/") & filters.me)
    async def handle_send_preview(client: Client, message: Message):
        """
        Preview pesan sebelum kirim ke semua grup.
        /sendpreview <pesan>
        """
        text = message.text.split(maxsplit=1)[1] if len(message.text.split(maxsplit=1)) > 1 else ""

        if not text:
            await message.reply("Gunakan: `/sendpreview Pesan kamu di sini`")
            return

        groups = await get_active_groups()
        preview = (
            f"**Preview Pesan:**\n\n"
            f"{text}\n\n"
            f"---\n"
            f"Akan dikirim ke **{len(groups)}** grup.\n"
            f"Ketik `/send {text}` untuk mengirim."
        )
        await message.reply(preview)
