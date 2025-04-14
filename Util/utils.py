import json

def getColorDB():
    with open("colorDB.json", "r") as f:
        return json.load(f)