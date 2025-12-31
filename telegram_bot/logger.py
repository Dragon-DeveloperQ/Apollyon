import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv("../config/logging.env")
PATH = getenv("LOGS_PATH")
LEVEL = getenv("LEVEL")
FORMAT = getenv("FORMAT")

_loggers = {}


def initAllLoggers():

    loggerAiogram = logging.getLogger("Ayiogram")
    aiogramHandler = logging.FileHandler(f"{PATH}/aiogram.log", encoding="utf-8")
    loggerAiogram.addHandler(aiogramHandler)
    aiogramHandler.setFormatter(logging.Formatter(FORMAT))

    loggerMiddleware = logging.getLogger("Middleware")
    middlewareHandler = logging.FileHandler(f"{PATH}/middleware.log", encoding="utf-8")
    loggerMiddleware.addHandler(middlewareHandler)
    middlewareHandler.setFormatter(logging.Formatter(FORMAT))

    loggerDatabase = logging.getLogger("Database")
    databaseHandler = logging.FileHandler(f"{PATH}/database.log", encoding="utf-8")
    loggerDatabase.addHandler(databaseHandler)
    databaseHandler.setFormatter(logging.Formatter(FORMAT))

    loggerAiogram.setLevel(LEVEL)
    loggerMiddleware.setLevel(LEVEL)
    loggerDatabase.setLevel(LEVEL)

    _loggers["aiogram"] = loggerAiogram
    _loggers["middleware"] = loggerMiddleware
    _loggers["database"] = loggerDatabase

def getLogger(name: str) -> logging.Logger:
    return _loggers.get(name)