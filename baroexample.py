import baro
import smbus

bus = smbus.SMBus(1)
address = 0x76

barom = baro.Barometer(bus,address)
while (1):
    print barom.getPressureTemp()
