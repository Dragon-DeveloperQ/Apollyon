from .middleware import Middleware

def include_middlewares(dp):
    dp.update.middleware(Middleware())