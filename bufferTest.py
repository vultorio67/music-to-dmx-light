import io

import pyaudio
import numpy as np
import librosa
import threading
import time
from collections import deque
import soundfile as sf
import winsound

# Paramètres audio
RATE = 44100  # Fréquence d'échantillonnage
CHUNK = 1024  # Taille d'un buffer de capture
CHANNELS = 1  # Nombre de canaux (mono)
FORMAT = pyaudio.paInt16  # Format audio
maxDurationBuffer = 5  # Durée du buffer circulaire en secondes
sr = 22050

# Calcul de la taille du buffer circulaire
BUFFER_SIZE = int(RATE * maxDurationBuffer / CHUNK)
audio_buffer = deque(maxlen=BUFFER_SIZE)
start_time = time.time()

beat_times = []
beat_times_global = []
predicted_beats = [0]

minimumAudioTimeBuffer = 4

# Initialisation de PyAudio
p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)


def capture_audio():
    global start_time
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        np_data = np.frombuffer(data, dtype=np.int16)
        audio_buffer.append(np_data)


def on_beat_predicted(beat_number):
    print(f"Beat numéro {beat_number} atteint!")

# Calcul de l'intervalle moyen entre les beats
def calculate_average_interval():
    # Calcul des intervalles entre les battements
    intervals = [beat_times_global[i] - beat_times_global[i - 1] for i in range(1, len(beat_times_global))]

    # Filtrer les intervalles entre 0.5 et 1
    valid_intervals = [interval for interval in intervals if 0.1 <= interval <= 0.8]

    # Retourner la moyenne des intervalles valides, ou 0 si aucun intervalle valide n'existe
    return sum(valid_intervals) / len(valid_intervals) if valid_intervals else 0


# Prédire les prochains beats
def predict_next_beats():
    average_interval = calculate_average_interval()

    currentTime = time.time() - start_time

    epsilon = 0.2

    while predicted_beats[-1] < currentTime+5:
        currentTime = time.time() - start_time
        lastBeat = beat_times_global[-1]

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


    """if len(beat_times_global) >= 2:
        while len(predicted_beats) <= 6:
            if len(predicted_beats) > 0:
                last_moment = beat_times_global[-1]
            else:
                last_moment = 0
            for i in range(len(predicted_beats)+1, 7+1):
                predicted_beats.append(last_moment + i * average_interval)"""

def predictBeat():
    global predicted_beats

    timeprint = 0

    while True:
        currentTime = time.time() - start_time

        if len(beat_times_global) > 0:
            predict_next_beats()

        predicted_beats = [valeur for valeur in predicted_beats if valeur >= currentTime-5 or valeur == 0]

        i = 0
        """for beat in predicted_beats:
            if beat < currentTime-0.5:
                del predicted_beats[i]
            i=i+1"""

        for element in predicted_beats:
            if abs(currentTime - element) <= 0.01:
                winsound.Beep(1000, 200)
                time.sleep(0.05)
                #predicted_beats = [valeur for valeur in predicted_beats if valeur >= currentTime]

        if currentTime - timeprint > 1:
            print("les beat prédit sont: ", predicted_beats, "et le temps vaut: ",currentTime)
            timeprint = currentTime

        previousPredicted = predicted_beats

        time.sleep(0.001)



def process_audio():
    global beat_times_global

    while True:

        timeDataStockBuffer = len(audio_buffer) * CHUNK / RATE

        print("le nombre de secondes stoquées dans le buffer est : ", timeDataStockBuffer)

        if timeDataStockBuffer >= minimumAudioTimeBuffer:
            buffer_start_time = time.time() - start_time - len(audio_buffer) * CHUNK / RATE  # Adapter dtype selon format PyAudio


            print("buffer start at: ",buffer_start_time, "s")
            audio_bytes = b"".join(audio_buffer)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)  # Adapter dtype selon format PyAudio


            virtual_file = io.BytesIO()
            sf.write(virtual_file, audio_data, RATE, format="WAV")

            # ⚠️ Étape 4 : Revenir au début du buffer pour que librosa puisse lire
            virtual_file.seek(0)


            # ✅ Étape 5 : Charger avec librosa.load()
            y, sr = librosa.load(virtual_file, sr=None)

            # Separate harmonics and percussives into two waveforms
            y_harmonic, y_percussive = librosa.effects.hpss(y)

            # Beat track on the percussive signal
            tempo, beat_frames = librosa.beat.beat_track(y=y_percussive,
                                                         sr=sr, start_bpm=121)

            beat_times = librosa.frames_to_time(beat_frames, sr=sr) #+ buffer_start_time
            beat_times_global = beat_times+buffer_start_time

            #print(beat_times_global)

            bip_freq = 440  # Hz
            bip_duration = 0.05  # secondes
            t = np.linspace(0, bip_duration, int(sr * bip_duration), endpoint=False)
            bip = 0.3 * np.sin(2 * np.pi * bip_freq * t)  # Amplitude à 0.5 pour éviter la saturation

            # 🔹 Insérer les bips dans l’audio original
            y_with_bips = y.copy()
            for beat_time in beat_times:
                beat_sample = int(beat_time * sr)  # Convertir le temps en index d’échantillon

                # Ajouter le bip au bon endroit (éviter dépassement de tableau)
                if beat_sample + len(bip) < len(y_with_bips):
                    y_with_bips[beat_sample:beat_sample + len(bip)] += bip

            # 🔹 Normaliser pour éviter la saturation
            y_with_bips = np.clip(y_with_bips, -1.0, 1.0)
            # 🔹 Sauvegarder le fichier avec les bips
            sf.write("output_with_bips.wav", y_with_bips, sr)

            print("le tempo vaut :", tempo[0])
            print("les beat reel: ", beat_times_global)
            #print("les beats predit: ", predicted_beats)

        time.sleep(2)



# Création et démarrage des threads
capture_thread = threading.Thread(target=capture_audio, daemon=True)
process_thread = threading.Thread(target=process_audio, daemon=True)
predictThread = threading.Thread(target=predictBeat, daemon=True)
capture_thread.start()
process_thread.start()
predictThread.start()

print("Enregistrement en cours...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Arrêt de l'enregistrement")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()