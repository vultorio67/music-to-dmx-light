import json
import random


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


def calculateSleepTime(controller) -> float:
    median = float(controller.showGenerator.estimate_median_and_fill())
    diff = controller.getCurrentTime() - controller.showGenerator.getLastBeatTime()

    # si le beat est passé avant
    if diff < median / 3:
        sleepTime = median - diff
    else:
        sleepTime = 2 * median - diff

    return sleepTime
