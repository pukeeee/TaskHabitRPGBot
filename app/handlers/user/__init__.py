from .main import router as main_router
from .profiles import router as profile_router
from .tasks import router as task_router
from .habits import router as habit_router
from .subscription import router as subscription_router

user_routers = [main_router, profile_router, task_router, habit_router, subscription_router]

__all__ = [
    'user_routers'
]