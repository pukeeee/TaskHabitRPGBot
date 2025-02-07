from .main import router as main_router
from .profiles import router as profile_router
from .tasks import router as task_router
from .habits import router as habit_router

__all__ = [
    'main_router',
    'profile_router',
    'task_router',
    'habit_router'
] 