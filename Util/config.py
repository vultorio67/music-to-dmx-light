import os
import yaml


#aims to load the config data

class Config:

    def __init__(self):
        default_config = {
            'window':
                {
                    'name': 'Rekordbox'
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

