import math
import threading
import time
from abc import abstractmethod, ABC
from typing import Callable, Optional

from MusicDmx import DmxSignalGenerator
from MusicDmx.DmxSignalGenerator import DMXSignalGenerator
from Util import getStandartColor, Config

cfg = Config()

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

    def set_rgb(self, color):
        if self.mode != "rgb":
            raise ValueError("set_rgb ne fonctionne qu'en mode RGB")
        self.rgb = (
            max(0, min(255, color[0])),
            max(0, min(255, color[1])),
            max(0, min(255, color[2]))
        )
    def getRed(self):
        return self.rgb[0]

    def getGreen(self):
        return self.rgb[1]

    def getBlue(self):
        return self.rgb[2]

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

class DMXFixture(ABC):
    def __init__(self, name, start_address, dmx):
        self.name = name
        self.start_address = start_address - 1
        self.dmx = dmx
        self.isRunnigEffect = False

    @abstractmethod
    def enableAutoMode(self, value):
        pass

    def set_param(self, param, value):
        raise NotImplementedError


class DMXLightFixtures(DMXFixture):
    def __init__(self, name, start_adress, dmx):
        super().__init__(name, start_adress, dmx)

    @abstractmethod
    def setColor(self):
        pass

    @abstractmethod
    def enableLight(self, isEnabled):
        pass

    @abstractmethod
    def setStroboscopeSpeed(self, speed:int):
        pass

    @abstractmethod
    def turnOffAllLight(self):
        pass

class DMXLightRGBFixtures(DMXLightFixtures):

    def __init__(self, name, start_adress, dmx):
        super().__init__(name, start_adress, dmx)
        self._fade_thread = None
        self._fade_lock = threading.Lock()
        self._running = False
        self.current_color = (0, 0, 0)  # RGB

    def fade_to_color(self, color:str, duration: float = 2.0):
        dmxColor = CouleurDMX("rgb", color, None).get_dmx()
        def fade():
            steps = 50
            sleep_time = duration / steps
            start_r, start_g, start_b = self.current_color

            for step in range(1, steps + 1):
                with self._fade_lock:
                    r = int(start_r + (dmxColor[0] - start_r) * step / steps)
                    g = int(start_g + (dmxColor[1] - start_g) * step / steps)
                    b = int(start_b + (dmxColor[2] - start_b) * step / steps)
                    newColor = CouleurDMX("rgb", (r,g,b), None).get_dmx()
                    self.setColor(newColor)
                time.sleep(sleep_time)

        if self._fade_thread and self._fade_thread.is_alive():
            # Si un fade est en cours, on le stoppe
            self._fade_thread.join()

        self._fade_thread = threading.Thread(target=fade, daemon=True)
        self._fade_thread.start()

    def _run_pattern(self, colors, mode: str, duration: float):
        def pattern():
            self._running = True
            while self._running:
                for color in colors:
                    if not self._running:
                        break
                    if mode == "jump":
                        self.setColor(CouleurDMX("rgb", color, None).get_dmx())
                        time.sleep(duration)
                    elif mode == "fade":
                        self.fade_to_color(color, duration)
                        time.sleep(duration)

        if self._fade_thread and self._fade_thread.is_alive():
            self._running = False
            self._fade_thread.join()

        self._fade_thread = threading.Thread(target=pattern, daemon=True)
        self._fade_thread.start()

    def stop_effect(self):
        self._running = False
        if self._fade_thread and self._fade_thread.is_alive():
            self._fade_thread.join()

    def jump3(self, duration: float = 0.5):
        colors = ["red", "green", "blue"]
        self._run_pattern(colors, "jump", duration)

    def jump7(self, duration: float = 0.5):
        colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white"]
        self._run_pattern(colors, "jump", duration)

    def fade3(self, duration: float = 1.0):
        colors = ["red", "green", "blue"]
        self._run_pattern(colors, "fade", duration)

    def fade7(self, duration: float = 1.0):
        colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white"]
        self._run_pattern(colors, "fade", duration)

class DMXMovingFixture(DMXFixture):

    def __init__(self, name, start_address, dmx):
        super().__init__(name, start_address, dmx)
        self._motion_thread = None
        self._motion_lock = threading.Lock()
        self._running = False

    def start_motion(self, target_func, *args, **kwargs):
        """
        Lance une fonction de mouvement (comme move_to, pan_loop...) dans un thread.

        :param target_func: fonction à exécuter dans le thread
        :param args, kwargs: arguments à passer à la fonction
        """
        def thread_target():
            with self._motion_lock:
                self._running = True
                target_func(*args, **kwargs)
                self._running = False

        if self._motion_thread and self._motion_thread.is_alive():
            self.stop_motion()

        self._motion_thread = threading.Thread(target=thread_target, daemon=True)
        self._motion_thread.start()

    def stop_motion(self):
        self._running = False
        if self._motion_thread:
            self._motion_thread.join()

    def is_moving(self):
        return self._motion_thread and self._motion_thread.is_alive()

    @abstractmethod
    def goToHomePosition(self):
        pass

    ###### different mouvement accélerer #####
    def ease_in_out_quad(self, t):
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

    def ease_in_sine(self, t):
        return 1 - math.cos((t * math.pi) / 2)

    def ease_out_sine(self, t):
        return math.sin((t * math.pi) / 2)

    def ease_in_exp(self, t):
        return t ** 3

    def ease_out_exp(self, t):
        return 1 - (1 - t) ** 3


class MyLight(DMXLightRGBFixtures):
    def __init__(self, name, start_address, dmx):
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
        self.current_color = (dmxColor[0], dmxColor[1], dmxColor[2])

    def turnOffAllLight(self):
        self.setColor((0,0,0))
        self.setPartyLight(0)
        self.setRotation1Light(0)
        self.setGreenLAZERLight(0)
        self.setRedLAZERLight(0)
        self.setStroboscopeSpeed(0)

    def setRotation1Light(self, intensity):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["rotation_1_light"], intensity)

    def setPartyLight(self, intensity):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["party_light"], intensity)

    def setRedLAZERLight(self, intensity):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["r_lazer"], intensity)

    def setGreenLAZERLight(self, intensity):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["g_lazer"], intensity)

    def setStroboscopeSpeed(self, speed:int):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["stroboscope_speed"], speed)
        self.dmx.set_channel(self.start_address + self.parameter["light"]["stroboscop_light"], speed)

    def enableAutoMode(self, value):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["automatic_light"], value)

    def setRotationSpeed(self,speed:int):
        self.dmx.set_channel(self.start_address + self.parameter["movement"]["rotation_1"], speed)
    def setPartyLightRotationSpeed(self,speed:int):
        self.dmx.set_channel(self.start_address + self.parameter["movement"]["party_rotation"], speed)
    def setLAZERRotationSpeed(self,speed:int):
        self.dmx.set_channel(self.start_address + self.parameter["movement"]["lazer_rotation"], speed)



"""
!!! mélange de couleur non traité
"""
#11 cannaux utilisés
#pan en degréé * 2
# tilt : 125 c'es tdroit
class LyreSylvain(DMXLightFixtures, DMXMovingFixture):
    def __init__(self, name, start_address, dmx):
        super().__init__(name, start_address, dmx)
        self.currentPan = 0
        self.currentTilt = 0
        self._task_done = threading.Event()
        self._thread = None
        self.lock = threading.Lock()
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
        self.mirror_slave = []
        self.center_pan = cfg

    def addSlave(self, slave):
        self.mirror_slave.append(slave)

    def enableLight(self, isEnabled):
        if isEnabled:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 255)
        else:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 0)

    def setColor(self, color:str):
        dmxColor = CouleurDMX("macro", color, self.parameter["light"]["macroColors"]).get_dmx()
        self.dmx.set_channel(self.start_address + self.parameter["light"]["channel"], dmxColor)

    def setStroboscopeSpeed(self, speed:int):
        self.dmx.set_channel(self.start_address + self.parameter["stroboscope_speed"], speed)

    def turnOffAllLight(self):
        self.enableLight(False)
        self.setStroboscopeSpeed(0)


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
        self.currentPan = pan_angle

    def setTiltPos(self, tilt_angle:int):
        self.dmx.set_channel(self.start_address + self.parameter["movement"]["tilt"], tilt_angle)
        self.currentTilt = tilt_angle

    def setPos(self, pan:int, tilt:int):
        self.setPanPos(pan)
        self.setTiltPos(tilt)
        self._notify_slaves()

    def _notify_slaves(self):
        for slave in self.mirror_slave:
            mirrored_pan = int(-self.currentPan+ 2 * cfg.centerPan)
            if 0 < mirrored_pan < 255:
                slave.setPos(mirrored_pan, self.currentTilt)

    def goToHomePosition(self):
        self.setPos(cfg.centerPan, 0)

    def move_to(self, pan_target, tilt_target, duration=1.0, steps=40):
        def motion():
            pan = self.currentPan
            tilt = self.currentTilt
            pan_step = (pan_target - pan) / steps
            tilt_step = (tilt_target - tilt) / steps

            for _ in range(steps):
                if not self._running:
                    break
                pan += pan_step
                tilt += tilt_step
                self.setPos(int(pan), int(tilt))
                time.sleep(duration / steps)

        self.start_motion(motion)

    def move_to_arc(self, pan_target, tilt_target, duration=1.0, radius = 1, steps=40):
        def motion():
            x0, y0 = self.currentPan, self.currentTilt
            x1, y1 = pan_target, tilt_target

            dx = x1 - x0
            dy = y1 - y0
            dist = math.hypot(dx, dy)

            if dist == 0 or radius == 0:
                # Pas de déplacement ou rayon nul, on fait un mouvement direct
                pan_step = dx / steps
                tilt_step = dy / steps
                for _ in range(steps):
                    if not self._running:
                        break
                    x0 += pan_step
                    y0 += tilt_step
                    self.setPos(int(x0), int(y0))
                    time.sleep(duration / steps)
                return

            # Calcul de l'angle entre départ et arrivée
            angle = math.atan2(dy, dx)

            # Calcul du centre du cercle (orthogonal au vecteur déplacement)
            mx = (x0 + x1) / 2
            my = (y0 + y1) / 2

            # vecteur orthogonal
            ox = -dy / dist
            oy = dx / dist

            # Il y a deux centres possibles (à gauche ou à droite du segment)
            cx = mx + ox * math.sqrt(max(radius ** 2 - (dist / 2) ** 2, 0))
            cy = my + oy * math.sqrt(max(radius ** 2 - (dist / 2) ** 2, 0))

            # Angle de départ et d’arrivée depuis le centre
            start_angle = math.atan2(y0 - cy, x0 - cx)
            end_angle = math.atan2(y1 - cy, x1 - cx)

            # Détermination du sens du mouvement (horaire ou anti-horaire)
            # Pour forcer le sens, on peut ajouter un paramètre optionnel
            delta_angle = end_angle - start_angle
            if delta_angle < -math.pi:
                delta_angle += 2 * math.pi
            elif delta_angle > math.pi:
                delta_angle -= 2 * math.pi

            for i in range(steps + 1):
                if not self._running:
                    break
                t = i / steps
                theta = start_angle + delta_angle * t
                x = cx + radius * math.cos(theta)
                y = cy + radius * math.sin(theta)
                self.setPos(int(x), int(y))
                time.sleep(duration / steps)

        self.start_motion(motion)

    def ellipse(self, center_pan, center_tilt, radius_pan, radius_tilt, duration=2.0, loops=1, steps=100):
        def motion():
            for i in range(int(loops * steps)):
                if not self._running:
                    break
                angle = (2 * math.pi * i) / steps
                pan = center_pan + radius_pan * math.cos(angle)
                tilt = center_tilt + radius_tilt * math.sin(angle)
                self.setPos(int(pan), int(tilt))
                time.sleep(duration / steps)

        self.start_motion(motion)

    def centerEllipse(self, center_tilt, radius_pan, radius_tilt, duration=2.0, loops=1, steps=100):
        return self.ellipse(cfg.centerPan, center_tilt, radius_pan, radius_tilt, duration, loops, steps)

    def circle(self, center_pan, center_tilt, radius, duration=2.0, loops=1, steps=100):
        self.ellipse(center_pan, center_tilt, radius, radius, duration, loops, steps)

    def centerCircle(self, center_tilt, radius, duration=2.0, loops=1, steps=100):
        self.ellipse(cfg.centerPan, center_tilt, radius, radius, duration, loops, steps)

    def sweep_horizontal(self, min_pan, max_pan, tilt, duration=2.0, loops=1, steps=50):
        def motion():
            for loop in range(loops):
                for i in range(steps):
                    if not self._running:
                        return
                    pan = min_pan + (max_pan - min_pan) * (i / steps)
                    self.setPos(int(pan), tilt)
                    time.sleep(duration / (2 * steps))
                for i in range(steps):
                    if not self._running:
                        return
                    pan = max_pan - (max_pan - min_pan) * (i / steps)
                    self.setPos(int(pan), tilt)
                    time.sleep(duration / (2 * steps))

        self.start_motion(motion)

    def figure_8(self, center_pan, center_tilt, radius_pan, radius_tilt, duration=4.0, loops=1, steps=100):
        def motion():
            for i in range(int(loops * steps)):
                if not self._running:
                    break
                t = (2 * math.pi * i) / steps
                pan = center_pan + radius_pan * math.sin(t)
                tilt = center_tilt + radius_tilt * math.sin(2 * t)
                self.setPos(int(pan), int(tilt))
                time.sleep(duration / steps)

        self.start_motion(motion)

    def diagonal_scan(self, pan_min, pan_max, tilt_min, tilt_max, duration=3.0, steps=50, loops=1):
        def motion():
            for _ in range(loops):
                for i in range(steps):
                    if not self._running:
                        return
                    alpha = i / steps
                    pan = pan_min + (pan_max - pan_min) * alpha
                    tilt = tilt_min + (tilt_max - tilt_min) * alpha
                    self.setPos(int(pan), int(tilt))
                    time.sleep(duration / (2 * steps))
                for i in range(steps):
                    if not self._running:
                        return
                    alpha = i / steps
                    pan = pan_max - (pan_max - pan_min) * alpha
                    tilt = tilt_max - (tilt_max - tilt_min) * alpha
                    self.setPos(int(pan), int(tilt))
                    time.sleep(duration / (2 * steps))

        self.start_motion(motion)

    def wave_horizontal(self, pan_min, pan_max, center_tilt, amplitude, duration=3.0, steps=100):
        def motion():
            for i in range(steps):
                if not self._running:
                    return
                t = (2 * math.pi * i) / steps
                pan = pan_min + (pan_max - pan_min) * (i / steps)
                tilt = center_tilt + amplitude * math.sin(t)
                self.setPos(int(pan), int(tilt))
                time.sleep(duration / steps)

        self.start_motion(motion)

    def zigzag(self, pan_min, pan_max, tilt_min, tilt_max, steps=10, duration=2.0, loops=1):
        def motion():
            for _ in range(loops):
                for i in range(steps):
                    if not self._running:
                        return
                    pan = pan_min if i % 2 == 0 else pan_max
                    tilt = tilt_min + (tilt_max - tilt_min) * (i / steps)
                    self.setPos(int(pan), int(tilt))
                    time.sleep(duration / steps)

        self.start_motion(motion)

    def move_to_variable_speed(self, pan_target, tilt_target, duration=2.0, steps=40, easing_function=None):
        if easing_function is None:
            easing_function = lambda t: t  # linéaire

        def motion():
            start_pan = self.currentPan
            start_tilt = self.currentTilt

            for step in range(steps + 1):
                if not self._running:
                    break
                t = step / steps  # entre 0 et 1
                eased_t = easing_function(t)
                current_pan = start_pan + (pan_target - start_pan) * eased_t
                current_tilt = start_tilt + (tilt_target - start_tilt) * eased_t
                self.setPos(int(current_pan), int(current_tilt))
                time.sleep(duration / steps)

        self.start_motion(motion)

    def enableAutoMode(self, mode_name:str):
        mode_dict = self.parameter["auto_sound"]["modes"]
        if mode_name not in mode_dict:
            raise ValueError(f"Mode auto/sound inconnu : {mode_name}")
        plage = mode_dict[mode_name]
        valeur = (plage[0] + plage[1]) // 2
        channel = self.parameter["auto_sound"]["channel"]
        self.dmx.set_channel(self.start_address + channel, valeur)


class RGBStripLed(DMXLightRGBFixtures):

    def __init__(self):
        self.parameter = {
            "enable_light": 1,
            "light":
                {
                    "r": 2,
                    "g": 3,
                    "b": 4,
                    "stroboscope_speed": 5,

                }
        }

    def enableLight(self, isEnabled):
        if isEnabled:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 255)
        else:
            self.dmx.set_channel(self.start_address + self.parameter["enable_light"], 0)

    def setColor(self, color):
        dmxColor = CouleurDMX("rgb", color, None).get_dmx()
        self.dmx.set_channel(self.start_address + self.parameter["light"]["r"], dmxColor[0])
        self.dmx.set_channel(self.start_address + self.parameter["light"]["g"], dmxColor[1])
        self.dmx.set_channel(self.start_address + self.parameter["light"]["b"], dmxColor[2])
        self.current_color = (dmxColor[0], dmxColor[1], dmxColor[2])

    def setStroboscopeSpeed(self, speed: int):
        self.dmx.set_channel(self.start_address + self.parameter["light"]['stroboscope_speed'], speed)

    def turnOffAllLight(self):
        self.dmx.set_channel(self.start_address + self.parameter["light"]["r"], 0)
        self.dmx.set_channel(self.start_address + self.parameter["light"]["g"], 0)
        self.dmx.set_channel(self.start_address + self.parameter["light"]["b"], 0)

    def enableAutoMode(self, value):
        pass

    def set_param(self, param, value):
        pass

class UVLight(DMXLightFixtures):
    def __init__(self):
        self.parameter = {
            "enable_light": 1,
            "light": {
                "u": 2,
                "stroboscope_speed": 3,
            }
        }

    def enableLight(self, isEnabled):
        pass

    def setStroboscopeSpeed(self, speed: int):
        pass

    def turnOffAllLight(self):
        pass


class LyreGroup:
    def __init__(self, lyres):
        self.lyres = lyres

    # comme la méhode existe pas on l'applique à l'ensemble des lyres du groupe
    def __getattr__(self, attr):
        def group_method(*args, **kwargs):
            for lyre in self.lyres:
                method = getattr(lyre, attr, None)
                if callable(method):
                    method(*args, **kwargs)
                else:
                    print(f"[WARN] {lyre.name} n’a pas la méthode {attr}")
        return group_method

    def soumis(self, master_group):
        min_count = min(len(self.lyres), len(master_group.lyres))
        for i in range(min_count):
            slave = self.lyres[i]
            master = master_group.lyres[i]
            master.addSlave(slave)





"""

testSy = LyreSylvain("test", 1, dmx)

testSy2 = LyreSylvain("test2", 12, dmx)

testSy.enableLight(True)
testSy2.enableLight(True)
testSy.setPos(255, 0)
testSy2.setPos(255, 0)
testSy.setColor("red")
testSy2.setColor("red")
time.sleep(3)
testSy.setTiltPos(100)
testSy2.setTiltPos(100)
testSy.setColor("pink")
testSy2.setColor("pink")
testSy.setGobo("open")
time.sleep(2)
testSy.setPanPos(100)
testSy2.setPanPos(100)"""
#testSy.setAutoMode("sound0")

