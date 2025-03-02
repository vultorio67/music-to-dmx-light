from Util import Config

import pygetwindow as gw
import time
import cv2
import numpy as np
import win32gui
import win32ui
import win32con

class RekordboxWindow:

    def __init__(self):
        self.config = Config()

        self.window_title = self.config.windowName

        self.windows = gw.getWindowsWithTitle(self.window_title)
        if not self.windows:
            print("Fenêtre non trouvée !")
            exit()

        self.window = self.windows[0]
        self.hwnd = self.window._hWnd  # Handle de la fenêtre

    def capture_window(self):
        """ Capture le contenu d'une fenêtre spécifique même si elle est en arrière-plan """

        # Récupérer la position et la taille de la fenêtre
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width, height = right - left, bottom - top

        # Récupérer le device context (DC) de la fenêtre
        hwndDC = win32gui.GetWindowDC(self.hwnd)
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
        win32gui.ReleaseDC(self.hwnd, hwndDC)

        # Convertir en BGR pour OpenCV
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)