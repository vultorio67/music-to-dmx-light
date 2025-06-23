import threading
import time
from abc import ABC, abstractmethod
import random

import Util.utils
from MusicDmx import DmxController
from MusicDmx.Univers_DMX import Univers_DMX
from MusicDmx.fixtures.DmxFixtures import *


class Scene(ABC):
    def __init__(self, univers_dmx: Univers_DMX):
        self.univers_dmx = univers_dmx
        self.running = False
        self.id = -1
        self.loopTime = -1

    @abstractmethod
    def activate(self):
        pass

    def start(self):
        if self.running:
            return  # déjà en cours
        self.running = True
        threading.Thread(target=self.activate).start()

    def stop(self, resetLight:bool=False):
        self.running = False
        if resetLight:
            self.univers_dmx.turnOffAllLight()


class BeamIntro(Scene):
    def __init__(self, univers_dmx:Univers_DMX):
        super().__init__(univers_dmx)
        self.id = 1
    def activate(self):
        u = self.univers_dmx

        test = self.univers_dmx.right_element[0]
        test2 = self.univers_dmx.left_element[0]
        test3 = self.univers_dmx.top_element[0]
        print(type(test2))
        print(isinstance(test, LyreSylvain))

        if isinstance(test, LyreSylvain):
            print("ok")
            test.enableLight(True)
            test.setPos(20, 30)
            test.setColor("pink")




class BlackScene(Scene):

    def __init__(self, univers_dmx:Univers_DMX, home_position=False):
        super().__init__(univers_dmx)
        self.id = 1
        self.home_position = home_position

    def activate(self):
        for fixture in self.univers_dmx.getAllFixtures():
            if isinstance(fixture, DMXLightFixtures):
                fixture.turnOffAllLight()
            if isinstance(fixture, DMXMovingFixture) and self.home_position == True:
                fixture.goToHomePosition()
        self.stop()

class WhiteScene(Scene):
    def __init__(self, univers_dmx:Univers_DMX):
        super().__init__(univers_dmx)
        self.id = 2

    def activate(self):
        for fixture in self.univers_dmx.getAllFixtures():
            if isinstance(fixture, DMXLightFixtures):
                fixture.enableLight(True)
                fixture.setColor("white")
        self.stop()

class ColorScene(Scene):
    def __init__(self, univers_dmx:Univers_DMX, color):
        super().__init__(univers_dmx)
        self.id = 3
        self.color = color

    def activate(self):
        for fixture in self.univers_dmx.getAllFixtures():
            if isinstance(fixture, DMXLightFixtures):
                fixture.enableLight(True)
                fixture.setColor(self.color)
        self.stop()

class BasicDisco(Scene):
    def __init__(self, univers_dmx:Univers_DMX):
        super().__init__(univers_dmx)
        self.id = 3
        self.loopTime = 4

    def activate(self):

        while self.running:

            color = Util.utils.random_color()
            ml = self.univers_dmx.getMyLight()
            ml.setPartyLight(255)
            ml.setPartyLightRotationSpeed(60)
            ml.enableLight(True)

            all_lyres = self.univers_dmx.getAllLyre()
            all_lyres.setColor(color)
            all_lyres.enableLight(True)
            all_lyres.centerCircle(40, 30, 2, 2)

            # --- Effet stroboscope aléatoire pendant 4 secondes ---
            strobe_start = time.time()
            while time.time() - strobe_start < 4:
                if random.random() < 0.3:  # 30% de chance de strobe
                    speed = random.randint(50, 200)
                    all_lyres.setStroboscopeSpeed(speed)
                else:
                    all_lyres.setStroboscopeSpeed(0)

                time.sleep(0.5)  # met à jour toutes les 200 ms

            # On s'assure que le strobe est coupé après les 4 sec
            all_lyres.setStroboscopeSpeed(0)


class LittleDancing(Scene):
    def __init__(self, univers_dmx: Univers_DMX):
        super().__init__(univers_dmx)
        self.id = 4

    def activate(self):
        while self.running:
            color = Util.utils.random_color()
            ml = self.univers_dmx.getMyLight()
            ml.setRotation1Light(255)
            ml.setRotationSpeed(60)
            ml.enableLight(True)
            self.univers_dmx.getAllLyre().setColor(color)
            self.univers_dmx.getAllLyre().enableLight(True)
            self.univers_dmx.getAllLyre().centerCircle(40, 30, 3, 2)
            time.sleep()
            time.sleep(6)

class ExtremStrope(Scene):
    def __init__(self, univers_dmx: Univers_DMX, color:str):
        super().__init__(univers_dmx)
        self.id = 5
        self.color = color

    def activate(self):
        while self.running:
            ml = self.univers_dmx.getMyLight()
            ml.setColor(self.color)
            ml.enableLight(True)
            self.univers_dmx.getAllLyre().setColor(self.color)
            self.univers_dmx.getAllLyre().enableLight(True)
            self.univers_dmx.getAllLyre().ellipse(cfg.centerPan, 100, 10, 90, 2)
            self.univers_dmx.strobAllLight(150)
            time.sleep(2)


class WarmScene(Scene):
    def __init__(self, univers_dmx: Univers_DMX, intensity: int):
        super().__init__(univers_dmx)
        self.intensity = intensity
        self.id = 1  # unique ID de la scène

    def activate(self):
        rightFixtures = self.univers_dmx.getRightFixtures()
        topFixtures = self.univers_dmx.getTopFixtures()
        otherFixtures = self.univers_dmx.getOtherFixtures()

        # Groupe de couleurs chaudes
        warm_colors = ["orange", "red", "yellow"]

        # Paramètres d'intensité
        color = warm_colors[min(self.intensity - 1, len(warm_colors) - 1)]
        strobe_speed = 0
        movement_loops = 1
        duration = 3.0

        if self.intensity == 1:
            strobe_speed = 0
            duration = 5.0
        elif self.intensity == 2:
            strobe_speed = 50
            duration = 4.0
        elif self.intensity == 3:
            strobe_speed = 100
            duration = 3.0
        elif self.intensity == 4:
            strobe_speed = 150
            duration = 2.5
        elif self.intensity == 5:
            strobe_speed = 200
            duration = 2.0

        while self.running:
            color = warm_colors[min(self.intensity - 1, len(warm_colors) - 1)]

        # Appliquer la scène
        for fixture in rightFixtures + topFixtures + otherFixtures:
            fixture.enableLight(True)
            try:
                fixture.setColor(color)
                fixture.setStroboscopeSpeed(strobe_speed)
                if isinstance(fixture, LyreSylvain):
                    fixture.centerEllipse(center_tilt=90, radius_pan=20, radius_tilt=10,
                                          duration=duration, loops=movement_loops)
            except Exception as e:
                print(f"Erreur sur fixture {fixture}: {e}")