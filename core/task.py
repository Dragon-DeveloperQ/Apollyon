import math

def calculateTaskReward(dificultyAverage, dificult, streak):
    return round(dificult + 0.2 * dificultyAverage * (1 + math.sqrt(dificultyAverage)*math.log1p(1 + streak)), 2)

def newAverageDifficulty(dificultyAverage, dificult):
    return round((dificultyAverage * 0.9 * 9 + dificult) / 10 , 2)