from . import read


# --------- Измененние средней сложности задания ---------
async def update_task_difficulty_average(session, logger, task_id: int, new_difficulty_avg: float):

    task = await read.get_task_by_id(session, logger, task_id)
    if task is None:
        logger.error(f"Задание с id={task_id} не найдено. Средняя сложность не обновлена.")
        return None

    task.difficultyAVG = new_difficulty_avg
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    logger.debug(f"Средняя сложность задания обновлена: id={task.id}, difficultyAVG={task.difficultyAVG}")
    return 


# --------- Получение награды за задание ---------
async def update_task_reward(session, logger, cheracter_id: int, reward: float):
    
    character = await read.get_character_by_id(session, logger, cheracter_id)
    character.exp += reward
    character.level += reward

    session.add(character)
    await session.commit()
    await session.refresh(character)
    
    logger.debug(f"Награда за задание добавлена персонажу: id={character.id}, experience={character.exp}, gold={character.gold}")
    return