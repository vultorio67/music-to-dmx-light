import cv2
import numpy as np

# Charger l'image
image = cv2.imread('test4.png')

# Copier l'image pour affichage
output = image.copy()

# Convertir en niveaux de gris et binariser
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

# Trouver les contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Stockage des résultats
rectangles = []

color_database = [
    {"color": (0, 50, 200), "moment": "INTRO"},
    {"color": (125, 170, 0), "moment": "CHORUS 2"},
    {"color": (255, 50, 140), "moment": "UP"},
    {"color": (255, 50, 105), "moment": "UP 2"},
    {"color": (255, 50, 90), "moment": "UP 3"},
    {"color": (0, 170, 15), "moment": "CHORUS"},
    {"color": (45, 115, 155), "moment": "DOWN"},
    {"color": (211, 226, 234), "moment": "OUTRO 1"},
    {"color": (175, 135, 95), "moment": "OUTRO 2"},

    {"color": (70, 70, 225), "moment": "INTRO"},
    {"color": (255, 110, 80), "moment": "VERSE 1"},
    {"color": (255, 85, 80), "moment": "VERSE 2"},
    {"color": (125, 195, 120), "moment": "CHORUS"},
    {"color": (65, 215, 225), "moment": "BRIDGE"},
    {"color": (255, 80, 100), "moment": "VERSE 3"},
    {"color": (150, 130, 115), "moment": "OUTRO"},
]

print(type(color_database[0]['color']))


# Fonction pour calculer la distance entre deux couleurs
def color_distance(c1, c2):
    return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))
    return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))

# Fonction pour trouver le moment musical correspondant
def find_moment(color, tolerance=1):
    min_dist = float('inf')
    matched_moment = "UNKNOWN"
    for entry in color_database:
        dist = color_distance(color, entry["color"])
        if dist < min_dist and dist <= tolerance:
            min_dist = dist
            matched_moment = entry["moment"]
    return matched_moment

# Parcourir chaque contour détecté
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)

    print(x)

    # Extraire la couleur au centre du rectangle
    color = image[y + 1 , x + w // 2].tolist()  # Format BGR

    rectangles.append({
        'start_position_x': x,
        'color': color
    })

# Trier les rectangles de droite à gauche
rectangles = sorted(rectangles, key=lambda r: r['start_position_x'])

base_donnee_musique = []

for rect in sorted(rectangles, key=lambda x: x['start_position_x']):
    color = tuple(rect['color'])
    moment = find_moment(color, tolerance=30)
    base_donnee_musique.append({
        'start_position_x': rect['start_position_x'],
        'color': rect['color'],
        'moment': moment
    })

# Affichage de la base de donnée
for item in base_donnee_musique:
    print(item)

for rect in rectangles:
    x = rect['start_position_x']
    cv2.rectangle(output, (x, 0), (x + 5, image.shape[0]), rect['color'], 2)

cv2.imshow("Rectangles", output)
cv2.waitKey(0)
cv2.destroyAllWindows()