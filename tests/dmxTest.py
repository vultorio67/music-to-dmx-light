import time

from MusicDmx.DmxController import DMXController

dmx = DMXController("COM3")
dmx.start()

# Test : on monte progressivement le canal 1

dmx.set_channel(8, 255)
dmx.set_channel(5, 45)
