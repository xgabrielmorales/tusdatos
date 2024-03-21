from tusdatos.routers.auth import router as auth_router
from tusdatos.routers.healthcheck import router as healthcheck_router
from tusdatos.routers.judicial_processes import router as judicial_process_router

__all__ = (
    "judicial_process_router",
    "auth_router",
    "healthcheck_router",
)
