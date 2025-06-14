import json

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
        "pink": (255, 102, 204)
    }
    return couleurs_rgb_standard