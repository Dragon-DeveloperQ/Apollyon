import math
from os import getenv
from dotenv import load_dotenv

load_dotenv("../config/curves.env")
REWARD_GROWTH = float(getenv("REWARD_GROWTH"))
LEVEL_BASE = float(getenv("LEVEL_BASE"))
LEVEL_GROWTH = float(getenv("LEVEL_GROWTH"))

def calculateTaskReward(dificultyAverage, dificulty, streak):
    '''
    f(difficulty, dificultyAverage, streak) = difficulty + g * difficultyAverage * (1 + math.sqrt(difficultyAverage)*math.log1p(1 + streak)), 2)
    '''
    return round(dificulty + 0.2 * dificultyAverage * (REWARD_GROWTH + math.sqrt(dificultyAverage)*math.log1p(1 + streak)), 2)

def newAverageDifficulty(dificultyAverage: float, dificulty:float, times:int):
    ''' 
    Работает при увеличении times на 1 после выполнения задания
    Если times = 0, возвращает None
    '''
    
    if times == 0:
        return None

    if times > 10:
        return round((dificultyAverage * 0.8 * 9 + dificulty) / 10 , 2)
    return round((dificultyAverage * (times - 1) + dificulty) / times , 2)


def calculateExpToLevelUp(level:int):
    ''' 
    f(n) = b + n^(g)
    '''
    return round(LEVEL_BASE + level**(LEVEL_GROWTH), 2)