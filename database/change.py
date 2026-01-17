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


# --------- Увеличение стрика задания ---------
async def increment_task_streak(session, logger, task_id: int):
    
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Стрик не увеличен.")
        return None
    
    
    
    task.streak += 1
    session.add(task)
    await session.flush()
    
    return task.streak