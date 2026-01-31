from sqlalchemy import select
from database.models.models import User, UserCharacter, Task, UserPreferences

# --------- Получить пользователя по ID ---------
async def get_user_by_id(session, user_id: int):
    user = await session.get(User, user_id)
    
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

# --------- Получить персонажа по ID ---------
async def get_character_by_id(session, logger, character_id: int):
    character = await session.get(UserCharacter, character_id)
    return character

# --------- Получить задачу по ID ---------
async def get_task_by_id(session, logger, task_id: int):
    task = await session.get(Task, task_id)
    return task

# --------- Получить задачу по названию и имени персонажа ---------
async def get_task_by_title_and_character(session, logger, title: str, character_id: int):
    result = await session.execute(
        select(Task).where(Task.title == title, Task.character_id == character_id)
    )
    return result.scalar_one_or_none()

# --------- Получить язык пользователя по telegram_id ---------
async def get_user_language_by_telegram_id(session, logger, telegram_id: int):

    result = await session.execute(
        select(User.language_code).where(User.telegram_id == telegram_id)
    )
    language = result.scalar_one_or_none()
    return language

# --------- Получить состояние задания ---------
async def get_task_active_state(session, logger, task_id: int):
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        return task.is_active
    return None

# --------- Получить время начало выполнения задания ---------
async def get_task_started_at(session, logger, task_id: int):
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        return task.started_at
    return None

# --------- Получить часовой пояс пользователя ---------
async def get_user_timezone(session, logger, telegram_id: int):
    result = await session.execute(
        select(User.timezone).where(User.telegram_id == telegram_id)
    )
    timezone_str = result.scalar_one_or_none()
    return timezone_str

# --------- Получить дату последнего выполненния задания ---------
async def get_task_completed_date(session, logger, task_id: int):
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        return task.completed_date
    return None

# --------- Получить стрик задания ---------
async def get_task_streak(session, logger, task_id: int):
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if task:
        return task.streak
    return None

# --------- Получить пользователя по заданию ---------
async def get_user_by_task_id(session, logger, task_id: int):
    result = await session.execute(
        select(User).join(UserCharacter).join(Task).where(Task.id == task_id)
    )
    user = result.scalar_one_or_none()
    return user

# --------- Получить всех пользователей для уведомлений ---------
async def get_users_for_notifications(session, logger):
    try:
        users = await session.execute(
            select(User).where(User.notifications_enabled == True)
        )
        users = users.scalars().all()

        logger.info(f"Получено {len(users)} пользователей для уведомлений.")
        return users

    except Exception as e:
        logger.error(f"Ошибка при получении пользователей для уведомлений: {e}")
        return []