import aiosqlite
from config import DB_PATH


async def init_db():
    """Inisialisasi database dan buat tabel jika belum ada."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS target_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                title TEXT DEFAULT '',
                topic_id INTEGER DEFAULT NULL,
                topic_name TEXT DEFAULT '',
                is_forum INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS send_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                topic_id INTEGER DEFAULT NULL,
                message_text TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        # Migrasi: tambah kolom topic jika belum ada (untuk database lama)
        try:
            await db.execute("ALTER TABLE target_groups ADD COLUMN topic_id INTEGER DEFAULT NULL")
            await db.execute("ALTER TABLE target_groups ADD COLUMN topic_name TEXT DEFAULT ''")
            await db.execute("ALTER TABLE target_groups ADD COLUMN is_forum INTEGER DEFAULT 0")
            await db.execute("ALTER TABLE send_log ADD COLUMN topic_id INTEGER DEFAULT NULL")
            await db.commit()
        except Exception:
            pass


async def add_group(chat_id: int, title: str = "", is_forum: bool = False) -> bool:
    """Tambah grup ke daftar target. Return True jika berhasil."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO target_groups (chat_id, title, is_forum) VALUES (?, ?, ?)",
                (chat_id, title, 1 if is_forum else 0),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # Update is_forum jika grup sudah ada
            await db.execute(
                "UPDATE target_groups SET is_forum = ?, title = ? WHERE chat_id = ?",
                (1 if is_forum else 0, title, chat_id),
            )
            await db.commit()
            return False


async def remove_group(chat_id: int) -> bool:
    """Hapus grup dari daftar target. Return True jika berhasil."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM target_groups WHERE chat_id = ?", (chat_id,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_active_groups() -> list[tuple[int, str, int | None, str]]:
    """Ambil semua grup target yang aktif. Return list of (chat_id, title, topic_id, topic_name)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT chat_id, title, topic_id, topic_name FROM target_groups WHERE is_active = 1"
        )
        rows = await cursor.fetchall()
        return [(row["chat_id"], row["title"], row["topic_id"], row["topic_name"]) for row in rows]


async def get_all_groups() -> list[tuple[int, str, int, int | None, str, int]]:
    """Ambil semua grup target. Return list of (chat_id, title, is_active, topic_id, topic_name, is_forum)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT chat_id, title, is_active, topic_id, topic_name, is_forum FROM target_groups ORDER BY added_at"
        )
        rows = await cursor.fetchall()
        return [
            (row["chat_id"], row["title"], row["is_active"], row["topic_id"], row["topic_name"], row["is_forum"])
            for row in rows
        ]


async def toggle_group(chat_id: int, is_active: int) -> bool:
    """Aktifkan/nonaktifkan grup. Return True jika berhasil."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE target_groups SET is_active = ? WHERE chat_id = ?",
            (is_active, chat_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def set_topic(chat_id: int, topic_id: int | None, topic_name: str = "") -> bool:
    """Set topic target untuk grup tertentu. Return True jika berhasil."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE target_groups SET topic_id = ?, topic_name = ? WHERE chat_id = ?",
            (topic_id, topic_name, chat_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def log_send(chat_id: int, message_text: str, status: str, error_message: str = "", topic_id: int | None = None):
    """Catat log pengiriman pesan."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO send_log (chat_id, topic_id, message_text, status, error_message) VALUES (?, ?, ?, ?, ?)",
            (chat_id, topic_id, message_text[:200], status, error_message),
        )
        await db.commit()


async def add_groups_bulk(groups: list[tuple[int, str, bool]]) -> int:
    """Tambah banyak grup sekaligus. Return jumlah yang berhasil ditambahkan."""
    count = 0
    async with aiosqlite.connect(DB_PATH) as db:
        for chat_id, title, is_forum in groups:
            try:
                await db.execute(
                    "INSERT INTO target_groups (chat_id, title, is_forum) VALUES (?, ?, ?)",
                    (chat_id, title, 1 if is_forum else 0),
                )
                count += 1
            except aiosqlite.IntegrityError:
                # Update is_forum & title jika sudah ada
                await db.execute(
                    "UPDATE target_groups SET is_forum = ?, title = ? WHERE chat_id = ?",
                    (1 if is_forum else 0, title, chat_id),
                )
        await db.commit()
    return count
