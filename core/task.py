import math

def calculateTaskReward(dificultyAverage, dificult, streak):
    return dificult + 0.2 * dificultyAverage * (1 + math.sqrt(dificultyAverage)*math.log1p(1 + streak))

def newAverageDifficulty(dificultyAverage, dificult):
    return (dificultyAverage * 0.9 * 9 + dificult) / 10 