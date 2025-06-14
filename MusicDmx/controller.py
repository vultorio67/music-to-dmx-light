#import queue
import threading
import time
from multiprocessing import Process, Queue
import multiprocessing

import cv2

from Util import Config
from .DmxController import DMXController
#from .RekordboxWindow import RekordboxWindow
from .RekordboxWindow import RekordbowWindow
from .BeatManager import BeatManager

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