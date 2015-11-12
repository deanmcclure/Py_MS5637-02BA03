import smbus
import time
bus = smbus.SMBus(1)
address = 0x76

CMD_RESET = 0x1E
#oversample level 0-5
def CMD_START_D1(oversample_level):
    return (0x40 + 2*oversample_level)
def CMD_START_D2(oversample_level):
    return (0x50 + 2*oversample_level)
CMD_READ_ADC = 0x00

def write(value):
        bus.write_byte(address, value)
        return -1

def getADC():
    #return bus.read_byte_data(address, CMD_READ_ADC)
    ADC = bus.read_i2c_block_data(address, CMD_READ_ADC)
    return ((ADC[0] << 16) + (ADC[1] << 8) + ADC[2])

def getShort(data):
    return ((data[0] << 8) + data[1])

def getShort(data):
    return ((data[0] << 8) + data[1])


def getD1():
        print "requesting pressure"
        write(CMD_START_D1(5))
        time.sleep(.2)
        print "reading ADC"
        return getADC()

def getD2():
        print "requesting temperature"
        write(CMD_START_D2(5))
        time.sleep(.2)
        print "reading ADC"
        return getADC()

def getProm(i):
    return bus.read_i2c_block_data(address, i)

def getPressureTemp():
    D1 = getD1()
    D2 = getD2()
    dT = D2 - C5 * (2**8)
    TEMP = 2000.0+(dT*(C6/(2.0**23)))

    #Compensation
    OFF = C2 * (2**17) + (C4*dT) / (2.0**6)
    SENS = C1 * (2**16) + (C3*dT) / (2.0**7)

    #Second Order Compensation
    if TEMP >= 2000:
        T2 = 5 * (dT**2) / (2.0**38)
        OFF2 = 0
        SENS2 = 0
    else:
        T2 = 3 * (dT**2) / 2.0**33
        OFF2 = 61 * ((TEMP - 2000)**2) / (2.0**4)
        SENS2 = 29 * ((TEMP - 2000)*2) / (2.0**4)

    TEMP = TEMP - T2
    OFF = OFF - OFF2
    SENS = SENS - SENS2

    P = (D1 * SENS / (2.0**21) - OFF) / (2.0**15)
    return float(P)/100,float(TEMP)/100

print "initialising"
write(CMD_RESET)
C1 = getShort(getProm(0xA2))
C2 = getShort(getProm(0xA4))
C3 = getShort(getProm(0xA6))
C4 = getShort(getProm(0xA8))
C5 = getShort(getProm(0xAA))
C6 = getShort(getProm(0xAC))

while True:
    time.sleep(0.8)
    print "reading"
    print getPressureTemp()
