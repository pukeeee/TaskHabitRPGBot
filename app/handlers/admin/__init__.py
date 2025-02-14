from .admin import router as admin_router
from .subscription import router as subscription_router

admin_routers = [admin_router, subscription_router]

__all__ = [
    'admin_routers'
] 