import serial
import time

PORT = 'COM3'  # Ou COMx sous Windows
BAUD = 250000
CHANNELS = 512

# Initialisation du port
ser = serial.Serial(PORT, baudrate=BAUD, bytesize=8, parity='N', stopbits=2)

# Fonction d'envoi DMX
def send_dmx(data):
    # On tente un "break" logiciel en mettant la ligne basse
    ser.break_condition = True
    time.sleep(0.0001)  # 100 µs
    ser.break_condition = False
    time.sleep(0.00001)  # 10 µs

    # Trame DMX : start code (0x00) + data
    packet = bytes([0]) + bytes(data)
    ser.write(packet)

# Exemple : Canal 1 à fond, le reste à 0
dmx_data = [0] * CHANNELS
dmx_data[0] = \
    100

while True:
    send_dmx(dmx_data)
    time.sleep(0.025)  # 40 FPS max (25 ms)
