import cv2

from Util import capture_window

import pygetwindow as gw

import pyautogui


window_title = "rekordbox"

# Trouver la fenêtre
windows = gw.getWindowsWithTitle(window_title)
if not windows:
    print("Fenêtre non trouvée !")
    exit()

window = windows[0]
hwnd = window._hWnd  # Handle de la fenêtre
print(windows)

while True:

    image = capture_window(hwnd)


    #image2 = crop_region(image, deck1Area)

    #
    cv2.imshow("windows", image)


    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


    #print(detectMaster(image))


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Quitter la boucle avec 'q'


# 🔚 Fermer les fenêtres
cv2.destroyAllWindows()