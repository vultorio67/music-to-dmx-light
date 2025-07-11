#import queue
import threading
import time
from multiprocessing import Process, Queue
import multiprocessing
from typing import List

import cv2

from MusicDmx.DmxSignalGenerator import DMXSignalGenerator
from MusicDmx.ShowGenerator import ShowGenerator
from MusicDmx.RekordboxWindow import RekordbowWindow
from MusicDmx.Univers_DMX import Univers_DMX
from MusicDmx.fixtures.Scenes import SceneBank
from Util import Config


class MainController:
    def __init__(self):
        # Queues pour la communication entre threads
        self.window_queue = Queue(maxsize=1)

        self.config = Config()

        self.firstReferenceTime = time.time()

        self.rekordboxWindow = RekordbowWindow()

        self.dmxSignalGenerator = DMXSignalGenerator(self)

        self.univers_dmx = Univers_DMX(self)

        self.sceneBank = SceneBank(self)

        self.showGenerator = ShowGenerator(self)

    def getCurrentTime(self):
        return time.time() - self.firstReferenceTime


    def start(self):
        print("[MainController] Starting system...")

        # start sending dmx signal
        self.dmxSignalGenerator.start()

        #self start rekordbox analisis
        self.video_process = multiprocessing.Process(target=self.rekordboxWindow.run, args=(self.window_queue,self.firstReferenceTime,))
        self.video_process.start()

        # start show manager
        self.showGenerator.start()

        #no need to enable light
        self.univers_dmx.enableAllLight()

        #self.beat_process = multiprocessing.Process(target=self.beat_analyzer.run, args=(self.window_queue,))
        #self.beat_process.start()

        #self.rekordboxWindows.run()


        # Boucle principale (par exemple pour garder le programme en vie)
        try:
            while True:
                beatList = self.window_queue.get()
                self.showGenerator.update_beat(beatList)
        except KeyboardInterrupt:
            print("[MainController] Shutting down...")



