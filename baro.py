import smbus
import time

CMD_RESET = 0x1E
#oversample level 0-5
def CMD_START_D1(oversample_level):
    return (0x40 + 2*oversample_level)
def CMD_START_D2(oversample_level):
    return (0x50 + 2*oversample_level)
CMD_READ_ADC = 0x00


class Barometer:
    def __init__(self,smbus,i2cAddress):
        self.bus = smbus
        self.add = i2cAddress
        self.initialise()

    @staticmethod
    def getShort(data):
        return ((data[0] << 8) + data[1])

    def initialise(self):
        #print "initialising"
        self.write(CMD_RESET)
        self.C1 = self.getShort(self.getProm(0xA2))
        self.C2 = self.getShort(self.getProm(0xA4))
        self.C3 = self.getShort(self.getProm(0xA6))
        self.C4 = self.getShort(self.getProm(0xA8))
        self.C5 = self.getShort(self.getProm(0xAA))
        self.C6 = self.getShort(self.getProm(0xAC))

    def write(self,value):
        self.bus.write_byte(self.add, value)
        return -1

    def getADC(self):
        #return bus.read_byte_data(self.add, CMD_READ_ADC)
        ADC = self.bus.read_i2c_block_data(self.add, CMD_READ_ADC)
        return ((ADC[0] << 16) + (ADC[1] << 8) + ADC[2])

    def getD1(self):
        #print "requesting pressure"
        self.write(CMD_START_D1(5))
        time.sleep(.2)
        #print "reading ADC"
        return self.getADC()

    def getD2(self):
        #print "requesting temperature"
        self.write(CMD_START_D2(5))
        time.sleep(.2)
        #print "reading ADC"
        return self.getADC()

    def getProm(self,i):
        return self.bus.read_i2c_block_data(self.add, i)

    def getPressureTemp(self):
        D1 = self.getD1()
        D2 = self.getD2()
        dT = D2 - self.C5 * (2**8)
        TEMP = 2000.0+(dT*(self.C6/(2.0**23)))

        #Compensation
        OFF = self.C2 * (2**17) + (self.C4*dT) / (2.0**6)
        SENS = self.C1 * (2**16) + (self.C3*dT) / (2.0**7)

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
