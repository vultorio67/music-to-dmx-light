import math
import threading
import time

import cv2
import numpy as np
import pyautogui
import win32gui
import win32ui
import pygetwindow as gw
import win32con

import pytesseract
import winsound

# Nom de la fenêtre cible (doit être exactement le titre affiché)
window_title = "rekordbox"

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r'--oem 3 --psm 6'  # Mode de segmentation

# Trouver la fenêtre
windows = gw.getWindowsWithTitle(window_title)
if not windows:
    print("Fenêtre non trouvée !")
    exit()

window = windows[0]
hwnd = window._hWnd  # Handle de la fenêtre
print(windows)


# Fonction callback pour afficher la position de la souris

class SquareSelection():
    def __init__(self, x, y, width, heigth):
        self.x = x
        self.y = y
        self.width = width
        self.heigth = heigth


deck1Area = SquareSelection(810, 157, 300, 70)
deck2Area = SquareSelection(810, 230, 300, 70)

master1Detect = SquareSelection(900, 325, 50, 15)
master2Detect = SquareSelection(1850, 325, 50, 15)

timeLine1 = SquareSelection(10, 340, 950, 40)
timeLine2 = SquareSelection(970, 340, 950, 40)

partDetection1 = SquareSelection(10, 380, 950, 15)
partDetection2 = SquareSelection(970, 380, 950, 15)

useDeck = deck1Area

class Beat:
    def __init__(self, id, x):
        self.id = id
        self.x = x
        self.isPast = False

    def __str__(self):
        return f"id: {self.id}, x: {self.x}, isPast: {self.isPast}"


def capture_window(hwnd):
    """ Capture le contenu d'une fenêtre spécifique même si elle est en arrière-plan """

    # Récupérer la position et la taille de la fenêtre
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width, height = right - left, bottom - top

    # Récupérer le device context (DC) de la fenêtre
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Créer un bitmap compatible pour sauvegarder l'image
    saveBitmap = win32ui.CreateBitmap()
    saveBitmap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitmap)

    # Copier la fenêtre dans le bitmap
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Convertir en tableau NumPy
    bmpinfo = saveBitmap.GetInfo()
    bmpstr = saveBitmap.GetBitmapBits(True)
    img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))


    # Libérer les ressources
    win32gui.DeleteObject(saveBitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)


    #cv2.imshow("test", cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))

    # Convertir en BGR pour OpenCV
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

#permet de décopuper une partie souhaité
def crop_region(image, square:SquareSelection):
    """ Découpe une région spécifique de l'image """
    return image[square.y:square.y+square.heigth, square.x:square.x + square.width]

#permet de ne pas ajouter deux fois la mm bar
def ajouter_si_pas_trop_proche(liste, element, seuil):
    for e in liste:
        if abs(e - element) < seuil:
            return False  # L'élément est trop proche, on ne l'ajoute pas
    liste.append(element)  # Si aucune différence n'est trop petite, on ajoute l'élément
    return True

i = 0


detected_beats = []  # Liste des timestamps des beats détectés

def on_beat_detected():
    detected_beats.append(time.time())

def get_predicted_beat():
    if len(detected_beats) < 2:
        return None  # Pas assez d'info pour prédire
    intervals = np.diff(detected_beats[-5:])  # Derniers intervalles
    avg_interval = np.mean(intervals)
    next_beat = detected_beats[-1] + avg_interval
    return next_beat


beatList = []
mainBeatList = []

def beatDetection(hsv, image):
    # 🔍 Définir la couleur cible (gris)
    lower_bound = np.array([0, 0, 10])  # Min HSV
    upper_bound = np.array([0, 0, 200])  # Max HSV
    maskGrayBar = cv2.inRange(hsv, lower_bound, upper_bound)

    lower_bound = np.array([0, 0, 150])  # Min HSV
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

    basicBeat = []
    mainBeat = []

    # 🎯 Relier les contours qui sont proches et dessiner la ligne
    for i in range(len(valid_contours)):
        x1, y1, w1, h1 = valid_contours[i]
        for j in range(i + 1, len(valid_contours)):
            x2, y2, w2, h2 = valid_contours[j]
            if (abs(x1 - x2) < 10):
                ajouter_si_pas_trop_proche(basicBeat, (x1 + x2) / 2, 10)

    # 📏 Trouver les contours
    contours, _ = cv2.findContours(maskWhiteBar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_height = 2
    # Liste des contours valides
    valid_contours = []


    # 🎯 Définir une hauteur minimale pour filtrer
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        mainBeat.append(x)

    #print(valid_contours)


    basicBeat.sort()

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
                newBeat = Beat(beatList[-1].id+1, beat)
                print("création")
            except:
                newBeat = Beat(0, beat)
            beatList.append(newBeat)

    for beat in beatList:
        #print("beat", math.ceil(beat.x))
        cv2.putText(image, f"{beat.id} {beat.isPast}", (math.ceil(beat.x), 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1, )
        if beat.x < 150 and beat.isPast == False:
            beat.isPast = True
            winsound.Beep(700, 50)

    for beat in mainBeat:
        detected = False
        for i in mainBeatList:
            if abs(i.x - beat) < 60:
                i.x = beat
                detected = True

        if detected == False:
            try:
                newBeat = Beat(mainBeatList[-1].id+1, beat)
                print("création")
            except:
                newBeat = Beat(0, beat)
            mainBeatList.append(newBeat)

    for beat in mainBeatList:
        #print("beat", math.ceil(beat.x))
        cv2.putText(image, f"{beat.id} {beat.isPast}", (math.ceil(beat.x), 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1, )
        if beat.x < 150 and beat.isPast == False:
            beat.isPast = True
            winsound.Beep(1000, 50)


    if len(beatList) > 5:
        beatList.pop(0)  # On garde que les 5 derniers

    if len(mainBeatList) > 5:
        try:
            mainBeat.pop(0)  # On garde que les 5 derniers
        except:
            None


    for i in beatList:
        None
        #print(i)

    #mainBeat.sort()

    #print(mainBeat)

    # a changé mais permet de pas bip en permanence

    for i in basicBeat:
        cv2.line(image, (int(i), 0), (int(i), 100), (0, 255, 0), 2)
        if (-10 < i - 158 < 0):
            #winsound.Beep(700, 50)
            on_beat_detected()
        """predicted = get_predicted_beat()
        if predicted and time.time() > predicted + 0.05:  # marge d'erreur
            print("Beat manquant, insertion virtuelle à :", predicted)
            winsound.Beep(1500, 50)
            detected_beats.append(predicted)  # On ajoute un beat simulé"""

    for i in mainBeat:
        cv2.line(image, (int(i), 0), (int(i), 100), (255, 255, 0), 2)


    # text = pytesseract.image_to_string(gray, config=custom_config)

    # Afficher le texte détecté sur la vidéo
    # cv2.putText(image, text.strip(), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    # Affi
    # 🖥 Afficher en temps réel
    # image = detect_vertical_white_line(image, 30, 10)

    cv2.imshow("detect", image)


def detectMaster(rekordBoxImage):
    LOWER_ORANGE = np.array([5, 150, 150])  # Valeur minimale (en HSV)
    UPPER_ORANGE = np.array([15, 255, 255])  # Valeur maximale (en HSV)

    deck1Image = crop_region(rekordBoxImage, master1Detect)

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


pos = (0, 0)

def mouse_callback(event, x, y, flags, param):
    global pos
    if event == cv2.EVENT_MOUSEMOVE:
        pos = (x, y)
        print(x)

cv2.namedWindow("detect")
cv2.setMouseCallback("detect", mouse_callback)


while True:

    image = capture_window(hwnd)

    cv2.putText(image, f"({pos[0]}, {pos[1]})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2)

    #image2 = crop_region(image, deck1Area)

    #
    cv2.imshow("windows", image)

    image = crop_region(image, deck1Area)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


    beatDetection(hsv, image)

    #print(detectMaster(image))


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Quitter la boucle avec 'q'


# 🔚 Fermer les fenêtres
cv2.destroyAllWindows()





