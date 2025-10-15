import yaml
import logging
import os

class SquareSelection():
    def __init__(self, x, y, width, heigth):
        self.x = x
        self.y = y
        self.width = width
        self.heigth = heigth

def get_beat_bar_position(yaml_path="zones.yaml") -> int:
    if not os.path.exists(yaml_path):
        logging.error(f"Zones file not found: {yaml_path}")
        return {}

    with open(yaml_path, "r") as f:
        zones_data = yaml.safe_load(f)
    return zones_data["beat_bar_position"]["pos"]


def load_zones_from_yaml(yaml_path="zones.yaml"):
    """
    Load zones from a YAML file and return a dict of SquareSelection objects.
    """
    if not os.path.exists(yaml_path):
        logging.error(f"Zones file not found: {yaml_path}")
        return {}

    with open(yaml_path, "r") as f:
        zones_data = yaml.safe_load(f)

    zones = {}
    for name, rect in zones_data.items():
        try:
            zones[name] = SquareSelection(
                rect["x"], rect["y"], rect["width"], rect["height"]
            )
        except KeyError as e:
            logging.error(f"Missing key {e} in zone '{name}'")

    return zones
