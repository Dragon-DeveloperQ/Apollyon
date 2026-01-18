import math

def calculateTaskReward(dificultyAverage, dificulty, streak):
    return round(dificulty + 0.2 * dificultyAverage * (1 + math.sqrt(dificultyAverage)*math.log1p(1 + streak)), 2)

def newAverageDifficulty(dificultyAverage: float, dificulty:float, times:int):
    ''' 
    Работает при увеличении streak на 1 после выполнения задания
    Если streak = 0, возвращает None
    '''
    
    if times == 0:
        return None

    if times > 10:
        return round((dificultyAverage * 0.8 * 9 + dificulty) / 10 , 2)
    return round((dificultyAverage * (times - 1) + dificulty) / times , 2)