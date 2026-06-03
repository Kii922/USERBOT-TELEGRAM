import asyncio
import random
import logging
from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    ChatWriteForbidden,
    ChannelPrivate,
    PeerIdInvalid,
    SlowmodeWait,
)
from database import get_active_groups, log_send
from config import MIN_DELAY, MAX_DELAY

logger = logging.getLogger(__name__)


class SendResult:
    """Hasil pengiriman pesan ke semua grup."""

    def __init__(self):
        self.success: list[tuple[int, str]] = []
        self.failed: list[tuple[int, str, str]] = []

    @property
    def total(self) -> int:
        return len(self.success) + len(self.failed)

    def summary(self) -> str:
        lines = [f"Selesai! {len(self.success)}/{self.total} pesan terkirim.\n"]

        if self.success:
            lines.append("Berhasil:")
            for chat_id, title, topic_name in self.success:
                display = title or str(chat_id)
                if topic_name:
                    display += f" > {topic_name}"
                lines.append(f"  + {display}")

        if self.failed:
            lines.append("\nGagal:")
            for chat_id, title, error in self.failed:
                display = title or str(chat_id)
                lines.append(f"  - {display}: {error}")

        return "\n".join(lines)


async def send_to_groups(
    client: Client,
    text: str,
    reply_message=None,
    progress_callback=None,
) -> SendResult:
    """
    Kirim pesan teks ke semua grup target yang aktif.
    """
    result = SendResult()
    groups = await get_active_groups()

    if not groups:
        return result

    for i, (chat_id, title, topic_id, topic_name) in enumerate(groups):
        display = title or str(chat_id)
        if topic_name:
            display += f" > {topic_name}"

        status = "pending"
        error_msg = ""

        try:
            if reply_message and reply_message.media:
                await reply_message.copy(
                    chat_id,
                    caption=text if text else None,
                    reply_to_message_id=topic_id if topic_id else None,
                )
            else:
                await client.send_message(
                    chat_id,
                    text,
                    reply_to_message_id=topic_id if topic_id else None,
                )

            status = "success"
            result.success.append((chat_id, title, topic_name or ""))
            logger.info(f"Terkirim ke {display} ({chat_id}, topic={topic_id})")

        except FloodWait as e:
            wait_time = e.value
            logger.warning(f"FloodWait: tunggu {wait_time} detik")
            await asyncio.sleep(wait_time)

            try:
                if reply_message and reply_message.media:
                    await reply_message.copy(
                        chat_id,
                        caption=text if text else None,
                        reply_to_message_id=topic_id if topic_id else None,
                    )
                else:
                    await client.send_message(
                        chat_id,
                        text,
                        reply_to_message_id=topic_id if topic_id else None,
                    )

                status = "success"
                result.success.append((chat_id, title, topic_name or ""))

            except Exception as retry_err:
                status = "failed"
                error_msg = str(retry_err)
                result.failed.append((chat_id, title, error_msg))
                logger.error(f"Gagal (retry) ke {display}: {error_msg}")

        except ChatWriteForbidden:
            status = "failed"
            error_msg = "Tidak punya izin menulis di grup ini"
            result.failed.append((chat_id, title, error_msg))
            logger.error(f"Gagal ke {display}: {error_msg}")

        except ChannelPrivate:
            status = "failed"
            error_msg = "Grup ini private atau kamu sudah bukan member"
            result.failed.append((chat_id, title, error_msg))
            logger.error(f"Gagal ke {display}: {error_msg}")

        except PeerIdInvalid:
            status = "failed"
            error_msg = "ID grup tidak valid"
            result.failed.append((chat_id, title, error_msg))
            logger.error(f"Gagal ke {display}: {error_msg}")

        except SlowmodeWait as e:
            status = "failed"
            error_msg = f"Slowmode aktif, tunggu {e.value} detik"
            result.failed.append((chat_id, title, error_msg))
            logger.error(f"Gagal ke {display}: {error_msg}")

        except Exception as e:
            status = "failed"
            error_msg = str(e)
            result.failed.append((chat_id, title, error_msg))
            logger.error(f"Gagal ke {display}: {error_msg}")

        await log_send(
            chat_id,
            text[:200] if text else "(media)",
            status,
            error_msg,
            topic_id=topic_id,
        )

        if progress_callback:
            await progress_callback(
                chat_id,
                display,
                status,
                i + 1,
                len(groups),
            )

        if i < len(groups) - 1:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            logger.info(f"Delay {delay:.1f} detik...")
            await asyncio.sleep(delay)

    return result
