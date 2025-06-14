import time
from abc import abstractmethod

from MusicDmx import DmxController
from MusicDmx.DmxController import DMXController
from Util import getStandartColor

class DMXFixture:
    def __init__(self, name, start_address, dmx:DmxController):
        self.name = name
        self.start_address = start_address - 1
        self.dmx = dmx

    def set_param(self, param, value):
        raise NotImplementedError

class DMXLightFixtures(DMXFixture):
    def __init__(self, name, start_adress, dmx:DmxController):
        super().__init__(name, start_adress, dmx)

    @abstractmethod
    def setColor(self):
        pass

    @abstractmethod
    def enableLight(self, isEnabled):
        pass

class CouleurDMX:
    def __init__(self, mode, color, table_macro):
        """
        mode: "rgb" ou "macro"
        table_macro: dictionnaire {nom_couleur: (min, max)} pour mode "macro"
        """
        self.mode = mode
        self.table_macro = table_macro or {}
        self.rgb = (0, 0, 0)
        self.nom_macro = "aucune"
        self.valeur_macro = 0

        if isinstance(color, str):
            self.set_color_by_name(color)
        else:
            self.set_rgb(color)

    def set_color_by_name(self, nom):
        if self.mode == "macro":
            if nom not in self.table_macro:
                raise ValueError(f"Couleur inconnue : {nom}")
            self.nom_macro = nom
            plage = self.table_macro[nom]
            self.valeur_macro = (plage[0] + plage[1]) // 2
        elif self.mode == "rgb":
            colors = getStandartColor()
            if nom not in colors:
                raise ValueError(f"Couleur inconnue dans couleurs RGB standards : {nom}")
            r, g, b = colors[nom]
            self.rgb = [r, g, b]

        else:
            raise ValueError("set_couleur_par_nom ne fonctionne qu'en mode macro")

    def set_rgb(self, r, g, b):
        if self.mode != "rgb":
            raise ValueError("set_rgb ne fonctionne qu'en mode RGB")
        self.rgb = (
            max(0, min(255, r)),
            max(0, min(255, g)),
            max(0, min(255, b))
        )

    def get_dmx(self):
        """
        Retourne les valeurs DMX à envoyer :
        - En mode RGB : [R, G, B]
        - En mode Macro : [valeur_macro]
        """
        if self.mode == "rgb":
            return list(self.rgb)
        elif self.mode == "macro":
            return self.valeur_macro
        else:
            raise ValueError(f"Mode inconnu : {self.mode}")

class GoboDMX:
    def __init__(self,nom, parameters):
        # Cherche automatiquement les gobos dans parameters["light"]["gobos"]
        self.table_gobos = parameters.get("light", {}).get("gobos", {})
        self.nom = None
        self.valeur_dmx = 0
        self.set_gobo(nom)

    def set_gobo(self, nom):
        if nom not in self.table_gobos:
            raise ValueError(f"Gobo inconnu : {nom}")
        self.nom = nom
        plage = self.table_gobos[nom]
        self.valeur_dmx = (plage[0] + plage[1]) // 2

    def get_dmx(self):
        return self.valeur_dmx

    def get_nom(self):
        return self.nom


class MyLight(DMXLightFixtures):
    def __init__(self, name, start_address, dmx:DmxController):
        super().__init__(name, start_address, dmx)
        self.parameter = {
            "movement":
                {
                    "rotation_1": 1,
                    "party_rotation": 2,
                    "lazer_rotation":3
                },
            "enable_light": 4,
            "light":
                {
                    "stroboscop_light": 5,
                    "r":6,
                    "g":7,
                    "b":8,
                    "rotation_1_light": 9,
                    "party_light":10,
                    "r_lazer":11,
                    "g_lazer":12,
                    "stroboscope_speed": 13,
                    "automatic_light":14

                }
        }

    def enableLight(self, isEnabled):
        if isEnabled:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 255)
            print(self.start_address + self.parameter["enable_light"])
        else:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 0)

    def setColor(self, color):
        dmxColor = CouleurDMX("rgb", color, None).get_dmx()
        self.dmx.set_channel(self.start_address + self.parameter["light"]["r"], dmxColor[0])
        self.dmx.set_channel(self.start_address + self.parameter["light"]["g"], dmxColor[1])
        self.dmx.set_channel(self.start_address + self.parameter["light"]["b"], dmxColor[2])
        print(self.start_address + self.parameter["light"]["r"])
        print(dmxColor[1])



"""
!!! mélange de couleur non traité
"""
#11 cannaux utilisés
class LyreSylvain(DMXLightFixtures):
    def __init__(self, name, start_address, dmx:DmxController):
        super().__init__(name, start_address, dmx)
        self.parameter = {
            "enable_light": 8,
            "movement":
                {
                    "pan": 1,
                    "pan_fine": 2,
                    "tilt": 3,
                    "tilt_fine":4
                },
            "light":
                {
                    "channel": 5,
                    "macroColors": {
                        "white":(0,9),
                        "red":(10,19),
                        "green":(20,29),
                        "blue":(30,39),
                        "yellow":(40,49),
                        "orange":(59,59),
                        "light_blue":(60,69),
                        "pink":(70,79),
                    }
                },
            "gobos":
                {
                    "channel": 6,
                    "open": (0, 7),
                    "gobo1": (8, 15),
                    "gobo2": (16, 23),
                    "gobo3": (24, 31),
                    "gobo4": (32, 39),
                    "gobo5": (40, 47),
                    "gobo6": (48, 55),
                    "gobo7": (56, 63),
                    "gobo1_shake": (64, 71),
                    "gobo2_shake": (72, 79),
                    "gobo3_shake": (80, 87),
                    "gobo4_shake": (88, 95),
                    "gobo5_shake": (96, 103),
                    "gobo6_shake": (104, 111),
                    "gobo7_shake": (112, 119),
                    "gobo_rainbow": (120, 127),
                    "gobo_auto_scroll": (128, 255)
                },
            "auto_sound": {
                "channel": 10,  # à adapter selon ton mapping
                "modes": {
                    "off": (0, 59),
                    "auto1": (60, 84),
                    "auto2": (85, 109),
                    "auto3": (110, 134),
                    "auto4": (135, 159),
                    "sound0": (160, 184),
                    "sound1": (185, 209),
                    "sound2": (210, 234),
                    "sound3": (235, 249),
                    "reset": (250, 255)
                }
            },
            "stroboscope_speed": 7
        }

    def enableLight(self, isEnabled):
        if isEnabled:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 255)
        else:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 0)

    def setColor(self, color:str):
        dmxColor = CouleurDMX("macro", color, self.parameter["light"]["macroColors"]).get_dmx()
        self.dmx.set_channel(self.start_address + self.parameter["light"]["channel"], dmxColor)

    def setGobo(self, gobo_name:str):
        mode_dict = self.parameter["gobos"]
        if gobo_name not in mode_dict:
            raise ValueError(f"Mode auto/sound inconnu : {gobo_name}")
        plage = mode_dict[gobo_name]
        valeur = (plage[0] + plage[1]) // 2
        channel = self.parameter["gobos"]["channel"]
        self.dmx.set_channel(self.start_address + channel, valeur)

    def setPanPos(self, pan_angle:int):
        self.dmx.set_channel(self.start_address + self.parameter["movement"]["pan"], pan_angle)

    def setTiltPos(self, tilt_angle:int):
        self.dmx.set_channel(self.start_address + self.parameter["movement"]["tilt"], tilt_angle)

    def setAutoMode(self, mode_name:str):
        mode_dict = self.parameter["auto_sound"]["modes"]
        if mode_name not in mode_dict:
            raise ValueError(f"Mode auto/sound inconnu : {mode_name}")
        plage = mode_dict[mode_name]
        valeur = (plage[0] + plage[1]) // 2
        channel = self.parameter["auto_sound"]["channel"]
        self.dmx.set_channel(self.start_address + channel, valeur)


dmx = DMXController("COM3")
dmx.start()

testSy = LyreSylvain("test", 1, dmx)

testEv = MyLight("test2", 12, dmx)

testSy.enableLight(True)
testEv.enableLight(True)
testSy.setColor("red")
testEv.setColor("red")
time.sleep(3)
testSy.setTiltPos(100)
testSy.setColor("pink")
testEv.setColor("pink")
testSy.setGobo("open")
time.sleep(2)
testSy.setPanPos(100)
#testSy.setAutoMode("sound0")

