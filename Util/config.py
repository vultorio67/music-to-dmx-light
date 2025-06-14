import os
import yaml
import json
from pathlib import Path


#aims to load the config data

class Config:

    def __init__(self):
        default_config = {
            'window':
                {
                    'name': 'Rekordbox'
                },
            'dmx':
                {
                    'port': "COM3"
                }
        }

        # Vérifier si le fichier existe
        if not os.path.exists('config.yaml'):
            # Si le fichier n'existe pas, le créer avec les valeurs par défaut
            with open('config.yaml', 'w') as file:
                yaml.dump(default_config, file, default_flow_style=False)
            print("Fichier config.yaml créé avec les valeurs par défaut.")

        # Charger le fichier YAML
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        # Accéder aux données
        self.windowName = config['window']['name']
        self.portDmx = config['dmx']['port']

class DMXConfigManager:
    def __init__(self, json_path="DmxConfig.json"):
        self.json_path = Path(json_path)
        self.data = {"fixtures": []}
        self.load()

    def load(self):
        if self.json_path.exists():
            with open(self.json_path, 'r') as f:
                self.data = json.load(f)

    def save(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_fixture(self, name, fixture_type, start_address, channels, position=None):
        fixture = {
            "name": name,
            "type": fixture_type,
            "start_address": start_address,
            "channels": channels
        }
        if position:
            fixture["position"] = position

        self.data["fixtures"].append(fixture)
        self.save()

    def get_fixtures(self):
        return self.data["fixtures"]

    def get_fixture_by_name(self, name):
        return next((f for f in self.data["fixtures"] if f["name"] == name), None)

    def remove_fixture(self, name):
        self.data["fixtures"] = [f for f in self.data["fixtures"] if f["name"] != name]
        self.save()

    def list_channels(self):
        return [(f["name"], f["start_address"], f["channels"]) for f in self.data["fixtures"]]


