import json
import random
import time


def getColorDB():
    with open("colorDB.json", "r") as f:
        return json.load(f)
def getStandartColor():
    couleurs_rgb_standard = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "amber": (255, 191, 0),
        "pink": (255, 102, 204),
        "orange": (255, 165, 0)
    }
    return couleurs_rgb_standard


def random_color():
    colors = ["red", "blue", "green", "yellow", "orange", "pink", "white"]
    return random.choice(colors)

def warm_color():
    warm_colors = ["red", "orange", "yellow", "pink"]
    return random.choice(warm_colors)

def cool_color():
    cool_colors = ["blue", "green", "purple", "cyan"]
    return random.choice(cool_colors)

def randomGobo():
    gobo =  [
    "open",
    "gobo1",
    "gobo2",
    "gobo3",
    "gobo4",
    "gobo5",
    "gobo6",
    "gobo7",
    "gobo1_shake",
    "gobo2_shake",
    "gobo3_shake",
    "gobo4_shake",
    "gobo5_shake",
    "gobo6_shake",
    "gobo7_shake",
    "gobo_rainbow",
    "gobo_auto_scroll"
    ]

    return random.choice(gobo)


def calculateSleepTime(controller) -> float:
    median = float(controller.showGenerator.estimate_median_and_fill())
    diff = controller.getCurrentTime() - controller.showGenerator.getLastBeatTime()

    # si le beat est passé avant
    if diff < median / 3:
        sleepTime = median - diff
    else:
        sleepTime = 2 * median - diff

    return sleepTime

def sleepBeatTime(controller, times:int):
    for i in range(times):
        sleepTime = calculateSleepTime(controller)
        time.sleep(sleepTime)
