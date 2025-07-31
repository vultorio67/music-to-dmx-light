import logging
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
        self.type = None

    """@abstractmethod
    def activate(self):
        pass"""

    def start(self, type):
        if self.running:
            return  # déjà en cours
        self.running = True
        self.type = type
        logging.info(f"[Scenes] Starting scene : {type.__name__}")
        self.univers_dmx.getAllLightFixtures().enableLight(True)
        threading.Thread(target=type).start()
        return self

    def stop(self, resetLight:bool=False):
        self.running = False
        threading.Thread(target=self.type).join()
        if resetLight:
            self.univers_dmx.turnOffAllLight()


class SceneBank(Scene):
    def __init__(self, controller):
        super().__init__(controller)
        self.ml = self.univers_dmx.getMyLight()

    #pour faire des testes de scènes
    def test(self):
        def run():

            while True:
                color = utils.random_color()

                self.univers_dmx.getAllLightFixtures().enableLight(True)
                self.univers_dmx.getAllLightFixtures().setColor(color)
                self.univers_dmx.getAllMovingHead().setPos(100, 100)

                sleepTime = calculateSleepTime(self.controller)
                #winsound.Beep(1000, 10)

                time.sleep(sleepTime)


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
                self.ml.setPartyLight(255)
                self.ml.setPartyLightRotationSpeed(60)
                self.ml.enableLight(True)

                lyres = self.univers_dmx.getAllMovingHead()
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
                self.ml.setRotation1Light(255)
                self.ml.setRotationSpeed(60)
                self.ml.enableLight(True)

                lyres = self.univers_dmx.getAllMovingHead()
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
                self.ml.setColor(color)
                self.ml.enableLight(True)

                lyres = self.univers_dmx.getAllMovingHead()
                lyres.setColor(color)
                lyres.enableLight(True)
                lyres.ellipse(cfg.centerPan, 70, rd, rd2, 2)
                self.univers_dmx.strobAllLight(170)
                time.sleep(2)
        self.start(run)




    ############ Up scene #############
    #                                 #
    ###################################

    def colorUp1(self, color):
        def run():
            self.univers_dmx.resetAllMasterSlave()
            self.univers_dmx.getAllLightFixtures().enableLight(True)
            self.univers_dmx.getRightMovingHead().addSlave(self.univers_dmx.getLeftMovingHead())
            self.univers_dmx.getRightLyreWash().addSlave(self.univers_dmx.getLeftLyreWash())


            while self.running:
                sleepTime = calculateSleepTime(self.controller)
                self.univers_dmx.getAllMovingHead().enableLight(True)
                self.univers_dmx.getAllMovingHead().setColor(color)

                self.univers_dmx.getRightMovingHead().move_to_arc(self.controller.config.centerPan - 10, 140, sleepTime * 2, 20)
                self.univers_dmx.getRightLyreWash().centerCircle(140, 15, sleepTime * 4)
                self.univers_dmx.getAllSpotLight().enableLight(True)
                self.univers_dmx.getAllSpotLight().fade_to_color(color, sleepTime * 2)
                time.sleep(sleepTime)

                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)

                sleepTime = calculateSleepTime(self.controller)
                self.univers_dmx.getAllMovingHead().turnOffAllLight()

                self.univers_dmx.getAllSpotLight().fade_to_color("black", sleepTime)


                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan - 10, 0, sleepTime)
                time.sleep(sleepTime)

                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)

        self.start(run)

    def colorUp2(self, color):
        def run():

            self.univers_dmx.resetAllMasterSlave()
            self.univers_dmx.getRightLyreWash().addSlave(self.univers_dmx.getLeftLyreWash())

            while self.running:

                sleepTime = calculateSleepTime(self.controller)
                self.univers_dmx.getAllMovingHead().enableLight(True)
                self.univers_dmx.getAllMovingHead().setGobo(utils.randomGobo())
                self.univers_dmx.getRightLyreWash().move_to(self.controller.config.centerPan -20, 80, sleepTime * 2)

                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan, 80, sleepTime * 2)
                self.univers_dmx.getLeftMovingHead().move_to(self.controller.config.centerPan, 0, sleepTime * 2)
                self.univers_dmx.getAllMovingHead().setColor(color)
                self.univers_dmx.getAllSpotLight().setColor(color)
                self.univers_dmx.getAllSpotLight().enableLight(True)
                time.sleep(sleepTime)

                sleepTime = calculateSleepTime(self.controller)
                self.univers_dmx.getAllSpotLight().enableLight(False)
                time.sleep(sleepTime)

                sleepTime = calculateSleepTime(self.controller)

                self.univers_dmx.getAllSpotLight().enableLight(True)
                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan, 0, sleepTime * 2)
                self.univers_dmx.getLeftMovingHead().move_to(self.controller.config.centerPan, 100, sleepTime * 2)
                self.univers_dmx.getRightLyreWash().move_to(self.controller.config.centerPan + 20, 80, sleepTime * 2)
                time.sleep(sleepTime)
                self.univers_dmx.getAllSpotLight().enableLight(False)

                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)

        self.start(run)

    def colorUp3(self, color):
        def run():
            self.univers_dmx.resetAllMasterSlave()
            self.univers_dmx.getRightMovingHead().addSlave(self.univers_dmx.getLeftMovingHead())
            while self.running:
                sleepTime = calculateSleepTime(self.controller)
                posRand = random.randint(40, 70)
                self.univers_dmx.getAllSpotLight().enableLight(True)
                self.univers_dmx.getAllSpotLight().fade_to_color(color, sleepTime)
                self.univers_dmx.getAllLyreWash().move_to(self.controller.config.centerPan, 100, sleepTime * 2)
                self.univers_dmx.getAllMovingHead().enableLight(True)
                self.univers_dmx.getAllMovingHead().setColor(color)
                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan + posRand, 0, sleepTime * 2)

                time.sleep(sleepTime)
                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)


                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan - posRand, 0, sleepTime * 2)
                self.univers_dmx.getAllLyreWash().move_to(self.controller.config.centerPan, 0, sleepTime * 2)


                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)
                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)

        self.start(run)

    def colorUp4(self, color):
        def run():

            self.univers_dmx.resetAllMasterSlave()

            while self.running:
                sleepTime = calculateSleepTime(self.controller)
                posRand = random.randint(40, 70)

                self.univers_dmx.getAllMovingHead().setColor(color)


                self.ml.enableLight(True)
                self.ml.setGreenLAZERLight(255)
                self.ml.setGreenLAZERLight(255)
                self.ml.setLAZERRotationSpeed(255)

                self.univers_dmx.getRightMovingHead().enableLight(True)
                self.univers_dmx.getLeftMovingHead().enableLight(False)
                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan, 100, sleepTime * 2)
                self.univers_dmx.getLeftMovingHead().move_to(self.controller.config.centerPan, 0, sleepTime)

                time.sleep(sleepTime)
                sleepTime = calculateSleepTime(self.controller)
                self.ml.enableLight(False)

                time.sleep(sleepTime)
                self.ml.enableLight(True)


                self.univers_dmx.getRightMovingHead().enableLight(False)
                self.univers_dmx.getLeftMovingHead().enableLight(True)
                self.univers_dmx.getRightMovingHead().move_to(self.controller.config.centerPan, 0, sleepTime)
                self.univers_dmx.getLeftMovingHead().move_to(self.controller.config.centerPan, 100, sleepTime * 2)

                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)
                self.ml.enableLight(False)

                sleepTime = calculateSleepTime(self.controller)
                time.sleep(sleepTime)

        self.start(run)

    def colorUp5(self, color1):
        def run():

            self.univers_dmx.resetAllMasterSlave()

            while self.running:
                sleepTime = calculateSleepTime(self.controller)

                lyres = self.univers_dmx.getAllMovingHead()
                color = utils.random_color()

                lyres.setColor(color1)
                lyres.enableLight(True)
                lyres.setGobo(utils.randomGobo())
                self.ml.enableLight(True)
                self.ml.setGreenLAZERLight(255)
                self.ml.setLAZERRotationSpeed(200)
                self.ml.fade7(1)
                self.univers_dmx.getRightMovingHead().centerCircle(40, 25, sleepTime * 8)
                color = utils.random_color()
                self.ml.setColor(color)
                time.sleep(sleepTime)
                sleepTime = calculateSleepTime(self.controller)

                for i in range(6):
                    color = utils.random_color()
                    self.ml.setColor(color)
                    time.sleep(sleepTime)
                    self.univers_dmx.getLeftMovingHead().centerCircle(40, 25, sleepTime * 8)





        self.start(run)
        return self









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