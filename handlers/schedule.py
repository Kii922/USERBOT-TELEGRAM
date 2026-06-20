import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from database import (
    add_schedule,
    get_all_schedules,
    remove_schedule,
    toggle_schedule,
    get_active_schedules,
)
from sender import send_to_groups
from auth import authorize

logger = logging.getLogger(__name__)


def register_schedule_handlers(app: Client):
    """Register handlers untuk schedule otomatis."""

    @app.on_message(filters.command("schedule", prefixes="/") & filters.me)
    @authorize()
    async def handle_schedule(client: Client, message: Message):
        parts = message.text.split(maxsplit=3)
        subcommand = parts[1].lower() if len(parts) > 1 else "list"

        if subcommand == "list":
            await _list_schedules(message)
        elif subcommand == "add":
            await _add_schedule(message, parts)
        elif subcommand == "remove":
            await _remove_schedule(message, parts)
        elif subcommand == "on":
            await _toggle_schedule(message, parts, active=True)
        elif subcommand == "off":
            await _toggle_schedule(message, parts, active=False)
        elif subcommand == "test":
            await _test_schedule(client, message, parts)
        else:
            await message.reply(
                "Gunakan: /schedule list | add <HH:MM> | remove <id> | on <id> | off <id> | test <id>"
            )


async def _list_schedules(message: Message):
    """Tampilkan daftar jadwal pesan dengan numbering 1,2,3..."""
    schedules = await get_all_schedules()

    if not schedules:
        await message.reply("Tidak ada jadwal. Gunakan /schedule add <HH:MM> untuk menambah.")
        return

    text = "**Daftar Jadwal Pesan:**\n\n"
    for index, (schedule_id, msg_text, time, is_active) in enumerate(schedules, 1):
        status = "✅" if is_active else "❌"
        preview = msg_text[:50] + "..." if len(msg_text) > 50 else msg_text
        text += f"{index}. {status} **{time}** — `{preview}`\n"

    text += "\n**Gunakan nomor urutan (1,2,3...) untuk command:**\n/schedule on <no> — Aktifkan\n/schedule off <no> — Nonaktifkan\n/schedule remove <no> — Hapus\n/schedule test <no> — Test"
    await message.reply(text)


async def _get_schedule_by_index(index: int) -> tuple | None:
    """Convert numbering (1,2,3) ke schedule ID. Return (schedule_id, msg_text, time, is_active) atau None."""
    schedules = await get_all_schedules()
    if 1 <= index <= len(schedules):
        return schedules[index - 1]  # Convert 1-based ke 0-based index
    return None


async def _add_schedule(message: Message, parts: list[str]):
    """Tambah jadwal pesan baru."""
    if len(parts) < 4:
        await message.reply(
            "Gunakan: /schedule add <HH:MM> <pesan>\n"
            "Contoh: /schedule add 09:30 Assalamualaikum"
        )
        return

    time = parts[2]
    msg_text = message.text.split(maxsplit=3)[3]

    # Validasi format HH:MM
    try:
        hours, minutes = map(int, time.split(":"))
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError
    except (ValueError, IndexError):
        await message.reply("Format jam tidak valid. Gunakan HH:MM (contoh: 09:30)")
        return

    schedule_id = await add_schedule(msg_text, time)
    await message.reply(
        f"✅ Jadwal ditambahkan!\n\n"
        f"ID: `{schedule_id}`\n"
        f"Waktu: **{time}**\n"
        f"Pesan: `{msg_text}`\n\n"
        f"Bot akan mengirim pesan ke semua grup target pada jam tersebut setiap hari."
    )


async def _remove_schedule(message: Message, parts: list[str]):
    """Hapus jadwal pesan."""
    if len(parts) < 3:
        await message.reply("Gunakan: /schedule remove <nomor>")
        return

    try:
        index = int(parts[2])
    except ValueError:
        await message.reply("Nomor harus angka.")
        return
    
    schedule_data = await _get_schedule_by_index(index)
    if not schedule_data:
        await message.reply(f"Jadwal nomor `{index}` tidak ditemukan.")
        return
    
    schedule_id = schedule_data[0]
    success = await remove_schedule(schedule_id)
    if success:
        await message.reply(f"✅ Jadwal nomor `{index}` dihapus.")
    else:
        await message.reply(f"Error saat menghapus jadwal nomor `{index}`.")


async def _toggle_schedule(message: Message, parts: list[str], active: bool):
    """Aktifkan atau nonaktifkan jadwal."""
    if len(parts) < 3:
        cmd = "on" if active else "off"
        await message.reply(f"Gunakan: /schedule {cmd} <nomor>")
        return

    try:
        index = int(parts[2])
    except ValueError:
        await message.reply("Nomor harus angka.")
        return

    schedule_data = await _get_schedule_by_index(index)
    if not schedule_data:
        await message.reply(f"Jadwal nomor `{index}` tidak ditemukan.")
        return
    
    schedule_id = schedule_data[0]
    success = await toggle_schedule(schedule_id, active)
    status = "diaktifkan" if active else "dinonaktifkan"
    if success:
        await message.reply(f"✅ Jadwal nomor `{index}` {status}.")
    else:
        await message.reply(f"Error saat mengupdate jadwal nomor `{index}`.")


async def _test_schedule(client: Client, message: Message, parts: list[str]):
    """Test trigger jadwal secara manual."""
    if len(parts) < 3:
        await message.reply("Gunakan: /schedule test <nomor>")
        return
    
    try:
        index = int(parts[2])
    except ValueError:
        await message.reply("Nomor harus angka.")
        return
    
    schedule_data = await _get_schedule_by_index(index)
    if not schedule_data:
        await message.reply(f"Jadwal nomor `{index}` tidak ditemukan.")
        return
    
    schedule_id, msg_text, stime, is_active = schedule_data
    
    if not is_active:
        await message.reply(f"Jadwal nomor `{index}` tidak aktif. Aktifkan dulu dengan /schedule on {index}")
        return
    
    # Test trigger
    status_msg = await message.reply(f"🧪 Testing jadwal {index}...\nJam: **{stime}**\nPesan: `{msg_text}`")
    
    try:
        result = await send_to_groups(client, msg_text)
        await status_msg.edit(
            f"✅ Test berhasil!\n\n"
            f"Jadwal: **{stime}** (nomor {index})\n"
            f"Pesan terkirim: **{len(result.success)}/{result.total}**\n"
            f"Pesan: `{msg_text}`"
        )
        logger.info(f"Manual test jadwal {index} (ID: {schedule_id}) dijalankan.")
    except Exception as e:
        await status_msg.edit(f"❌ Error: {str(e)}")
        logger.error(f"Error test jadwal {index}: {str(e)}")
