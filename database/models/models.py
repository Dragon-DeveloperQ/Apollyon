from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship

# Базовый класс для всех моделей
Base = declarative_base()

#=================== Модель пользователя ===================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=True)
    username = Column(String(255), nullable=True)
    
    # Связи с другими моделями
    character = relationship("UserCharacter", back_populates="user", uselist=False)
    


# ============== Модель персонажа пользователя =============
class UserCharacter(Base):
    __tablename__ = "user_characters"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Связь с User

    level = Column(Integer, default=0)
    exp = Column(Integer, default=0)
    gold = Column(Integer, default=0)

    
    '''Основные характеристики персонажа. 
    Каждая характеристика имеет формулу расчета показателя, 
    на основе этого базового модификатора.
    Формулы расчет будут храниться в core'''
    strength = Column(Integer, default=1)
    agility = Column(Integer, default=1)
    physique = Column(Integer, default=1)
    intelligence = Column(Integer, default=1)
    wisdom = Column(Integer, default=1)
    charisma = Column(Integer, default=1)
    luck = Column(Integer, default=1)

    user = relationship("User", back_populates="character")
    tasks = relationship("Task", back_populates="character")


# ==================== Модель задач ========================
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("user_characters.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    difficultyAVG = Column(Integer, default=0)
    streak = Column(Integer, default=0)

    character = relationship("UserCharacter", back_populates="tasks")