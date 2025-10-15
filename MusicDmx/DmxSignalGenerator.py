import asyncio
import logging
import socket

import serial
import threading
import time

from pyartnet import ArtNetNode

from Util import Config


import logging
import threading
import time
import asyncio
import serial

from pyartnet import ArtNetNode
from Util import Config


class DMXSignalGenerator:
    def __init__(self, controller, mode="serial", fps=30, channels=512):
        """
        mode: 'serial' or 'artnet'
        fps: frames per second (for refresh loop)
        channels: number of DMX channels
        """
        self.mainController = controller
        self.config = Config()

        self.mode = mode
        self.channels = channels
        self.fps = fps
        self.interval = 1.0 / fps

        self.data = bytearray([0] * channels)
        self.lock = threading.Lock()

        # Control flags
        self.running = False
        self.thread = None

        if mode == "serial":
            self.port = self.config.portDmx
            self.baudrate = 250000
            if checkSerial(self.port):
                self.serial = serial.Serial(
                    self.port,
                    baudrate=self.baudrate,
                    bytesize=8,
                    parity="N",
                    stopbits=2,
                )
            else:
                logging.error("[DMXSignalGenerator] Serial port not available")

        elif mode == "artnet":
            self.target_ip = getattr(self.config, "artnet_ip", "127.0.0.1")
            self.universe_id = getattr(self.config, "artnet_universe", 0)
            self.loop = asyncio.new_event_loop()
            self.node = ArtNetNode(self.target_ip, 6454, refresh_universe=fps, loop=self.loop)
            self.universe = self.node.add_universe(self.universe_id)
            self.fixture = self.universe.add_fixture(1, channels)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    # --- public API ---------------------------------------------------------
    def set_channel(self, channel, value):
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

    def start(self):
        logging.info(f"[DMXSignalGenerator] Starting in {self.mode} mode ...")
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, name="DMXThread")
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

        if self.mode == "serial" and hasattr(self, "serial"):
            self.serial.close()

        elif self.mode == "artnet":
            # Stop asyncio loop
            self.loop.call_soon_threadsafe(self.loop.stop)

        logging.info("[DMXSignalGenerator] Stopped")

    # --- internals ----------------------------------------------------------
    def _send_frame_serial(self):
        frame = bytes([0]) + bytes(self.data)
        self.serial.break_condition = True
        time.sleep(0.0001)
        self.serial.break_condition = False
        time.sleep(0.00001)
        self.serial.write(frame)

    def _send_frame_artnet(self):
        # Push all channel values into pyartnet fixture
        self.fixture.set_values(list(self.data), fade_time=0)

    def _run(self):
        if self.mode == "artnet":
            asyncio.set_event_loop(self.loop)
            while self.running:
                self._send_frame_artnet()
                self.loop.run_until_complete(asyncio.sleep(self.interval))
        else:
            while self.running:
                self._send_frame_serial()
                time.sleep(self.interval)


def checkSerial(port: str) -> bool:
    try:
        s = serial.Serial(port, 9600, timeout=0.1)
        s.close()
        return True
    except serial.serialutil.SerialException:
        return False

