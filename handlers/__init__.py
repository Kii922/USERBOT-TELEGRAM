from handlers.groups import register_group_handlers
from handlers.send import register_send_handlers
from handlers.help import register_help_handlers
from handlers.schedule import register_schedule_handlers
from handlers.register import register_register_handlers


def register_all_handlers(app, owner_id):
    """Register semua command handlers."""
    register_help_handlers(app)
    register_group_handlers(app)
    register_send_handlers(app)
    register_schedule_handlers(app)
    register_register_handlers(app, owner_id)
