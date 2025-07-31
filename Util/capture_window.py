import time

import cv2
import numpy as np
import win32con
import win32gui
import win32ui


def capture_window(hwnd, retry_interval=0.1, max_retries=None):

    try:
        # Récupérer la position et la taille de la fenêtre
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width, height = right - left, bottom - top
        if width == 0 or height == 0:
            raise ValueError("Fenêtre de taille nulle.")

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
        img = np.frombuffer(bmpstr, dtype=np.uint8)

        # Libérer les ressources
        win32gui.DeleteObject(saveBitmap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        if img.size == 0:
            raise ValueError("Image vide capturée.")

        # Conversion finale
        img = img.reshape((bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    except Exception as e:
        time.sleep(retry_interval)