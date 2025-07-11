import threading
import time
from abc import ABC, abstractmethod
import random
from random import randint

import winsound

import Util.utils
from MusicDmx import MainController
from MusicDmx.fixtures.DmxFixtures import *
from Util import utils
from Util.utils import calculateSleepTime


#MainController is the main point

class Scene(ABC):
    def __init__(self, controller: MainController):
        self.controller = controller
        self.univers_dmx = controller.univers_dmx
        self.running = False
        self.id = -1
        self.loopTime = -1
        self.sleepTime = -1

    """@abstractmethod
    def activate(self):
        pass"""

    def start(self, type):
        if self.running:
            return  # déjà en cours
        self.running = True
        threading.Thread(target=type).start()

    def stop(self, resetLight:bool=False):
        self.running = False
        if resetLight:
            self.univers_dmx.turnOffAllLight()


class SceneBank(Scene):
    def __init__(self, controller):
        super().__init__(controller)

    #pour faire des testes de scènes
    def test(self):
        def run():

            ml = self.univers_dmx.getMyLight()

            while True:
                color = utils.random_color()

                sleepTime = calculateSleepTime(self.controller)
                #winsound.Beep(1000, 10)

                ml.enableLight(True)
                ml.setColor(color)
                time.sleep(sleepTime/4)
                #sleepTime = calculateSleepTime(self.controller)
                ml.enableLight(False)

                time.sleep(sleepTime/4)

                ml.enableLight(True)
                ml.setColor(color)
                time.sleep(sleepTime / 4)
                # sleepTime = calculateSleepTime(self.controller)
                ml.enableLight(False)

                time.sleep(sleepTime / 4)

        self.start(run)

    def beam_intro(self):
        def run():
            el = self.univers_dmx.right_element[0]
            if isinstance(el, LyreSylvain):
                el.enableLight(True)
                el.setPos(20, 30)
                el.setColor("pink")
            self.stop()
        self.start(run)

    #
    def black(self, home_position=False):
        def run():
            for fixture in self.univers_dmx.getAllFixtures():
                if isinstance(fixture, DMXLightFixtures):
                    fixture.turnOffAllLight()
                if isinstance(fixture, DMXMovingFixture) and home_position:
                    fixture.goToHomePosition()
            self.stop()
        self.start(run)

    def white(self):
        def run():
            for fixture in self.univers_dmx.getAllFixtures():
                if isinstance(fixture, DMXLightFixtures):
                    fixture.enableLight(True)
                    fixture.setColor("white")
            self.stop()
        self.start(run)


    def color(self, color):
        def run():
            for fixture in self.univers_dmx.getAllFixtures():
                if isinstance(fixture, DMXLightFixtures):
                    fixture.enableLight(True)
                    fixture.setColor(color)
            self.stop()
        self.start(run)

    def basic_disco(self):
        def run():
            while self.running:
                color = utils.random_color()
                ml = self.univers_dmx.getMyLight()
                ml.setPartyLight(255)
                ml.setPartyLightRotationSpeed(60)
                ml.enableLight(True)

                lyres = self.univers_dmx.getAllLyre()
                lyres.setColor(color)
                lyres.enableLight(True)
                lyres.centerCircle(40, 30, 2, 2)

                strobe_start = time.time()
                while time.time() - strobe_start < 4:
                    if random.random() < 0.3:
                        lyres.setStroboscopeSpeed(random.randint(50, 200))
                    else:
                        lyres.setStroboscopeSpeed(0)
                    time.sleep(0.5)
                lyres.setStroboscopeSpeed(0)
        self.start(run)

    def little_dancing(self):
        def run():
            while self.running:
                color = utils.random_color()
                ml = self.univers_dmx.getMyLight()
                ml.setRotation1Light(255)
                ml.setRotationSpeed(60)
                ml.enableLight(True)

                lyres = self.univers_dmx.getAllLyre()
                lyres.setColor(color)
                lyres.enableLight(True)
                lyres.centerCircle(40, 30, 3, 2)
                time.sleep(6)
        self.start(run)

    def extrem_strobe(self, color):
        def run():
            while self.running:
                rd = random.randint(1, 20)
                rd2 = random.randint(20, 70)
                ml = self.univers_dmx.getMyLight()
                ml.setColor(color)
                ml.enableLight(True)

                lyres = self.univers_dmx.getAllLyre()
                lyres.setColor(color)
                lyres.enableLight(True)
                lyres.ellipse(cfg.centerPan, 70, rd, rd2, 2)
                self.univers_dmx.strobAllLight(170)
                time.sleep(2)
        self.start(run)




############ Up scene #############
#                                 #
###################################




"""class WarmScene(Scene):
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
                print(f"Erreur sur fixture {fixture}: {e}")"""