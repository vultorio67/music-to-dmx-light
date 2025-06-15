#import queue
import threading
import time
from multiprocessing import Process, Queue
import multiprocessing
from typing import List

import cv2

from Util import Config
from .DmxController import DMXController
#from .RekordboxWindow import RekordboxWindow
from .RekordboxWindow import RekordbowWindow
from .BeatManager import BeatManager
from .fixtures.DmxFixtures import *


class MainController:
    def __init__(self):
        # Queues pour la communication entre threads
        self.window_queue = Queue(maxsize=1)

        self.config = Config()

        # Initialisation des gestionnaires
        #self.rekordboxWindows = RekordboxWindow(self.window_queue)
        self.beat_analyzer = BeatManager(self.window_queue )
        self.rekordboxWindow = RekordbowWindow()
        #self.dmx_controller = DMXController(self.beat_queue)

        self.dmxController = DMXController(self.config.portDmx)

        self.univers_dmx = Univers_DMX(self.config, self.dmxController)


        # Threads
        self.threads = [
            #threading.Thread(target=self.rekordboxWindows.run),
            #threading.Thread(target=self.beat_analyzer.run, args=(self.window_queue,)),
        ]

    def start(self):
        print("[MainController] Starting system...")

        self.dmxController.start()

        for t in self.threads:
            t.start()

        """for i in self.univers_dmx.left_element:
            if isinstance(i, DMXLightFixtures):
                i.enableLight(True)
                i.setColor("red")
        """
        self.video_process = multiprocessing.Process(target=self.rekordboxWindow.run, args=(self.window_queue,))
        self.video_process.start()

        self.beat_process = multiprocessing.Process(target=self.beat_analyzer.run, args=(self.window_queue,))
        #self.beat_process.start()

        #self.rekordboxWindows.run()

        # Boucle principale (par exemple pour garder le programme en vie)
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("[MainController] Shutting down...")


#define all the elements of the univers
class Univers_DMX:
    def __init__(self, config:Config, dmxController: DMXController):
        self.right_element : List[DMXFixture] = []
        self.left_element : List[DMXFixture] = []
        self.top_element : List[DMXFixture] = []
        self.bottom_element : List[DMXFixture] = []
        self.other_element : List[DMXFixture] = []

        self.cfg = config
        self.dmxController = dmxController

        #init directly from config
        self.addFromConfig()

    def addRightElement(self, add):
        self.right_element.append(add)
    def addLeftElement(self, add):
        self.left_element.append(add)
    def addTopElement(self, add):
        self.top_element.append(add)
    def addBottomElement(self, add):
        self.bottom_element.append(add)
    def addOtherElement(self, add):
        self.other_element.append(add)

    def addFromConfig(self):
        for ft in self.cfg.get_fixtures("right"):
            self.addRightElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("left"):
            self.addLeftElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("top"):
            self.addTopElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("bottom"):
            self.addBottomElement(self.constructFixturesElement(ft))

        for ft in self.cfg.get_fixtures("other"):
            self.addOtherElement(self.constructFixturesElement(ft))


    #add here new element identification
    def constructFixturesElement(self, fixtures_config):

        fixture_type = fixtures_config.get('type')

        if fixture_type == "LyreSylvain":
            return LyreSylvain(fixtures_config['name'], fixtures_config['adresse'], self.dmxController)

        elif fixture_type == "MyLight":
            return MyLight(fixtures_config['name'], fixtures_config['adresse'], self.dmxController)

        else:
            raise ValueError(
                f"Type de fixture inconnu : {fixture_type} pour le projecteur '{fixtures_config.get('name', 'inconnu')}'")





