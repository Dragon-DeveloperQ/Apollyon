from . import start
from . import profile
from . import task
from . import settings

def include_handlers(dp):
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(task.router)
    dp.include_router(settings.router)