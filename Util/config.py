import os
import yaml
import json
from pathlib import Path


#aims to load the config data

class Config:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file

        default_config = {
            'window': {'name': 'Rekordbox'},
            'dmx': {'port': "COM3"},
            'fixtures': {
                "left": [
                  {
                    "name": "lyre1",
                    "adresse": 1,
                    "type": "lyreSylvain"
                  }
                ],
                "right": [
                  {
                    "name": "lyre2",
                    "adresse": 12,
                    "type": "lyreSylvain"
                  }
                ],
                "top": [

                ],
                "bottom": [

                ],
                'other': [

                ]
              }
        }

        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as file:
                yaml.dump(default_config, file, default_flow_style=False)
            print("Fichier config.yaml créé avec les valeurs par défaut.")

        with open(self.config_file, 'r') as file:
            config = yaml.safe_load(file)

        self.windowName = config['window']['name']
        self.portDmx = config['dmx']['port']
        self.fixtures_by_group = config.get('fixtures', {})

    def get_fixtures(self, group=None):
        """Retourne tous les fixtures ou ceux d'un groupe."""
        if group:
            return self.fixtures_by_group.get(group, [])
        else:
            all_fixtures = []
            for group_fixtures in self.fixtures_by_group.values():
                all_fixtures.extend(group_fixtures)
            return all_fixtures

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


