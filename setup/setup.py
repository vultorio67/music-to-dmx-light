import cv2
import yaml
from Util import capture_window# remplace ça par ton import réel
import win32gui

import pygetwindow as gw

selected_regions = {}
drawing = False
start_point = (0, 0)
current_rect = None

def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, current_rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_rect = (start_point[0], start_point[1], x - start_point[0], y - start_point[1])

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        x1, y1 = start_point
        x2, y2 = end_point
        rect_name = input("Nom de la zone ? (ex: deck1Area): ")
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        selected_regions[rect_name] = {'x': x, 'y': y, 'width': w, 'heigth': h}
        print(f"{rect_name} = SquareSelection({x}, {y}, {w}, {h})")
        current_rect = None


def select_regions_on_window(window_name='rekordbox'):
    windows = gw.getWindowsWithTitle(window_name)
    if not windows:
        print("Fenêtre non trouvée !")
        exit()

    window = windows[0]
    hwnd = window._hWnd  # Handle de la fenêtre

    image = capture_window(hwnd)

    clone = image.copy()

    cv2.namedWindow("Sélection des zones")
    cv2.setMouseCallback("Sélection des zones", mouse_callback)

    while True:
        display = clone.copy()
        if current_rect:
            x, y, w, h = current_rect
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Sélection des zones", image)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC pour quitter
            break

    cv2.destroyAllWindows()

    with open("zones.yaml", "w") as f:
        yaml.dump(selected_regions, f)

    print("Zones enregistrées dans zones.yaml")

select_regions_on_window()
