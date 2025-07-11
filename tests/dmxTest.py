import time

from MusicDmx.DmxSignalGenerator import DMXSignalGenerator

dmx = DMXSignalGenerator("COM3")
dmx.start()

# Test : on monte progressivement le canal 1

dmx.set_channel(8, 255)
dmx.set_channel(5, 45)
