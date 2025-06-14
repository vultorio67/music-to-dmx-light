import time
from multiprocessing import Queue

import cv2
import winsound
import numpy as np

from MusicDmx.DmxController import DMXController

class Beat:
    def __init__(self, id, x):
        self.id = id
        self.x = x
        self.isPast = False

    def __str__(self):
        return f"id: {self.id}, x: {self.x}, isPast: {self.isPast}"


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

        all = queue.get()
        prec = all[0]
        #mainBeat = all[1]

        if 'already_triggered' not in globals():
            already_triggered = set()
        if 'last_time' not in globals():
            last_time = time.time()

        beatList = []
        mainBeatList = []

        while True:

            now = time.time()
            delta_time = now - last_time
            last_time = now

            all = queue.get()
            basicBeat = all[0]
            mainBeat = all[1]

            if 150 in mainBeat:
                mainBeat.remove(150)

            print(mainBeat)

            for beat in basicBeat:
                detected = False
                for i in beatList:
                    if abs(i.x - beat) < 40:
                        i.x = beat
                        detected = True

                if detected == False:
                    try:
                        newBeat = Beat(beatList[-1].id + 1, beat)
                        print("création")
                    except:
                        newBeat = Beat(0, beat)
                    beatList.append(newBeat)

            for beat in beatList:
                # print("beat", math.ceil(beat.x))
                if beat.x < 150 and beat.isPast == False:
                    beat.isPast = True
                    winsound.Beep(700, 10)

            for beat in mainBeat:
                detected = False
                for i in mainBeatList:
                    if abs(i.x - beat) < 60:
                        i.x = beat
                        detected = True

                if detected == False:
                    try:
                        newBeat = Beat(mainBeatList[-1].id + 1, beat)
                        print("création")
                    except:
                        newBeat = Beat(0, beat)
                    mainBeatList.append(newBeat)

            for beat in mainBeatList:
                # print("beat", math.ceil(beat.x))
                if beat.x < 150 and beat.isPast == False:
                    beat.isPast = True
                    winsound.Beep(1000, 10)
            if len(beatList) > 5:
                beatList.pop(0)  # On garde que les 5 derniers

            if len(mainBeatList) > 5:
                try:
                    mainBeat.pop(0)  # On garde que les 5 derniers
                except:
                    None

            #cv2.imshow("test", image)
