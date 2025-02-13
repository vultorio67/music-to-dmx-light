# Initialisation des variables
predicted_beats = [0, 1, 2, 3]  # Exemple de liste existante
lastBeat = 2
average_interval = 1.01  # Intervalle moyen
epsilon = 0.1  # Plage de tolérance

# Fonction pour vérifier si un élément existe déjà à 0.1 près
def is_already_in_list(value, epsilon, predicted_beats):
    return any(abs(value - beat) <= epsilon for beat in predicted_beats)

# Calcul de la prochaine valeur
new_beat = lastBeat + average_interval

# Si l'élément existe déjà à 0.1 près, ajouter une multiplication de l'intervalle
i = 1  # Compteur pour multiplier l'intervalle
while is_already_in_list(new_beat, epsilon, predicted_beats):
    new_beat = lastBeat + i * average_interval
    i += 1

# Ajouter la nouvelle valeur à la liste
predicted_beats.append(new_beat)

# Afficher le résultat
print(predicted_beats)
