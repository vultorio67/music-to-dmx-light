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
window_title = "Rekordbox"

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Trouver la fenêtre
windows = gw.getWindowsWithTitle(window_title)
if not windows:
    print("Fenêtre non trouvée !")
    exit()

window = windows[0]
hwnd = window._hWnd  # Handle de la fenêtre

custom_config = r'--oem 3 --psm 6'  # Mode de segmentation

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

    # Convertir en BGR pour OpenCV
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def crop_region(image, x, y, width, height):
    """ Découpe une région spécifique de l'image """
    return image[y:y+height, x:x+width]

def ajouter_si_pas_trop_proche(liste, element, seuil):
    for e in liste:
        if abs(e - element) < seuil:
            return False  # L'élément est trop proche, on ne l'ajoute pas
    liste.append(element)  # Si aucune différence n'est trop petite, on ajoute l'élément
    return True

i = 0


def detect_vertical_white_line(image, min_height=50, max_gap=10):
    image = crop_region(image, 800, 157, 500, 70)

    # 🔍 Convertir en niveaux de gris et HSV
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 🎨 Définir les seuils pour le blanc
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 50, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # 📏 Trouver les contours
    contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_contours = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h >= min_height and w < 10:  # Filtrer les lignes verticales fines
            valid_contours.append((x, y, w, h))

    # 🔴 Vérifier la présence de rouge en haut et en bas
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 | mask_red2  # Union des deux masques

    for x, y, w, h in valid_contours:
        top_red = np.any(mask_red[y:y + 5, x:x + w])  # Vérifier le rouge en haut
        bottom_red = np.any(mask_red[y + h - 5:y + h, x:x + w])  # Vérifier le rouge en bas

        if top_red and bottom_red:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # ✅ Ligne validée

    return image

while True:

    image = capture_window(hwnd)

    image = crop_region(image, 800 , 157, 500, 70)


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # 🎨 Convertir en HSV pour détection de couleur
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 🔍 Définir la couleur cible (gris)
    lower_bound = np.array([0, 0, 10])  # Min HSV
    upper_bound = np.array([0, 0, 200])  # Max HSV
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    lower_bound = np.array([0, 0, 150])  # Min HSV
    upper_bound = np.array([0, 0, 255])  # Max HSV
    mask2 = cv2.inRange(hsv, lower_bound, upper_bound)

    # 📏 Trouver les contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_height = 2
    # Liste des contours valides
    valid_contours = []

    # 🎯 Définir une hauteur minimale pour filtrer
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h >= min_height:
            valid_contours.append((x, y, w, h))

    basicBeat = []

    # 🎯 Relier les contours qui sont proches et dessiner la ligne
    for i in range(len(valid_contours)):
        x1, y1, w1, h1 = valid_contours[i]
        for j in range(i + 1, len(valid_contours)):
            x2, y2, w2, h2 = valid_contours[j]
            if(abs(x1-x2)<10):
                ajouter_si_pas_trop_proche(basicBeat, (x1+x2)/2, 10)


    basicBeat.sort()

    #print(len(basicBeat))

    for i in basicBeat:
        cv2.line(image, (int(i), 0), (int(i), 100), (0, 255, 0), 2)
        if(abs(i-158)<5):
            winsound.Beep(1000, 50)


   # text = pytesseract.image_to_string(gray, config=custom_config)

    # Afficher le texte détecté sur la vidéo
   # cv2.putText(image, text.strip(), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

    # Affi
    # 🖥 Afficher en temps réel
    #image = detect_vertical_white_line(image, 30, 10)

    cv2.imshow("Détection en Temps Réel", mask2)

    # ⏹ Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 🔚 Fermer les fenêtres
cv2.destroyAllWindows()
