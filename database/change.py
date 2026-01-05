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

    logger.debug(f"Средняя сложность задания обновлена: id={task.id}, difficultyAVG={task.difficultyAVG}")
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



# --------- Увеличение стрика задания ---------
async def increment_task_streak(session, logger, task_id: int):
    
    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Стрик не увеличен.")
        return None
    
    '''
    -------------------------------------------------------------------------------------
    Тут нужна проверка на время выполнения задания
    Проверка, не опоздал ли пользователь, в таком случае сброс стрика
    Проверка, не выполнялось ли задание уже сегодня, в таком случае не увеличиваем стрик
    -------------------------------------------------------------------------------------
    '''
    
    task.streak += 1
    session.add(task)
    await session.flush()
    
    logger.debug(f"Стрик задания увеличен: id={task.id}, streak={task.streak}")
    return task.streak