import threading
import time

from MusicDmx.BeatManager import BasicBeat, MainBeat, Beat
from MusicDmx.fixtures.DmxFixtures import DMXLightFixtures, CouleurDMX
import statistics



class ShowGenerator:

    def __init__(self, controller):
        self.mainController = controller
        self.univers_dmx = controller.univers_dmx
        self.bpm = -1
        self.beatList = []

    def start(self):
        x = threading.Thread(target=self.run, args=())
        x.start()

    def update_beat(self, beatList):
        self.beatList = beatList

    def run(self):

        time.sleep(3)

        while self.mainController.showGenerator.getLastMainBeatTime() == None:
            pass

        while abs(self.mainController.showGenerator.getLastMainBeatTime() - self.mainController.getCurrentTime()) < 0.05:
            time.sleep(0.01)
            print("starting the scene")

        a = self.mainController.sceneBank.basic_disco()
        time.sleep(2)
        a.stop()


        while True:
            currentTime = time.time() - self.mainController.firstReferenceTime
            self.bpm = self.estimate_median_and_fill()
            time.sleep(0.01)

    def getCurrentBeatStructureMoment(self):

        if len(self.beatList) == 0:
            return 0
        try:
            if isinstance(self.beatList[-1], MainBeat):
                return 1
            elif isinstance(self.beatList[-1], BasicBeat) and isinstance(self.beatList[-2], MainBeat):
                return 2
            elif isinstance(self.beatList[-1], BasicBeat) and isinstance(self.beatList[-2], BasicBeat) and isinstance(self.beatList[-3], MainBeat):
                return 3
            elif isinstance(self.beatList[-1], BasicBeat) and isinstance(self.beatList[-2], BasicBeat) and isinstance(self.beatList[-3], BasicBeat) and isinstance(self.beatList[-4], MainBeat):
                return 4

        except IndexError:
            return 0
            print("Not enough past beat")

    def getLastMainBeatTime(self):
        if self.getCurrentBeatStructureMoment() != 0:
            beat = self.beatList[-self.getCurrentBeatStructureMoment()]
            if isinstance(beat, MainBeat):
                return beat.detectedTime
            else:
                print("did not find the last main beat time")

    def getLastBeatTime(self):
        if self.getCurrentBeatStructureMoment() != 0:
            return self.beatList[-1].detectedTime

    def estimate_median_and_fill(self, max_gap_multiplier: float = 1.5) -> float:
        # Tri par temps*

        beats = self.beatList

        if len(beats) == 0:
            return 0

        beats = sorted(beats, key=lambda b: b.detectedTime)
        filled_beats = [beats[0]]

        # Calcul des intervalles
        intervals = [
            beats[i].detectedTime - beats[i - 1].detectedTime
            for i in range(1, len(beats))
        ]

        if not intervals:
            return beats, None

        # Estimation du BPM à partir de la médiane des intervalles
        median_interval = float(statistics.median(intervals))
        #estimated_bpm = 60 / median_interval
        #print(f"🎼 BPM estimé: {estimated_bpm:.2f} (intervalle médian: {median_interval:.3f}s)")

        # Complétion des beats manquants
        """for i in range(1, len(beats)):
            prev = beats[i - 1]
            curr = beats[i]
            delta = curr.detectedTime - prev.detectedTime

            if delta > median_interval * max_gap_multiplier:
                missing_count = round(delta / median_interval) - 1
                print(f"⚠️ Gap trop grand ({delta:.3f}s), insertion de {missing_count} beat(s)")

                for j in range(1, missing_count + 1):
                    fake_time = prev.detectedTime + j * median_interval
                    fake_beat = BasicBeat(id=-1, x=-1, isDetected=False)
                    fake_beat.detectedTime = fake_time
                    filled_beats.append(fake_beat)

            filled_beats.append(curr)"""

        # Tri final car on insère des beats entre deux existants
        filled_beats.sort(key=lambda b: b.detectedTime)
        return median_interval

