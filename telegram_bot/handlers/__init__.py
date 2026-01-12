from .start import router as start_router
from .profile import router as profile_router
from .task import router as task_router
from .settings import router as settings_router

def include_handlers(dp):
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(task_router)
    dp.include_router(settings_router)