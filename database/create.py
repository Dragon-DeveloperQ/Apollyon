from datetime import datetime
from database.models.models import User, UserCharacter, Task



# --------- Создать пользователя ---------
async def create_user(session, logger, telegram_id: int, username: str):
    
    user = User(
        telegram_id=telegram_id,
        username=username,
        last_reminder_at=datetime.utcnow()
    )
    session.add(user) 
    await session.flush()

    logger.info(f"Пользователь создан: id={user.id}")
    return user



# --------- Создать персонажа пользователя ---------
async def create_character(session, logger, user_id: int):
    character = UserCharacter(
        user_id=user_id
        
    )
    
    session.add(character)
    await session.flush()
    
    logger.info(f"Персонаж создан: id={character.id}")
    return character



# --------- Создать задачу ---------
async def create_task(session, logger, character_id: int, title: str, description: str):

    task = Task(
        character_id=character_id,
        title=title,
        description=description
    )
    
    session.add(task)
    await session.flush()
    
    logger.info(f"Задание создано: id={task.id}, title='{task.title}'")
    return task

