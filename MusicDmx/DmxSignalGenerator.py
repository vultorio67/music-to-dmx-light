import serial
import threading
import time

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
        while self.running:
            self._send_frame()
            time.sleep(self.interval)

    def start(self):
        """Démarre le thread DMX"""
        if not self.running and checkSerial(self.port):
            self.running = True
            self.thread = threading.Thread(target=self._run)
            #a definir plus tard car pour l'instant le programme s'arrète
            #self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Arrête le thread DMX proprement"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.serial.close()


def checkSerial(port: str) -> bool:
    try:
        serial.Serial("COM3", 9600)
        return True
    except serial.serialutil.SerialException:
        return False
