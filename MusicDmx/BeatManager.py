import time
from multiprocessing import Queue

import cv2
import winsound
import numpy as np

from MusicDmx.DmxController import DMXController


class BeatManager:

    def __init__(self, window_queue: Queue):
        self.window_queue = window_queue
        #self.beat_queue = beat_queue

    def ajouter_si_pas_trop_proche(self, liste, element, seuil):
        for e in liste:
            if abs(e - element) < seuil:
                return False  # L'élément est trop proche, on ne l'ajoute pas
        liste.append(element)  # Si aucune différence n'est trop petite, on ajoute l'élément
        return True

    def ajouter_si_pas_trop_proche(self, liste, element, seuil):
        for e in liste:
            if abs(e - element) < seuil:
                return False  # L'élément est trop proche, on ne l'ajoute pas
        liste.append(element)  # Si aucune différence n'est trop petite, on ajoute l'élément
        return True

    def run(self, queue : Queue):

        dmx = DMXController("COM3")
        dmx.start()

        # Test : on monte progressivement le canal 1

        dmx.set_channel(4, 255)
        dmx.set_channel(9, 255)


        while True:

            all = queue.get()
            basicBeat = all[0]
            mainBeat = all[1]

            #print(mainBeat)

            # a changé mais permet de pas bip en permanence
            if 150 in mainBeat:
                mainBeat.remove(150)


            for i in basicBeat:
                #cv2.line(image, (int(i), 0), (int(i), 100), (0, 255, 0), 2)
                if (-5 < i - 158 < 5):
                    winsound.Beep(700, 30)
                    dmx.set_channel(6, 255)
                    time.sleep(0.03)
                    dmx.set_channel(6, 0)
                    print("beat")

            for i in mainBeat:
                #cv2.line(image, (int(i), 0), (int(i), 100), (0, 255, 0), 2)
                if (-5 < i - 158 < 5):
                    winsound.Beep(1000, 30)
                    dmx.set_channel(6, 255)
                    time.sleep(0.03)
                    dmx.set_channel(6, 0)
                    print("main beat")



            #cv2.imshow("test", image)
