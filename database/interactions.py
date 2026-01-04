import database
import logger as logger
import asyncio

from . import create
from . import read

db_logger = logger.getLogger("database")


# --------- Регистрация нового пользователя ---------
async def register_new_user(telegram_id: int, username: str):
    db_logger.info(f"Регестрация пользователя: telegram_id={telegram_id}, username={username}")

    # Проверяем, существует ли пользователь
    async with database.db.async_session_maker() as session:
        user =await read.get_user_by_telegram_id(session, db_logger,telegram_id)
    if user is not None:
        db_logger.warning(f"Пользователь с telegram_id={telegram_id} уже зарегистрирован.")
        return

    # Попытка создать пользователя и персонажа
    try:
        async with database.db.async_session_maker() as session:
            user_id = (await create.create_user(session, db_logger, telegram_id=telegram_id, username=username)).id
            await create.create_character(session, db_logger, user_id=user_id)
    except Exception as e:
        db_logger.error(f"Ошибка при регистрации пользователя telegram_id={telegram_id}: {e}")


# --------- Создание задания для персонажа ---------
async def create_task_for_character(character_id: int, title: str, description: str):
    db_logger.info(f"Создание задания для character_id={character_id}: title='{title}'")

    # Проверяем, существует ли персонаж и задание
    async with database.db.async_session_maker() as session:
        character = await read.get_character_by_user_id(session, db_logger, character_id)
        task = await read.get_task_by_title_and_character(session, db_logger, title, character_id)

    if character is None:
        db_logger.error(f"Персонаж с id={character_id} не найден. Задание не создано.")
    if task is not None:
        db_logger.warning(f"Задание для character_id={character_id} под именем '{title}' уже существует. Новое задание не создано.")    
    
    if character is None or task is not None:
        return
    
    # Попытка создать задание
    try:
        async with database.db.async_session_maker() as session:
            await create.create_task(session, db_logger, character_id=character_id, title=title, description=description)
    except Exception as e:
        db_logger.error(f"Ошибка при создании задания для character_id={character_id}: {e}")