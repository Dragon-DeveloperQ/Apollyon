import database
import logger as logger
import asyncio

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import core.task

from . import change
from . import create
from . import read

db_logger = logger.getLogger("database")



# --------- Регистрация нового пользователя ---------
async def register_new_user(telegram_id: int, username: str):
    '''
    Регистрирует нового пользователя с заданным telegram_id и username.
    '''

    db_logger.info(f"Регестрация пользователя: telegram_id={telegram_id}, username={username}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                # Проверяем, существует ли пользователь
                user = await read.get_user_by_telegram_id(session, db_logger,telegram_id)
                if user is not None:
                    db_logger.warning(f"Пользователь с telegram_id={telegram_id} уже зарегистрирован.")
                    raise Exception("Пользователь уже зарегистрирован.")

                # Попытка создать пользователя и персонажа
                user_id = (await create.create_user(session, db_logger, telegram_id=telegram_id, username=username)).id
                await create.create_character(session, db_logger, user_id=user_id)
                
                return user
    
    except Exception as e:
        db_logger.error(f"Ошибка при регистрации пользователя telegram_id={telegram_id}: {e}")



# --------- Создание задания для персонажа ---------
async def create_task_for_character(character_id: int, title: str, description: str):
    '''
    Создает задание для персонажа с заданным character_id.
    '''

    db_logger.info(f"Создание задания для character_id={character_id}: title='{title}'...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                # Проверяем, существует ли персонаж и задание           
                character = await read.get_character_by_user_id(session, db_logger, character_id)
                task = await read.get_task_by_title_and_character(session, db_logger, title, character_id)

                if character is None:
                    db_logger.error(f"Персонаж с id={character_id} не найден. Задание не создано.")
                if task is not None:
                    db_logger.warning(f"Задание для character_id={character_id} под именем '{title}' уже существует. Новое задание не создано.")    
                
                if character is None or task is not None:
                    raise Exception("Предусловия для создания задания не выполнены.")
                
                # Попытка создать задание
                await create.create_task(session, db_logger, character_id=character_id, title=title, description=description)
                return task

    except Exception as e:
        db_logger.error(f"Ошибка при создании задания для character_id={character_id}: {e}")



# --------- Получение награды за задание ---------
async def reward_task_completion(task_id: int):
    '''
    Получение награды за выполнение задания.
    Требует task_id выполненного задания.

    При успешном выполнении: вовзращает итоговую награду
    При ошибке: возвращает None
    '''
    
    db_logger.info(f"Награждение за выполнение задания id={task_id} для пользователя...")
    
    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                # Получаем задание
                task = await read.get_task_by_id(session, db_logger, task_id)

                if task is None:
                    db_logger.error(f"Задание с id={task_id} не найдено. Награда не выдана.")
                    return None

                # Увеличение streak при надобности
                streak = await change.increment_task_streak(session, db_logger, task_id)
                if streak is None:
                    db_logger.error(f"Не удалось увеличить стрик задания id={task_id}. Награда не выдана.")
                    raise Exception("Ошибка увеличения стрика")

                # Повторно получаем задание с обновленным стриком
                task = await read.get_task_by_id(session, db_logger, task_id)

                # Рассчет сложности (заглушка)
                difficulty = 1

                # Обновление средней сложности задания
                new_difficulty_avg = core.task.newAverageDifficulty(task.difficultyAVG, difficulty, streak)
                if new_difficulty_avg is None:
                    db_logger.error(f"Ошибка при расчете новой средней сложности для задания id={task_id}. Награда не выдана.")
                    raise Exception("Ошибка расчета новой средней сложности")

                new_difficulty_avg = await change.update_task_difficulty_average(session, db_logger, task_id, new_difficulty_avg)
                if new_difficulty_avg is None:
                    db_logger.error(f"Ошибка при обновлении средней сложности для задания id={task_id}. Награда не выдана.")
                    raise Exception("Ошибка обновления средней сложности")
                
                # Повторно получаем задание с обновленным стриком
                task = await read.get_task_by_id(session, db_logger, task_id)

                # Рассчет нагрды
                reward = core.task.calculateTaskReward(task.difficultyAVG, difficulty, streak)
                if reward is None:
                    db_logger.error(f"Ошибка при расчете награды для задания id={task_id}. Награда не выдана.")
                    raise Exception("Ошибка расчета награды")
                
                # Выдача награды персонажу
                await change.update_task_reward(session, db_logger, task.character_id, reward)
                db_logger.debug(f"Награда за выполнение задания id={task_id} успешно выдана: reward={reward}")
                return reward
            
    except Exception as e:
        db_logger.error(f"Ошибка при выдаче награды за задание id={task_id}: {e}")



# ---------- Удаление задания ----------
async def delete_task(task_id: int):
    '''
    Удаляет задание с заданным task_id.
    '''

    db_logger.info(f"Удаление задания id={task_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                # Получаем задание
                task = await read.get_task_by_id(session, db_logger, task_id)
                if task is None:
                    db_logger.warning(f"Задание с id={task_id} не найдено. Удаление не выполнено.")
                    return False

                await session.delete(task)
                await session.flush()

                db_logger.info(f"Задание id={task_id} успешно удалено.")
                return True

    except Exception as e:
        db_logger.error(f"Ошибка при удалении задания id={task_id}: {e}")
        return False



async def get_all_tasks_for_character(character_id: int):
    '''
    Получает все задания для персонажа с заданным character_id.
    Возвращает список заданий или None в случае ошибки.
    '''

    db_logger.info(f"Получение всех заданий для character_id={character_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                character = await read.get_character_by_id(session, db_logger, character_id)
                if character is None:
                    db_logger.error(f"Персонаж с id={character_id} не найден. Невозможно получить задания.")
                    return None

                result = await session.execute(
                    read.select(Task).where(Task.character_id == character_id)
                )
                tasks = result.scalars().all()

                db_logger.info(f"Получено {len(tasks)} заданий для character_id={character_id}.")
                return tasks

    except Exception as e:
        db_logger.error(f"Ошибка при получении заданий для character_id={character_id}: {e}")
        return None