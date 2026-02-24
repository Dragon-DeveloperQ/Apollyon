from datetime import datetime, timezone

from aiogram import Bot

import database
import logger as logger

import core.task
import core.timezone

from . import change
from . import create
from . import read

from .models import Task
from database.db import db_logger

from os import getenv
from dotenv import load_dotenv

load_dotenv("../config/core.env")
TIME_TO_EARN_DIFFICULTY = int(getenv("TIME_TO_EARN_DIFFICULTY", 1800))  # В секундах, по умолчанию 30 минут
MINIMAL_DIFFICULTY_TO_DEACTIVATE_TASK = float(getenv("MINIMAL_DIFFICULTY_TO_DEACTIVATE_TASK", 0.5))  # Минимальная сложность для деактивации задания

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
async def create_task_for_character(character_id: int, title: str, description=None):
    '''
    Создает задание для персонажа с заданным character_id.
    '''
    
    db_logger.debug(f"Создание задания для character_id={character_id}: title='{title}'...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                # Проверяем, существует ли персонаж и задание           
                character = await read.get_character_by_id(session, db_logger, character_id)
                task = await read.get_task_by_title_and_character(session, db_logger, title, character_id)

                if character is None:
                    db_logger.error(f"Персонаж с id={character_id} не найден. Задание не создано.")
                    raise Exception("Персонаж не найден.")
                if task is not None:
                    db_logger.warning(f"Задание для character_id={character_id} под именем '{title}' уже существует. Новое задание не создано.")
                    raise Exception("Задание уже существует.")   
                
                if character is None or task is not None:
                    raise Exception("Предусловия для создания задания не выполнены.")
                
                # Попытка создать задание
                await create.create_task(session, db_logger, character_id=character_id, title=title, description=description)
                return task

    except Exception as e:
        db_logger.error(f"Ошибка при создании задания для character_id={character_id}: {e}")
async def create_task_for_character_by_telegram_id(telegram_id: int, title: str, description=None):
    '''
    Создает задание для персонажа пользователя с заданным telegram_id.
    '''
    
    db_logger.debug(f"Создание задания для пользователя telegram_id={telegram_id}: title='{title}'...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                # Получаем пользователя и персонажа
                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                if user is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Задание не создано.")
                    raise Exception("Пользователь не найден.")

                character = await read.get_character_by_user_id(session, db_logger, user.id)
                if character is None:
                    db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Задание не создано.")
                    raise Exception("Персонаж не найден.")

                # Проверяем, существует ли задание
                task = await read.get_task_by_title_and_character(session, db_logger, title, character.id)
                if task is not None:
                    db_logger.warning(f"Задание для character_id={character.id} под именем '{title}' уже существует. Новое задание не создано.")    
                    raise Exception("Задание уже существует.")
                
                # Попытка создать задание
                await create.create_task(session, db_logger, character_id=character.id, title=title, description=description)
                return task

    except Exception as e:
        db_logger.error(f"Ошибка при создании задания для пользователя telegram_id={telegram_id}: {e}")


# --------- Статус задания ----------
async def activate_task(task_id: int):
    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                if await read.get_task_active_state(session, db_logger, task_id):
                    db_logger.warning(f"Задание id={task_id} уже было активно.")
                    return
                # Смена состояния задания на активное
                await change.change_task_active_state(session, db_logger, task_id, is_active=True)
                # Установить время начала задания
                await change.set_task_started_at(session, db_logger, task_id)
        
    except Exception as e:
        db_logger.error(f"Ошибка при активации задания id={task_id}: {e}")
async def deactivate_task(task_id: int):
    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                difficulty = round(await calculate_task_difficulty(session, task_id), 2)
                if difficulty is None:
                    db_logger.error(f"Ошибка при расчете сложности задания id={task_id}. Невозможно деактивировать задание.")
                    return None
                if difficulty < MINIMAL_DIFFICULTY_TO_DEACTIVATE_TASK:
                    db_logger.info(f"Недостаточная сложность для деактивации задания id={task_id}. Требуется минимум 1, получено {difficulty}.")
                    return None
                
                # Смена состояния задания на неактивное
                await change.change_task_active_state(session, db_logger, task_id, is_active=False)
                # Установить последнее время выполнения задания
                await change.set_task_completed_at(session, db_logger, task_id)
                
                telegram_id = (await read.get_user_by_task_id(session, db_logger, task_id)).telegram_id
                level_up = await check_character_level_up(session, telegram_id)
                streak = await calculate_task_streak(session, task_id) - 1
                times = await change.increment_task_completed_times(session, db_logger, task_id)
                reward = await reward_task_completion(session, task_id, difficulty, times)

                if streak is None:
                    db_logger.error(f"Ошибка при расчете стрика задания id={task_id}. Невозможно деактивировать задание.")
                    return None
                
                stats = {
                    "difficulty": difficulty,
                    "streak": streak,
                    "reward": reward
                }
                
                await level_up_character(session, telegram_id, level_up)
                return stats
    except Exception as e:
        db_logger.error(f"Ошибка при деактивации задания id={task_id}: {e}")
        return { "difficulty": "ERROR", "streak": "ERROR", "reward": "ERROR" }
async def hard_deactivate_task(task_id: int):
    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                # Смена состояния задания на неактивное
                await change.change_task_active_state(session, db_logger, task_id, is_active=False)
    except Exception as e:
        db_logger.error(f"Ошибка при намереной деактивации задания id={task_id}: {e}")

# --------- Проверка повышения уровня персонажа ---------
async def check_character_level_up(session, telegram_id: int, level_offset: int = 0):
    '''
    Проверяет, достиг ли персонаж пользователя с заданным telegram_id нового уровня.
    Возвращает необходимый опыт для повышения уровня или False в случае ошибки.
    '''

    db_logger.debug(f"Проверка повышения уровня персонажа для пользователя telegram_id={telegram_id}...")

    try:
        user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
        if user is None:
            db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Невозможно проверить уровень.")
            return False

        character = await read.get_character_by_user_id(session, db_logger, user.id)
        if character is None:
            db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Невозможно проверить уровень.")
            return False

        exp_to_level_up = core.task.calculateExpToLevelUp(character.level + 1 + level_offset)
        if exp_to_level_up < character.exp:
            db_logger.info(f"Персонажу пользователя telegram_id={telegram_id} хватает опыта, для повышения уровня: -> level={character.level + 1} ({exp_to_level_up}).")
            return True
        return False

    except Exception as e:
        db_logger.error(f"Ошибка при проверке уровня персонажа для пользователя telegram_id={telegram_id}: {e}")
        return False
async def level_up_character(session, telegram_id: int, levels: int = 1):
    '''
    Повышает уровень персонажа пользователя с заданным telegram_id.
    Возвращает новый уровень или False в случае ошибки.
    '''

    db_logger.debug(f"Повышение уровня персонажа для пользователя telegram_id={telegram_id}...")

    try:
        user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
        if user is None:
            db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Невозможно повысить уровень.")
            return False

        character = await read.get_character_by_user_id(session, db_logger, user.id)
        if character is None:
            db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Невозможно повысить уровень.")
            return False

        new_levels = 0
        exp_to_level_up = core.task.calculateExpToLevelUp(character.level + 1 + new_levels)
        while await check_character_level_up(session, telegram_id, level_offset=new_levels):
            exp_to_level_up = core.task.calculateExpToLevelUp(character.level + 1 + new_levels)
            await change.change_character_exp(session, db_logger, character.id, character.exp - exp_to_level_up)
            await change.increment_character_level(session, db_logger, character.id)
            await change.increment_character_stat_points(session, db_logger, character.id)
            new_levels += 1
        
        db_logger.info(f"Персонаж пользователя telegram_id={telegram_id} повышен на {new_levels} уровней.")
        return new_levels
    
    except Exception as e:
        db_logger.error(f"Ошибка при повышении уровня персонажа для пользователя telegram_id={telegram_id}: {e}")
        return False
    
# --------- Проверка стрика задания ---------
async def check_task_streak(session, task_id: int):
    task = await read.get_task_by_id(session, db_logger, task_id)
    if task is None:
        db_logger.error(f"Задание с id={task_id} не найдено. Невозможно проверить стрик.")
        return None

    now = (datetime.now(core.timezone.tz_from_string(await read.get_user_timezone(session, db_logger, task.character_id)))).date()
    completed_date = (await read.get_task_completed_date(session, db_logger, task_id))
    db_logger.debug(f"Проверка стрика для задания id={task_id}: now={now}, completed_date={completed_date}")
    if completed_date is None:
        delta_days = 1
    else:
        delta_days = (now - completed_date).days
        if delta_days is None or delta_days < 0:
            db_logger.error(f"Ошибка при расчете разницы дат для задания id={task_id}. Невозможно проверить стрик.")
            return None

    # db_logger.warning((datetime.now(core.timezone.tz_from_string(await read.get_user_timezone(session, db_logger, task.character_id)))))
    # db_logger.warning(f"Проверка стрика для задания id={task_id}: now={now}, completed_date={completed_date}, delta_days={delta_days}")

    return delta_days

# --------- Расчет strak задания ---------
async def calculate_task_streak(session, task_id: int):
    delta_days = await check_task_streak(session, task_id)
    #db_logger.debug(f"Расчет стрика для задания id={task_id}: take={take}")
    if delta_days == 1:
        await change.increment_task_streak(session, db_logger, task_id)
        db_logger.debug(f"Задание с id={task_id} было выполнено. Стрик увеличен.")
        return await read.get_task_streak(session, db_logger, task_id) + 1
    
    elif delta_days > 1:
        await change.reset_task_streak(session, db_logger, task_id)
        db_logger.debug(f"Задание с id={task_id} не было выполнено вчера. Стрик сброшен.")
        return 0
    
    elif delta_days == 0:
        db_logger.debug(f"Задание с id={task_id} уже было выполнено сегодня. Стрик не изменен.")
        return await read.get_task_streak(session, db_logger, task_id)
    
    else:
        db_logger.error(f"Ошибка при расчете стрика задания id={task_id}. Невозможно рассчитать стрик.")
        return None

# --------- Обнуление стриков всех не просроченных заданий персонажа ---------
async def reset_streaks_for_character_tasks(character_id: int):
    '''
    Обнуляет стрики всех заданий персонажа с заданным character_id, которые не были выполнены вчера.
    '''

    db_logger.info(f"Обнуление стриков для заданий character_id={character_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                result = await session.execute(
                    read.select(Task).where(Task.character_id == character_id)
                )
                tasks = result.scalars().all()

                for task in tasks:
                    delta_days = await check_task_streak(session, task.id)
                    if delta_days is None:
                        db_logger.error(f"Ошибка при проверке стрика задания id={task.id}. Пропуск обнуления стрика.")
                        continue
                    if delta_days > 1:
                        await change.reset_task_streak(session, db_logger, task.id)
                        db_logger.debug(f"Стрик задания id={task.id} сброшен.")

                db_logger.info(f"Обнуление стриков для заданий character_id={character_id} завершено.")

    except Exception as e:
        db_logger.error(f"Ошибка при обнулении стриков для заданий character_id={character_id}: {e}")

# --------- Рассчет сложности задания ---------
async def calculate_task_difficulty(session, task_id: int):
    #Получение время начала выполненния задания
    started_at = (await read.get_task_started_at(session, db_logger, task_id)).replace(tzinfo=timezone.utc)
    complated_at = datetime.now(timezone.utc)


    if started_at is None:
        db_logger.error(f"Время начала задания id={task_id} не установлено. Невозможно рассчитать сложность.")
        return 1
    if complated_at is None:
        db_logger.error(f"Время завершения задания id={task_id} не установлено. Невозможно рассчитать сложность.")
        return 1  

    # Отнимаем от текущего времени время начала выполнения задания
    time_difference = complated_at - started_at
    if time_difference.total_seconds() < 0:
        db_logger.error(f"Время завершения задания id={task_id} меньше времени начала. Невозможно рассчитать сложность.")
        return None
    if time_difference.total_seconds() == 0:
        db_logger.warning(f"Время выполнения задания id={task_id} равно нулю. Сложность установлена как 0.")
        return 0

    # Делим на пол часа
    difficulty = round(time_difference.total_seconds() / TIME_TO_EARN_DIFFICULTY, 2)

    return difficulty

# --------- Получение награды за задание ---------
async def reward_task_completion(session, task_id: int, difficulty: float, times: int):
    '''
    Получение награды за выполнение задания.
    Требует task_id выполненного задания.

    При успешном выполнении: вовзращает итоговую награду
    При ошибке: возвращает None
    '''
    
    db_logger.info(f"Награждение за выполнение задания id={task_id} для пользователя...")
                
    # Получаем задание
    task = await read.get_task_by_id(session, db_logger, task_id)

    if task is None:
        db_logger.error(f"Задание с id={task_id} не найдено. Награда не выдана.")
        return None

    # Обновление средней сложности задания
    new_difficulty_avg = core.task.newAverageDifficulty(task.difficultyAVG, difficulty, times)
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
    reward = core.task.calculateTaskReward(task.difficultyAVG, dificulty=difficulty, streak=task.streak)
    if reward is None:
        db_logger.error(f"Ошибка при расчете награды для задания id={task_id}. Награда не выдана.")
        raise Exception("Ошибка расчета награды")

    # Выдача награды персонажу
    await change.update_task_reward(session, db_logger, task.character_id, reward)
    db_logger.debug(f"Награда за выполнение задания id={task_id} успешно выдана: reward={reward}")
    
    # Установить дату последнего выполненния задания
    last_date = datetime.now(core.timezone.tz_from_string(await read.get_user_timezone(session, db_logger, (await read.get_user_by_task_id(session, db_logger, task_id)).telegram_id))).date()
    await change.update_task_completed_date(session, db_logger, task_id, last_date)

    return reward

# --------- Удаление задания ----------
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

# --------- Изменение задания ---------
async def change_task_name(task_id: int, new_name: str):
    '''
    Изменяет название задания с заданным task_id на new_name.
    '''

    db_logger.info(f"Смена названия задания id={task_id} на '{new_name}'...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                task = await read.get_task_by_id(session, db_logger, task_id)
                if task is None:
                    db_logger.error(f"Задание с id={task_id} не найдено. Смена названия не выполнена.")
                    return False

                await change.change_task_name(session, db_logger, task_id, new_name)

                db_logger.info(f"Название задания id={task_id} успешно изменено на '{new_name}'.")
                return True

    except Exception as e:
        db_logger.error(f"Ошибка при смене названия задания id={task_id}: {e}")
        return False
async def change_task_description(task_id: int, new_description: str):
    '''
    Изменяет описание задания с заданным task_id на new_description.
    '''

    db_logger.info(f"Смена описания задания id={task_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                task = await read.get_task_by_id(session, db_logger, task_id)
                if task is None:
                    db_logger.error(f"Задание с id={task_id} не найдено. Смена описания не выполнена.")
                    return False

                await change.change_task_description(session, db_logger, task_id, new_description)

                db_logger.info(f"Описание задания id={task_id} успешно изменено.")
                return True

    except Exception as e:
        db_logger.error(f"Ошибка при смене описания задания id={task_id}: {e}")
        return False

# --------- Получение всех заданий для персонажа ---------
async def get_all_tasks_for_character(character_id: int):
    '''
    Получает все задания для персонажа с заданным character_id.
    Возвращает список заданий или None в случае ошибки.
    '''

    db_logger.debug(f"Получение всех заданий для character_id={character_id}...")

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
async def get_all_tasks_for_character_by_telegram_id(telegram_id: int):
    '''
    Получает все задания для персонажа пользователя с заданным telegram_id.
    Возвращает список заданий или None в случае ошибки.
    '''

    db_logger.debug(f"Получение всех заданий для пользователя telegram_id={telegram_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                if user is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Невозможно получить задания.")
                    return None

                character = await read.get_character_by_user_id(session, db_logger, user.id)
                if character is None:
                    db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Невозможно получить задания.")
                    return None

                result = await session.execute(
                    read.select(Task).where(Task.character_id == character.id)
                )
                tasks = result.scalars().all()

                db_logger.info(f"Получено {len(tasks)} заданий для пользователя telegram_id={telegram_id}.")
                return tasks

    except Exception as e:
        db_logger.error(f"Ошибка при получении заданий для пользователя telegram_id={telegram_id}: {e}")
        return None
async def get_task_by_id(task_id: int):
    '''
    Получает задание с заданным task_id.
    Возвращает задание или None в случае ошибки.
    '''

    db_logger.debug(f"Получение задания id={task_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                task = await read.get_task_by_id(session, db_logger, task_id)
                if task is None:
                    db_logger.error(f"Задание с id={task_id} не найдено.")
                    return None

                db_logger.info(f"Задание id={task_id} успешно получено.")
                return task

    except Exception as e:
        db_logger.error(f"Ошибка при получении задания id={task_id}: {e}")
        return None
async def get_task_by_telegram_id(task_id: int):
    '''
    Получает задание с заданным task_id.
    Возвращает задание или None в случае ошибки.
    '''

    db_logger.debug(f"Получение задания id={task_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                task = await read.get_task_by_id(session, db_logger, task_id)
                if task is None:
                    db_logger.error(f"Задание с id={task_id} не найдено.")
                    return None

                db_logger.info(f"Задание id={task_id} успешно получено.")
                return task

    except Exception as e:
        db_logger.error(f"Ошибка при получении задания id={task_id}: {e}")
        return None

# --------- Характеристики персонажа ---------
async def increment_character_stat(telegram_id: int, stat_name: str):
    '''
    Увеличивает характеристику stat_name персонажа пользователя с заданным telegram_id на 1.
    '''

    db_logger.info(f"Увеличение характеристики '{stat_name}' персонажа пользователя telegram_id={telegram_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                if user is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Увеличение характеристики не выполнено.")
                    return False

                character = await read.get_character_by_user_id(session, db_logger, user.id)
                if character is None:
                    db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Увеличение характеристики не выполнено.")
                    return False

                if character.stat_points <= 0:
                    db_logger.debug(f"Недостаточно очков характеристик для персонажа пользователя telegram_id={telegram_id}. Увеличение характеристики не выполнено.")
                    return False

                await change.increment_character_stat(session, db_logger, character.id, stat_name)
                await change.increment_character_stat_points(session, db_logger, character.id, -1)

                db_logger.info(f"Характеристика '{stat_name}' персонажа пользователя telegram_id={telegram_id} успешно увеличена.")
                return True

    except Exception as e:
        db_logger.error(f"Ошибка при увеличении характеристики '{stat_name}' персонажа пользователя telegram_id={telegram_id}: {e}")
        return False
async def get_character_stats(telegram_id: int):
    '''
    Получает показатели персонажа пользователя с заданным telegram_id.
    Возвращает словарь с показателями или None в случае ошибки.
    '''

    #db_logger.debug(f"Получение показателей персонажа для пользователя telegram_id={telegram_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                character = await read.get_character_by_user_id(session, db_logger, user.id)
                if character is None:
                    db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Невозможно получить показатели.")
                    return None

                stats = {
                    "username": user.username,
                    "level": character.level,
                    "exp": character.exp,
                    "gold": character.gold,

                    "strength": character.strength,
                    "agility": character.agility,
                    "physique": character.physique,
                    "intelligence": character.intelligence,
                    "wisdom": character.wisdom,
                    "charisma": character.charisma,
                    "luck": character.luck,

                    "stat_points": character.stat_points
                }

                #db_logger.debug(f"Показатели персонажа для пользователя telegram_id={telegram_id} успешно получены.")
                return stats

    except Exception as e:
        db_logger.error(f"Ошибка при получении показателей персонажа для пользователя telegram_id={telegram_id}: {e}")
        return None

# --------- Смена языка пользователя ---------
async def change_user_language(telegram_id: int, new_language: str):
    '''
    Изменяет язык пользователя с заданным telegram_id на new_language.
    '''

    db_logger.info(f"Смена языка пользователя telegram_id={telegram_id} на '{new_language}'...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                if user is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Смена языка не выполнена.")
                    return False

                user.language_code = new_language
                session.add(user)
                await session.flush()

                db_logger.info(f"Язык пользователя telegram_id={telegram_id} успешно изменен на '{new_language}'.")
                return True

    except Exception as e:
        db_logger.error(f"Ошибка при смене языка пользователя telegram_id={telegram_id}: {e}")
        return False

# --------- Получение языка пользователя ---------
async def get_user_language(telegram_id: int):
    '''
    Получает язык пользователя с заданным telegram_id.
    Возвращает код языка или None в случае ошибки.
    '''

    #db_logger.debug(f"Получение языка пользователя telegram_id={telegram_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                language = await read.get_user_language_by_telegram_id(session, db_logger, telegram_id)
                if language is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Невозможно получить язык.")
                    return None

                return language

    except Exception as e:
        db_logger.error(f"Ошибка при получении языка пользователя telegram_id={telegram_id}: {e}")
        return None

# --------- Сброс персонажа пользователя ---------
async def reset_user_character(telegram_id: int):
    '''
    Сбрасывает персонажа пользователя с заданным telegram_id.
    '''

    db_logger.info(f"Сброс персонажа пользователя telegram_id={telegram_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                if user is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Сброс персонажа не выполнен.")
                    return False

                character = await read.get_character_by_user_id(session, db_logger, user.id)
                if character is None:
                    db_logger.error(f"Персонаж пользователя с telegram_id={telegram_id} не найден. Сброс персонажа не выполнен.")
                    return False

                new_character = await create.create_character(session, db_logger, user_id=character.user_id)
                if new_character is None:
                    db_logger.error(f"Не удалось создать нового персонажа для пользователя telegram_id={telegram_id}. Сброс персонажа не выполнен.")
                    return False

                character.user_id = 0
                
                session.add(character)
                await session.flush()

                db_logger.info(f"Персонаж пользователя telegram_id={telegram_id} успешно сброшен.")
                return True

    except Exception as e:
        db_logger.error(f"Ошибка при сбросе персонажа пользователя telegram_id={telegram_id}: {e}")
        return False

# --------- Сохранение часового пояса пользователя ---------
async def save_user_timezone(telegram_id: int, timezone_name: str):
    '''
    Сохраняет часовой пояс пользователя с заданным telegram_id.
    '''

    db_logger.info(f"Сохранение часового пояса '{timezone_name}' для пользователя telegram_id={telegram_id}...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
                if user is None:
                    db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Сохранение часового пояса не выполнено.")
                    return False

                await change.change_user_timezone(session, db_logger, telegram_id, timezone_name)

                db_logger.info(f"Часовой пояс '{timezone_name}' для пользователя telegram_id={telegram_id} успешно сохранен.")
                return timezone_name

    except Exception as e:
        db_logger.error(f"Ошибка при сохранении часового пояса для пользователя telegram_id={telegram_id}: {e}")
        return False

# --------- Уведомлений ---------
async def get_users_for_notifications():
    '''
    Получает всех пользователей, которые включили уведомления.
    Возвращает список пользователей или None в случае ошибки.
    '''

    db_logger.debug(f"Получение пользователей для уведомлений...")

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                users = await read.get_users_for_notifications(session, db_logger)

                db_logger.info(f"Получено {len(users)} пользователей для уведомлений.")
                return users

    except Exception as e:
        db_logger.error(f"Ошибка при получении пользователей для уведомлений: {e}")
        return None
async def get_users_for_reminders():
    '''
    Получает всех пользователей, которые включили напоминанния
    и которые находятся в статусе is_active=True.
    '''

    db_logger.debug(f"Получение пользователей для напоминаний...")
    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():

                users = await read.get_users_for_reminders(session, db_logger)

                db_logger.info(f"Получено {len(users)} пользователей для напоминаний.")
                return users

    except Exception as e:
        db_logger.error(f"Ошибка при получении пользователей для напоминаний: {e}")
        return None

async def send_reminder(bot: Bot, telegram_id: int, language_code: str):
    from telegram_bot.handlers.task import cancel_task_execution
    from telegram_bot.bot_instance import dp
    from telegram_bot.fsm import get_fsm_context
    from telegram_bot.reminders import send

    FSMcontext = await get_fsm_context(telegram_id, bot, dp.storage)
    data = await FSMcontext.get_data()
    task_id_by_character = int(data.get("task_number"))

    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                pending = await read.check_reminder_pending(session, db_logger, telegram_id)
                if pending is False:
                    await send.send_reminder(session, bot, telegram_id, db_logger, language_code)
                    await set_reminder_pending(session, telegram_id, language_code, pending=True)
                    db_logger.info(f"Напоминание для пользователя telegram_id={telegram_id} было принято в прошлом.")
        if pending:
            db_logger.info(f"Напоминание для пользователя telegram_id={telegram_id} не было принято в прошлом")
            await cancel_task_execution(telegram_id, task_id_by_character, FSMcontext, logger=db_logger, language_code=language_code, bot=bot)

            async with database.db.async_session_maker() as session:
                async with session.begin():
                    message = await read.get_reminder_pending_message_id(session, db_logger, telegram_id)
                    await bot.delete_message(
                        chat_id=telegram_id,
                        message_id=message
                    )
        
    except Exception as e:
        db_logger.error(f"Ошибка при отправке уведомлений: {e}")

async def accept_reminder(telegram_id: int, language_code: str):
    try:
        async with database.db.async_session_maker() as session:
            async with session.begin():
                await set_reminder_pending(session, telegram_id, language_code, pending=False)
    except Exception as e:
        db_logger.error(f"Ошибка при отправке уведомлений: {e}")

async def send_notification(bot: Bot, telegram_id: int, message: str):
    pass

async def set_reminder_pending(session, telegram_id: int, language_code: str, pending: bool):
    '''
    Устанавливает статус напоминания для пользователя с заданным telegram_id.
    '''

    db_logger.info(f"Установка статуса напоминания для пользователя telegram_id={telegram_id}...")

    try:
        user = await read.get_user_by_telegram_id(session, db_logger, telegram_id)
        if user is None:
            db_logger.error(f"Пользователь с telegram_id={telegram_id} не найден. Установка статуса напоминания не выполнена.")
            return False

        await change.set_reminder_pending(session, db_logger, telegram_id, pending)
        db_logger.info(f"Статус напоминания для пользователя telegram_id={telegram_id} успешно установлен.")
        return True

    except Exception as e:
        db_logger.error(f"Ошибка при установке статуса напоминания для пользователя telegram_id={telegram_id}: {e}")
        return False
    
