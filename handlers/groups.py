import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from database import (
    add_group,
    remove_group,
    remove_all_groups,
    get_all_groups,
    add_groups_bulk,
    toggle_group,
    set_topic,
)
from auth import authorize

logger = logging.getLogger(__name__)


def get_topic_id(message: Message):
    return (
        getattr(message, "message_thread_id", None)
        or getattr(message, "reply_to_top_message_id", None)
        or getattr(message, "reply_to_message_id", None)
    )


def register_group_handlers(app: Client):
    """Register handlers untuk manage grup target."""

    @app.on_message(filters.command("groups", prefixes="/") & filters.me)
    @authorize()
    async def handle_groups(client: Client, message: Message):
        parts = message.text.split(maxsplit=3)
        subcommand = parts[1].lower() if len(parts) > 1 else "list"

        if subcommand == "list":
            await _list_groups(message)
        elif subcommand == "scan":
            await _scan_groups(client, message)
        elif subcommand == "add":
            await _add_group(client, message, parts)
        elif subcommand == "remove":
            await _remove_group(message, parts)
        elif subcommand == "on":
            await _toggle(message, parts, active=True)
        elif subcommand == "off":
            await _toggle(message, parts, active=False)
        elif subcommand == "topic":
            await _set_topic(client, message, parts)
        elif subcommand == "topics":
            await _list_topics(client, message, parts)
        else:
            await message.reply(
                "Gunakan: /groups list | scan | add | remove | on | off | topic | topics"
            )

    @app.on_message(filters.command("settopic", prefixes="/") & filters.me)
    @authorize()
    async def handle_settopic(client: Client, message: Message):
        if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            await message.reply("Perintah ini hanya bisa digunakan di dalam grup.")
            return

        topic_id = get_topic_id(message)

        if not topic_id:
            await message.reply(
                "Jalankan /settopic di dalam topic forum yang ingin dijadikan target."
            )
            return

        chat_id = message.chat.id
        topic_name = ""

        try:
            topics = await client.get_forum_topics(chat_id)
            for topic in topics:
                if topic.id == topic_id:
                    topic_name = topic.title
                    break
        except Exception:
            topic_name = f"Topic #{topic_id}"

        success = await set_topic(
            chat_id,
            topic_id,
            topic_name or f"Topic #{topic_id}"
        )

        if success:
            await message.reply(
                f"Topic target diset!\n"
                f"Grup: **{message.chat.title}**\n"
                f"Topic: **{topic_name or topic_id}** (ID: `{topic_id}`)"
            )
        else:
            await message.reply(
                "Grup belum ada di daftar target. Tambahkan dulu dengan /groups add"
            )


async def _add_group(client: Client, message: Message, parts: list[str]):
    if len(parts) > 2:
        try:
            chat_id = int(parts[2])
        except ValueError:
            await message.reply("ID grup harus angka.")
            return

        # Cek apakah ada topic_id di parts[3]
        topic_id = None
        if len(parts) > 3:
            try:
                topic_id = int(parts[3])
            except ValueError:
                await message.reply("Topic ID harus angka.")
                return

        try:
            chat = await client.get_chat(chat_id)
            title = chat.title or ""
            is_forum = getattr(chat, "is_forum", False) or False
        except Exception:
            title = ""
            is_forum = False

        await add_group(chat_id, title, is_forum)
        await message.reply(f"Grup **{title or chat_id}** ditambahkan!")

    elif message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        chat_id = message.chat.id
        is_forum = getattr(message.chat, "is_forum", False) or False

        await add_group(
            chat_id,
            message.chat.title or "",
            is_forum
        )

        topic_id = get_topic_id(message)
        topic_name = ""

        if topic_id:
            try:
                topics = await client.get_forum_topics(chat_id)
                for t in topics:
                    if t.id == topic_id:
                        topic_name = t.title
                        break
            except Exception:
                pass

            topic_name = topic_name or f"Topic #{topic_id}"
            await set_topic(chat_id, topic_id, topic_name)

            await message.reply(
                f"Grup **{message.chat.title}** ditambahkan!\n"
                f"Topic: **{topic_name}** (ID: `{topic_id}`)"
            )
        else:
            await message.reply(
                f"Grup **{message.chat.title}** ditambahkan!"
            )

    else:
        await message.reply(
            "Gunakan:\n"
            "/groups add\n"
            "/groups add <chat_id>\n"
            "/groups add <chat_id> <topic_id>\n"
            "/groups scan"
        )


async def _list_groups(message: Message):
    """Tampilkan daftar grup target."""
    groups = await get_all_groups()
    
    if not groups:
        await message.reply("Belum ada grup target. Gunakan /groups add atau /groups scan")
        return
    
    text = "**Daftar Grup Target:**\n\n"
    for i, (chat_id, title, is_active, topic_id, topic_name, is_forum) in enumerate(groups, 1):
        status = "✅" if is_active else "❌"
        display = title or str(chat_id)
        forum_badge = "🧵" if is_forum else ""
        text += f"{i}. {status} {forum_badge} {display} (ID: `{chat_id}`)\n"
        if topic_name:
            text += f"   └─ Topic: {topic_name} (ID: `{topic_id}`)\n"
    
    await message.reply(text)


async def _scan_groups(client: Client, message: Message):
    """Scan semua grup yang user ikuti."""
    status_msg = await message.reply("Scanning grup...")
    
    count = 0
    errors = []
    
    try:
        async for dialog in client.get_dialogs():
            if dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                try:
                    is_forum = getattr(dialog.chat, "is_forum", False) or False
                    await add_group(dialog.chat.id, dialog.chat.title or "", is_forum)
                    count += 1
                except Exception as e:
                    errors.append(str(e))
    except Exception as e:
        errors.append(str(e))
    
    text = f"Scan selesai! Ditambahkan {count} grup.\n"
    if errors:
        text += f"Errors: {len(errors)} (lihat log)"
    
    await status_msg.edit(text)


async def _remove_group(message: Message, parts: list[str]):
    """Hapus grup dari target."""
    if len(parts) < 3:
        await message.reply("Gunakan: /groups remove <chat_id> atau /groups remove all")
        return
    
    # Cek apakah confirm DULU (sebelum cek "all")
    if len(parts) > 3 and parts[2].lower() == "all" and parts[3].lower() == "confirm":
        removed = await remove_all_groups()
        await message.reply(
            f"✅ Selesai! **{removed} grup** berhasil dihapus dari target."
        )
        return
    
    # Cek apakah "all" (tanpa confirm)
    if parts[2].lower() == "all":
        all_groups = await get_all_groups()
        if not all_groups:
            await message.reply("Tidak ada grup untuk dihapus.")
            return
        
        total = len(all_groups)
        await message.reply(
            f"⚠️ **PERINGATAN**\n\n"
            f"Anda akan menghapus **{total} grup** dari target.\n\n"
            f"Ketik `/groups remove all confirm` untuk konfirmasi."
        )
        return
    
    # Remove single group
    try:
        chat_id = int(parts[2])
    except ValueError:
        await message.reply("ID grup harus angka atau gunakan 'all'.")
        return
    
    success = await remove_group(chat_id)
    if success:
        await message.reply(f"Grup ID `{chat_id}` dihapus dari target.")
    else:
        await message.reply(f"Grup ID `{chat_id}` tidak ditemukan.")


async def _toggle(message: Message, parts: list[str], active: bool):
    """Aktifkan atau nonaktifkan grup."""
    if len(parts) < 3:
        cmd = "on" if active else "off"
        await message.reply(f"Gunakan: /groups {cmd} <chat_id>")
        return
    
    try:
        chat_id = int(parts[2])
    except ValueError:
        await message.reply("ID grup harus angka.")
        return
    
    success = await toggle_group(chat_id, active)
    status = "diaktifkan" if active else "dinonaktifkan"
    if success:
        await message.reply(f"Grup ID `{chat_id}` {status}.")
    else:
        await message.reply(f"Grup ID `{chat_id}` tidak ditemukan.")


async def _set_topic(client: Client, message: Message, parts: list[str]):
    """Set topic untuk grup target."""
    if len(parts) < 4:
        await message.reply("Gunakan: /groups topic <chat_id> <topic_id>")
        return
    
    try:
        chat_id = int(parts[2])
        topic_id = int(parts[3])
    except ValueError:
        await message.reply("chat_id dan topic_id harus angka.")
        return
    
    topic_name = f"Topic #{topic_id}"
    
    try:
        topics = await client.get_forum_topics(chat_id)
        for t in topics:
            if t.id == topic_id:
                topic_name = t.title
                break
    except Exception:
        pass
    
    success = await set_topic(chat_id, topic_id, topic_name)
    if success:
        await message.reply(
            f"Topic untuk grup `{chat_id}` diset ke:\n"
            f"**{topic_name}** (ID: `{topic_id}`)"
        )
    else:
        await message.reply(f"Grup `{chat_id}` tidak ditemukan.")


async def _list_topics(client: Client, message: Message, parts: list[str]):
    """Tampilkan daftar topics di grup."""
    if len(parts) < 3:
        await message.reply("Gunakan: /groups topics <chat_id>")
        return
    
    try:
        chat_id = int(parts[2])
    except ValueError:
        await message.reply("chat_id harus angka.")
        return
    
    try:
        topics = await client.get_forum_topics(chat_id)
        text = "**Daftar Topics:**\n\n"
        for i, topic in enumerate(topics, 1):
            text += f"{i}. {topic.title} (ID: `{topic.id}`)\n"
        await message.reply(text)
    except Exception as e:
        await message.reply(f"Error: {str(e)}")


def register_all_handlers(app: Client):
    """Register semua group handlers."""
    register_group_handlers(app)
