from datetime import datetime, timezone

from sqlalchemy import update, select
from sqlalchemy.exc import NoResultFound

from . import read
from .models import Base



# --------- Измененние средней сложности задания ---------
async def update_task_difficulty_average(session, logger, task_id: int, new_difficulty_avg: float):
    '''
    Обновляет значение средней сложности задания.
    '''

    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Средняя сложность не обновлена.")
        return None

    task.difficultyAVG = new_difficulty_avg
    session.add(task)
    await session.flush()

    return float(task.difficultyAVG)


# --------- Получение награды за задание ---------
async def update_task_reward(session, logger, character_id: int, reward: float):
    
    character = await read.get_character_by_id(session, logger, character_id)
    if character is None:
        logger.error(f"Персонаж с id={character_id} не найден. Награда не выдана.")
        return None
    
    character.exp += reward
    character.gold += reward

    session.add(character)
    await session.flush()
    
    return reward


# --------- Смена состояния задания ---------
async def change_task_active_state(session, logger, task_id: int, is_active: bool):
    
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Состояние не изменено.")
        return None
    
    task.is_active = is_active
    session.add(task)
    await session.flush()

    return task.is_active
async def set_task_started_at(session, logger, task_id: int):
    
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Время начала не установлено.")
        return None
    
    task.started_at = datetime.now(timezone.utc)
    session.add(task)
    await session.flush()
    
    return task.started_at

# --------- Установить последнее время выполнения задания ---------
async def set_task_completed_at(session, logger, task_id: int):
    
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Время выполнения не установлено.")
        return None
    
    task.completed_at = datetime.now(timezone.utc)
    session.add(task)
    await session.flush()
    
    return task.completed_at


# --------- Streak ---------
async def increment_task_streak(session, logger, task_id: int):
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Стрик не увеличен.")
        return None

    task.streak += 1
    task.completed_date = datetime.now(timezone.utc)
    session.add(task)
    await session.flush()
    
    return task.streak
async def reset_task_streak(session, logger, task_id: int):
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Стрик не сброшен.")
        return None

    task.streak = 0
    task.completed_date = datetime.now(timezone.utc)
    session.add(task)
    await session.flush()
    
    return task.streak

# --------- Уровень ---------
async def increment_character_level(session, logger, character_id: int):
    character = await read.get_character_by_id(session, logger, character_id)
    if character is None:
        logger.error(f"Персонаж с id={character_id} не найден. Уровень не увеличен.")
        return None

    character.level += 1
    session.add(character)
    await session.flush()
    
    return character.level
async def change_character_exp(session, logger, character_id: int, new_exp: int):
    character = await read.get_character_by_id(session, logger, character_id)
    if character is None:
        logger.error(f"Персонаж с id={character_id} не найден. Опыт не изменен.")
        return None

    character.exp = new_exp
    session.add(character)
    await session.flush()
    
    return character.exp

# --------- Смена часового пояса пользователя ---------
async def change_user_timezone(session, logger, user_id: int, new_timezone: str):
    user = await read.get_user_by_telegram_id(session, logger, user_id)
    if user is None:
        logger.error(f"Пользователь с telegram_id={user_id} не найден. Часовой пояс не изменен.")
        return None

    user.timezone = new_timezone
    session.add(user)
    await session.flush()

    return user.timezone

# --------- Увеличить количество выполнений задания ---------
async def increment_task_completed_times(session, logger, task_id: int):

    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Количество выполнений не увеличено.")
        return None

    task.completed_times += 1
    session.add(task)
    await session.flush()
    
    return task.completed_times

# --------- Сменить день последнего выполнения задания ---------
async def update_task_completed_date(session, logger, task_id: int, new_date: datetime.date):
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Дата последнего выполнения не изменена.")
        return None

    task.completed_date = new_date
    session.add(task)
    await session.flush()
    
    return task.completed_date

# --------- Смена названия задания ---------
async def change_task_name(session, logger, task_id: int, new_name: str):
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Название не изменено.")
        return None

    task.title = new_name
    session.add(task)
    await session.flush()
    
    return task.title

# --------- Смена описания задания ---------
async def change_task_description(session, logger, task_id: int, new_description: str):
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Описание не изменено.")
        return None

    task.description = new_description
    session.add(task)
    await session.flush()
    
    return task.description