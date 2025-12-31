from . import start

def include_handlers(dp):
    dp.include_router(start.router)