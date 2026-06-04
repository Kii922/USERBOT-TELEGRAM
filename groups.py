import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from database import (
    add_group,
    remove_group,
    get_all_groups,
    add_groups_bulk,
    toggle_group,
    set_topic,
)

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
            "/groups scan"
        )   
