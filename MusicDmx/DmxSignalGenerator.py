import asyncio
import logging

import serial
import threading
import time

from pyartnet import ArtNetNode

from Util import Config


class DMXSignalGenerator:
    def __init__(self, controller, baudrate=250000, channels=512, fps=30):

        self.mainController = controller
        self.config = Config()

        self.port = self.config.portDmx
        self.baudrate = baudrate
        self.channels = channels
        self.fps = fps
        self.interval = 1.0 / fps

        self.data = bytearray([0] * channels)
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        if checkSerial(self.port):
            # Port série
            self.serial = serial.Serial(
                self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=2
            )

    def set_channel(self, channel, value):
        """Change la valeur d'un canal (1-512)"""
        if not 1 <= channel <= self.channels:
            raise ValueError(f"Canal hors-limites : {channel}")
        if not 0 <= value <= 255:
            raise ValueError(f"Valeur invalide : {value}")
        with self.lock:
            self.data[channel - 1] = value

    def get_channel(self, channel):
        if not 1 <= channel <= self.channels:
            raise ValueError(f"Canal hors-limites : {channel}")
        with self.lock:
            return self.data[channel - 1]

    def _send_frame(self):
        """Envoie une trame DMX"""
        with self.lock:
            frame = bytes([0]) + bytes(self.data)


        # Break + MAB
        self.serial.break_condition = True
        time.sleep(0.0001)
        self.serial.break_condition = False
        time.sleep(0.00001)

        self.serial.write(frame)

    def _run(self):
        logging.info("[DMXSignalGenerator] Starting")
        while self.running:
            self._send_frame()
            time.sleep(self.interval)

    def start(self):
        """Démarre le thread DMX"""
        if not self.running: # and checkserial
            self.running = True
            self.thread = threading.Thread(target=self._run)
            #a definir plus tard car pour l'instant le programme s'arrète
            #self.thread.daemon = True
            self.thread.start()
        else:
            logging.error("[DMXSignalGenerator] Can't start dmx signal")

    def stop(self):
        """Arrête le thread DMX proprement"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.serial.close()
        logging.info("[DMXSignalGenerator] Stop sending DMX signal")


def checkSerial(port: str) -> bool:
    try:
        serial.Serial("COM3", 9600)
        return True
    except serial.serialutil.SerialException:
        return False


class ArtNetSignalGenerator:
    def __init__(self, controller, target_ip='192.168.1.255', universe_id=1, channels=512, fps=30, port=6454):
        self.mainController = controller
        self.target_ip = target_ip
        self.port = port
        self.universe_id = universe_id
        self.channels = channels
        self.fps = fps
        self.interval = 1.0 / fps

        self.data = [0] * channels
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        self.loop = asyncio.new_event_loop()
        self.node = ArtNetNode(self.target_ip, self.port, self.loop)
        self.universe = self.node.add_universe(self.universe_id)
        self.channel = self.universe.add_channel(start=1, width=self.channels)

    def set_channel(self, channel, value):
        """Met à jour un canal DMX (1..512)"""
        if not 1 <= channel <= self.channels:
            raise ValueError(f"Canal hors-limites : {channel}")
        if not 0 <= value <= 255:
            raise ValueError(f"Valeur invalide : {value}")
        with self.lock:
            self.data[channel - 1] = value

    def get_channel(self, channel):
        if not 1 <= channel <= self.channels:
            raise ValueError(f"Canal hors-limites : {channel}")
        with self.lock:
            return self.data[channel - 1]

    async def _update_loop(self):
        logging.info("[ArtNetSignalGenerator] Started")
        while self.running:
            with self.lock:
                values = self.data[:]
            await self.channel.set_values(values)
            await asyncio.sleep(self.interval)
        logging.info("[ArtNetSignalGenerator] Stopped")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_event_loop)
            self.thread.start()
        else:
            logging.warning("[ArtNetSignalGenerator] Already running")

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._update_loop())

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.loop.call_soon_threadsafe(self.loop.stop)
