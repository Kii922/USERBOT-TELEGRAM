import logging
from functools import wraps
from pyrogram.types import Message
from database import is_user_registered, get_user_role

logger = logging.getLogger(__name__)

# Global owner ID (akan di-set oleh bot)
OWNER_ID = None


def set_owner_id(owner_id: int):
    """Set bot owner ID untuk authorization."""
    global OWNER_ID
    OWNER_ID = owner_id


async def check_authorization(user_id: int, require_admin: bool = False, require_owner: bool = False) -> bool:
    """
    Cek apakah user authorized untuk menggunakan command.
    - Owner selalu authorized
    - Admin bisa akses perintah admin
    - User biasa bisa akses basic commands
    """

    logger.warning(f"AUTH CHECK | user_id={user_id} | owner={OWNER_ID}")

    role = await get_user_role(user_id)
    logger.warning(f"ROLE={role}")

    registered = await is_user_registered(user_id)
    logger.warning(f"REGISTERED={registered}")

    # Owner always allowed
    if user_id == OWNER_ID:
        return True

    # Owner-only command
    if require_owner:
        return False

    # Admin-only command
    if require_admin:
        return role == "admin"

    # Default: user harus terdaftar
    return registered


def authorize(require_admin: bool = False, require_owner: bool = False):


    """
    Decorator untuk command handlers yang butuh authorization.
    
    Usage:
    @authorize()  # Hanya registered users
    async def handler(client, message):
        ...
    
    @authorize(require_admin=True)  # Hanya admin/owner
    async def handler(client, message):
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message: Message):
            user_id = message.from_user.id
            
            # Check authorization
            if not await check_authorization(user_id, require_admin, require_owner):
                if require_owner:
                    await message.reply("❌ Hanya owner yang bisa menggunakan command ini!")
                elif require_admin:
                    await message.reply("❌ Hanya admin atau owner yang bisa menggunakan command ini!")
                else:
                    await message.reply(
                        "❌ Anda belum terdaftar!\n\n"
                        "Hubungi owner untuk mendapatkan akses."
                    )
                return

            # Call original handler
            return await func(client, message)
        return wrapper
    return decorator

