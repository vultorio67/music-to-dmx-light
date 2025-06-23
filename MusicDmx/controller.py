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
from .Univers_DMX import Univers_DMX
from .fixtures.DmxFixtures import *
from .fixtures.Scenes import *


class MainController:
    def __init__(self):
        # Queues pour la communication entre threads
        self.window_queue = Queue(maxsize=1)

        self.config = Config()

        self.rekordboxWindow = RekordbowWindow()

        self.dmxController = DMXController(self.config.portDmx)

        self.univers_dmx = Univers_DMX(self.config, self.dmxController)

    def start(self):
        print("[MainController] Starting system...")

        self.dmxController.start()

        self.video_process = multiprocessing.Process(target=self.rekordboxWindow.run, args=(self.window_queue,))
        self.video_process.start()

        #self.beat_process = multiprocessing.Process(target=self.beat_analyzer.run, args=(self.window_queue,))
        #self.beat_process.start()

        test = BeamIntro(self.univers_dmx)
        test.start()
        time.sleep(1)
        BlackScene(self.univers_dmx).start()
        time.sleep(2)
        ExtremStrope(self.univers_dmx, "green").start()
        #self.rekordboxWindows.run()

        # Boucle principale (par exemple pour garder le programme en vie)
        try:
            while True:
                time.sleep(1)
                pass
        except KeyboardInterrupt:
            print("[MainController] Shutting down...")



