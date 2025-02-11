from .main import router as main_router
from .profiles import router as profile_router
from .tasks import router as task_router
from .habits import router as habit_router
from .commands import router as commands_router
from .admin import router as admin_router
from .subscription import router as subscription_router


__all__ = [
    'main_router',
    'profile_router',
    'task_router',
    'habit_router',
    'commands_router',
    'admin_router',
    'subscription_router'
] 