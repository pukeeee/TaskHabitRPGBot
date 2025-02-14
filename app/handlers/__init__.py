from .commands import commands_routers
from .user import user_routers
from .admin import admin_routers

__all__ = [
    *commands_routers,
    *user_routers,
    *admin_routers
]