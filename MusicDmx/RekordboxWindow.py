import math

import psutil
import winsound

from MusicDmx.BeatManager import MainBeat, BasicBeat
from Util import Config, capture_window
from Util import getColorDB

import pygetwindow as gw
import time
import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from multiprocessing import Queue


class SquareSelection():
    def __init__(self, x, y, width, heigth):
        self.x = x
        self.y = y
        self.width = width
        self.heigth = heigth


class RekordbowWindow:

    def __init__(self):
        config = Config()

        #window_queue = window_queue

        window_title = config.windowName

        self.windows = gw.getWindowsWithTitle(window_title)
        if not self.windows:
            print("No rekorkbox window found")
            print("Starting in no beat Beat mode")

        else:
            print(self.windows)

            #régler le beug du nombre
            try:
                window = self.windows[1]
            except:
                window = self.windows[0]
            self.hwnd = window._hWnd  # Handle de la fenêtre

            self.master = 1

            self.color_db = getColorDB()

            self.beat_bar_position = 163

            self.beatObjectList = []

            #à changer pour mettre dans config
            self.deck1Area = SquareSelection(810, 157, 300, 70)
            self.deck2Area = SquareSelection(810, 227, 300, 70)

            self.master1Detect = SquareSelection(900, 325, 50, 15)
            self.master2Detect = SquareSelection(1850, 325, 50, 15)

            self.timeLine1 = SquareSelection(10, 340, 950, 40)
            self.timeLine2 = SquareSelection(970, 340, 950, 40)

            self.partDetection1 = SquareSelection(10, 380, 950, 15)
            self.partDetection2 = SquareSelection(970, 380, 950, 15)


    def ajouter_si_pas_trop_proche(self, liste, element, seuil):
        for e in liste:
            if abs(e - element) < seuil:
                return False  # L'élément est trop proche, on ne l'ajoute pas
        liste.append(element)  # Si aucune différence n'est trop petite, on ajoute l'élément
        return True

    def crop_region(self, image, square: SquareSelection):
        return image[square.y:square.y + square.heigth, square.x:square.x + square.width]

    def get_croped_deck(self,deckArea):
        return self.crop_region(capture_window(self.hwnd), deckArea)

    def detectMaster(self, rekordBoxImage):
        LOWER_ORANGE = np.array([5, 158, 158])  # Valeur minimale (en HSV)
        UPPER_ORANGE = np.array([15, 255, 255])  # Valeur maximale (en HSV)

        deck1Image = self.crop_region(rekordBoxImage, self.master1Detect)

        # Convertir l'image en espace HSV
        hsv = cv2.cvtColor(deck1Image, cv2.COLOR_BGR2HSV)

        # Créer un masque pour la couleur orange
        mask = cv2.inRange(hsv, LOWER_ORANGE, UPPER_ORANGE)

        # Calculer la proportion de pixels orange
        orange_pixels = np.count_nonzero(mask)
        total_pixels = mask.size
        proportion = orange_pixels / total_pixels

        if proportion > 0.05:
            return 1
        else:
            return 2

    # Fonction pour calculer la distance entre deux couleurs
    def color_distance(self, c1, c2):
        return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))

    # Fonction pour trouver le moment musical correspondant
    def find_moment(self, color, tolerance=10):
        min_dist = float('inf')
        matched_moment = "UNKNOWN"
        for entry in self.color_db:
            dist = self.color_distance(color, entry["color"])
            if dist < min_dist and dist <= tolerance:
                min_dist = dist
                matched_moment = entry["moment"]
        return matched_moment

    def getDeckMusicStructure(self, deckNumber):
        if deckNumber == 1:
            partDetectionImage = self.get_croped_deck(self.partDetection1)
        else:
            partDetectionImage = self.get_croped_deck(self.partDetection2)

        # Convertir en niveaux de gris et binariser
        gray = cv2.cvtColor(partDetectionImage, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        moments = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Extraire la couleur au centre du rectangle
            color = partDetectionImage[y + 1, x + w // 2].tolist()  # Format BGR

            moment = self.find_moment(color, tolerance=10)

            moments.append({
                'start_position_x': x,
                'color': color,
                'moment': moment
            })

        # Trier les rectangles de droite à gauche
        moments = sorted(moments, key=lambda r: r['start_position_x'])

        return moments

    def beatAnalisys(self,  queue : Queue):
        hsv = cv2.cvtColor(self.deckImage, cv2.COLOR_BGR2HSV)

        lower_bound = np.array([0, 0, 10])  # Min HSV
        upper_bound = np.array([0, 0, 200])  # Max HSV
        maskGrayBar = cv2.inRange(hsv, lower_bound, upper_bound)

        lower_bound = np.array([0, 0, 158])  # Min HSV
        upper_bound = np.array([0, 0, 255])  # Max HSV
        maskWhiteBar = cv2.inRange(hsv, lower_bound, upper_bound)

        # 📏 Trouver les contours des basic beat
        contours, _ = cv2.findContours(maskGrayBar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_height = 4
        # Liste des contours valides
        valid_contours = []

        # 🎯 Définir une hauteur minimale pour filtrer
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h >= min_height:
                valid_contours.append((x, y, w, h))

        self.basicBeat = []
        self.mainBeat = []

        # 🎯 Relier les contours qui sont proches et dessiner la ligne
        for i in range(len(valid_contours)):
            x1, y1, w1, h1 = valid_contours[i]
            for j in range(i + 1, len(valid_contours)):
                x2, y2, w2, h2 = valid_contours[j]
                if (abs(x1 - x2) < 10):
                    self.ajouter_si_pas_trop_proche(self.basicBeat, (x1 + x2) / 2, 10)

        # 📏 Trouver les contours
        contours, _ = cv2.findContours(maskWhiteBar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_height = 2
        # Liste des contours valides
        valid_contours = []

        # 🎯 Définir une hauteur minimale pour filtrer
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            self.mainBeat.append(x)

        self.basicBeat.sort()
        self.mainBeat.sort()

        if self.beat_bar_position in self.mainBeat:
            self.mainBeat.remove(self.beat_bar_position)


        for beat in self.basicBeat:
            detected = False
            for i in self.beatList:
                #distante minimal entre deux beat
                if abs(i.x - beat) < 40 :
                    i.x = beat
                    detected = True

            if detected == False and beat > (self.beat_bar_position-20):
                try:
                    newBeat = BasicBeat(self.beatList[-1].id + 1, beat)
                except:
                    newBeat = BasicBeat(0, beat)
                self.beatList.append(newBeat)

        for beat in self.beatList:
            # print("beat", math.ceil(beat.x))
            if not beat.isDetected:
                cv2.putText(self.deckImage, f"{beat.id} {beat.isDetected}", (math.ceil(beat.x), 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 1, )
            if beat.x < self.beat_bar_position and beat.isDetected == False:
                beat.isDetected = True
                #winsound.Beep(700, 3)
                beat.detectedTime = time.time() - self.firstReferenceTime
                self.beatObjectList.append(beat)

                if len(self.beatObjectList) > 15:
                    self.beatObjectList.pop(0)

                queue.put(self.beatObjectList)

        for beat in self.mainBeat:
            detected = False
            for i in self.mainBeatList:
                if abs(i.x - beat) < 80:
                    i.x = beat
                    detected = True

            if detected == False and beat > (self.beat_bar_position-20):
                try:
                    newBeat = MainBeat(self.mainBeatList[-1].id + 1, beat)
                except:
                    newBeat = MainBeat(0, beat)
                self.mainBeatList.append(newBeat)

        for beat in self.mainBeatList:
            # print("beat", math.ceil(beat.x))
            if not beat.isDetected:
                cv2.putText(self.deckImage, f"{beat.id} {beat.isDetected}", (math.ceil(beat.x), 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 100, 255), 1, )
            if beat.x < self.beat_bar_position and beat.isDetected == False:
                beat.isDetected = True
                #winsound.Beep(1000, 3)
                beat.detectedTime = time.time() - self.firstReferenceTime
                self.beatObjectList.append(beat)

                if len(self.beatObjectList) > 10:
                    self.beatObjectList.pop(0)

                queue.put(self.beatObjectList)
        if len(self.beatList) > 5:
            self.beatList.pop(0)  # On garde que les 5 derniers

        if len(self.mainBeatList) > 5:
            try:
                self.mainBeat.pop(0)  # On garde que les 5 derniers
            except:
                None



    def getTimeLineActivePosition(self):
        hsv = cv2.cvtColor(self.deckTimeLineImage, cv2.COLOR_BGR2HSV)

        lower_bound = np.array([0, 0, 158])  # Min HSV
        upper_bound = np.array([0, 0, 255])  # Max HSV
        maskWhiteBar = cv2.inRange(hsv, lower_bound, upper_bound)


        # 📏 Trouver les contours
        contours, _ = cv2.findContours(maskWhiteBar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_height = 2
        # Liste des contours valides
        valid_contours = []

        # 🎯 Définir une hauteur minimale pour filtrer
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h > 2:
                self.xpos = x
                cv2.line(self.deckTimeLineImage, (int(x), 0), (int(x), 30), (255, 0, 255), 2)
                return x

    def getCurrentActiveMoment(self):
        self.masterMusicStructure = self.getDeckMusicStructure(self.master)
        try:
            pos = self.getTimeLineActivePosition()
            i=-1
            structure = self.getDeckMusicStructure(self.master)
            for moment in structure:
                if moment['start_position_x'] > pos:
                    return [structure[i]['moment'], i]
                i=i+1
        except:
            print("not detect")




    def run(self, queue : Queue, firstReferenceTime):
        if self.windows:
            try:
                print("Process démarré")
                self.beatList = []
                self.mainBeatList = []

                last_action_time = time.time()

                current_master = self.master

                self.firstReferenceTime = firstReferenceTime

                p = psutil.Process()
                p.nice(psutil.HIGH_PRIORITY_CLASS)

                while True:
                    # print(get_croped_deck(deck1Area))
                    # window_queue.put(get_croped_deck(deck1Area))

                    # permet de détecter quell est le master avec un pas de tp

                    current_time = time.time()
                    if current_time - last_action_time >= 0.2:
                        self.master = self.detectMaster(capture_window(self.hwnd))
                        # print(self.getCurrentActiveMoment())
                        last_action_time = current_time

                    if current_master != self.master:
                        print("master change, refresh the music structure")
                        self.masterMusicStructure = self.getDeckMusicStructure(self.master)
                        current_master = self.master

                    if (self.master == 1):
                        self.deckImage = self.get_croped_deck(self.deck1Area)
                        self.deckTimeLineImage = self.get_croped_deck(self.timeLine1)
                        self.partDetectionImage = self.get_croped_deck(self.partDetection1)
                    else:
                        self.deckImage = self.get_croped_deck(self.deck2Area)
                        self.deckTimeLineImage = self.get_croped_deck(self.timeLine2)
                        self.partDetectionImage = self.get_croped_deck(self.partDetection2)

                    # print(valid_contours)

                    self.beatAnalisys(queue)

                    all = [self.basicBeat, self.mainBeat]
                    # queue.put(all)

                    if 158 in self.mainBeat:
                        self.mainBeat.remove(158)

                    if 159 in self.mainBeat:
                        self.mainBeat.remove(159)

                    # print("main",self.mainBeat)

                    for i in self.basicBeat:
                        cv2.line(self.deckImage, (int(i), 0), (int(i), 100), (0, 255, 0), 1)

                    for i in self.mainBeat:
                        cv2.line(self.deckImage, (int(i), 0), (int(i), 100), (255, 0, 255), 1)

                    cv2.line(self.deckImage, (self.beat_bar_position, 0), (self.beat_bar_position, 100), (255, 255, 255), 2)

                    cv2.imshow("test", self.deckImage)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                # Ton code ici...
            except Exception as e:
                import traceback
                print("Exception dans le processus :")
                traceback.print_exc()



