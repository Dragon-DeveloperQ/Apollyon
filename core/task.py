import math

def calculateTaskReward(dificultyAverage, dificult, streak):
    return round(dificult + 0.2 * dificultyAverage * (1 + math.sqrt(dificultyAverage)*math.log1p(1 + streak)), 2)

def newAverageDifficulty(dificultyAverage, dificult, streak):
    ''' 
    Работает при увеличении streak на 1 после выполнения задания
    Если streak = 0, возвращает None
    '''
    
    if streak == 0:
        return None

    if streak > 10:
        return round((dificultyAverage * 0.8 * 9 + dificult) / 10 , 4)
    return round((dificultyAverage * (streak - 1) + dificult) / streak , 4)