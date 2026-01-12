from .logger_middleware import LoggerMiddleware

def include_middlewares(dp):
    dp.update.middleware(LoggerMiddleware())