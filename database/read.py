from sqlalchemy import select
from database.models.models import User, UserCharacter, Task

# --------- Получить пользователя по ID ---------
async def get_user_by_id(session, logger, user_id: int):
    user = await session.get(User, user_id)
    
    if user is None:
        logger.warning(f"Пользователь с id={user_id} не найден.")
    
    return user


# --------- Получить пользователя по telegram_id ---------
async def get_user_by_telegram_id(session, logger, telegram_id: int):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    return user


# --------- Получить персонажа пользователя по user_id ---------
async def get_character_by_user_id(session, logger, user_id: int):
    result = await session.execute(
        select(UserCharacter).where(UserCharacter.user_id == user_id)
    ) 
    return result.scalar_one_or_none()


# --------- Получить задачу по ID ---------
async def get_task_by_id(session, logger, task_id: int):
    task = await session.get(Task, task_id)
    return task