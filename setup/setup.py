import logging
import os
import cv2
import yaml
import pygetwindow as gw
from Util import capture_window

# don't know why, but need to import if don't won't error
import pyautogui

selected_regions = {}
drawing = False
start_point = None
zone_names = [
    "deck1Area",
    "deck2Area",
    "master1Detect",
    "master2Detect",
    "timeLine1",
    "timeLine2",
    "partDetection1",
    "partDetection2"
]
zone_index = 0  # pour suivre quelle zone est en cours
current_preview = None  # rectangle en cours de dessin
mouse_pos = (0, 0)  # position courante de la souris

zone_file_name = "zones.yaml"

window_name="rekordbox"


def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, zone_index, current_preview, mouse_pos

    mouse_pos = (x, y)  # track mouse always

    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing:  # premier clic
            drawing = True
            start_point = (x, y)
            current_preview = None
        else:  # deuxième clic = fin du rectangle
            drawing = False
            x1, y1 = start_point
            x2, y2 = x, y
            rect_name = zone_names[zone_index] if zone_index < len(zone_names) else f"zone{zone_index+1}"

            # coordonnées et dimensions
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)

            selected_regions[rect_name] = {"x": x, "y": y, "width": w, "height": h}
            logging.info(f"{rect_name} = SquareSelection({x}, {y}, {w}, {h})")

            zone_index += 1
            current_preview = None

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        # preview du rectangle en cours
        x1, y1 = start_point
        current_preview = (x1, y1, x, y)


def select_regions_on_window(window_name="rekordbox"):
    logging.info("Starting the zones selecting program")
    windows = gw.getWindowsWithTitle(window_name)
    if not windows:
        logging.ERROR("Rekordbox window not found")
        exit()

    window = windows[0]
    hwnd = window._hWnd  # handle de la fenêtre

    image = capture_window(hwnd)
    clone = image.copy()

    cv2.namedWindow("Please select regions")
    cv2.setMouseCallback("Please select regions", mouse_callback)

    while True:
        display = clone.copy()

        # rectangles déjà validés
        for name, rect in selected_regions.items():
            cv2.rectangle(display, (rect["x"], rect["y"]),
                          (rect["x"] + rect["width"], rect["y"] + rect["height"]),
                          (255, 255, 0), 1)
            cv2.putText(display, name, (rect["x"], rect["y"] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # rectangle en cours (preview)
        if current_preview:
            x1, y1, x2, y2 = current_preview
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 100), 1)

        # show next zone name near mouse
        if zone_index < len(zone_names):
            next_zone_name = zone_names[zone_index]
        else:
            next_zone_name = f"zone{zone_index+1}"

        mx, my = mouse_pos
        cv2.putText(display, f"Next: {next_zone_name}",
                    (mx + 10, my + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 200, 255), 2)

        cv2.imshow("Please select regions", display)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC pour quitter
            break
        elif len(selected_regions.items()) >= len(zone_names):  # toutes les zones créées
            with open(zone_file_name, "w") as f:
                yaml.dump(selected_regions, f)
            logging.info(f"Zone selection complete, and saved to {zone_file_name}")
            break

    cv2.destroyAllWindows()


def view_existing_zones(window_name="rekordbox"):
    logging.info("Viewing zones from file")
    if not os.path.exists(zone_file_name):
        logging.error("No zones.yaml file found!")
        return

    with open(zone_file_name, "r") as f:
        zones = yaml.safe_load(f)

    windows = gw.getWindowsWithTitle(window_name)
    if not windows:
        logging.ERROR("Rekordbox window not found")
        exit()

    window = windows[0]
    hwnd = window._hWnd

    image = capture_window(hwnd)
    clone = image.copy()

    cv2.namedWindow("Zones Preview")

    while True:
        display = clone.copy()

        # draw zones
        for name, rect in zones.items():
            cv2.rectangle(display, (rect["x"], rect["y"]),
                          (rect["x"] + rect["width"], rect["y"] + rect["height"]),
                          (0, 200, 255), 2)
            cv2.putText(display, name, (rect["x"], rect["y"] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Zones Preview", display)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC pour quitter
            break

    cv2.destroyAllWindows()


def setup():
    windows = gw.getWindowsWithTitle(window_name)
    if not windows:
        logging.error("Rekordbox window not found")
        exit()
    choice = input("Do you want to (d)efine new zones or (v)iew existing zones? [d/v]: ").strip().lower()

    if choice == "d":
        # delete old file if exists
        if os.path.exists(zone_file_name):
            os.remove(zone_file_name)
            logging.info("Deleted old zones.yaml")
        select_regions_on_window()
    elif choice == "v":
        view_existing_zones()
    else:
        print("Invalid choice. Exiting.")
