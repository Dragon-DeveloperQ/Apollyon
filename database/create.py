from database.models.models import User, UserCharacter, Task

# --------- Создать пользователя ---------
async def create_user(session, logger, telegram_id: int, username: str):
    
    user = User(
        telegram_id=telegram_id,
        username=username
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"Пользователь создан: id={user.id}")
    return user


# --------- Создать персонажа пользователя ---------
async def create_character(session, logger, user_id: int):
    character = UserCharacter(
        user_id=user_id,
    )
    
    session.add(character)
    await session.commit()
    await session.refresh(character)
    
    logger.info(f"Персонаж создан: id={character.id}")
    return character


# --------- Создать задачу ---------
async def create_task(session, logger, user_id: int, title: str, description: str, difficulty: int):

    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        difficulty=difficulty
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    logger.info(f"Task created: id={task.id}, title='{task.title}'")
    return task
