from backend.routers.auth import router as auth_router
from backend.routers.products import router as products_router
from backend.routers.sales import router as sales_router
from backend.routers.inventory import router as inventory_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.hardware import router as hardware_router

__all__ = [
    "auth_router", "products_router", "sales_router",
    "inventory_router", "dashboard_router", "hardware_router",
]
