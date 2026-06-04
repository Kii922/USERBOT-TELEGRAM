from handlers.groups import register_group_handlers
from handlers.send import register_send_handlers
from handlers.help import register_help_handlers


def register_all_handlers(app):
    """Register semua command handlers."""
    register_help_handlers(app)
    register_group_handlers(app)
    register_send_handlers(app)
