#!/usr/bin/env python3
# must use python 3 because of quick2wire interface
# isdale: i think this is from https://www.raspberrypi.org/forums/viewtopic.php?t=64503
# LTC2499 I2C address is 7'b1110101 = 0x76 when all address pins tied high
import sys
import time
from Q2W_i2c import *
import math

class LTC2499:

    # define variables
    __LTC2499_config = 0b10100000 # set ADC for external input, 60Hz reject
    __LTC2499_temperature = 0b11100000 # performs an internal temp reading, 60Hz reject
    # define channel list as all zeros then populate with numbers
    __LTC2499_channel = [0,0,0,0,0,0,0,0,0,0,0,0]
    __LTC2499_channel[0] = 0b10110000 # thermistor: single-ended, normal polarity
    __LTC2499_channel[1] = 0b10111000 # thermistor: single-ended, normal polarity
    __LTC2499_channel[2] = 0b10110001 # thermistor: single-ended, normal polarity
    __LTC2499_channel[3] = 0b10111001 # thermistor: single-ended, normal polarity
    __LTC2499_channel[4] = 0b10110010 # thermistor: single-ended, normal polarity
    __LTC2499_channel[5] = 0b10111010 # thermistor: single-ended, normal polarity
    __LTC2499_channel[6] = 0b10110011 # thermistor: single-ended, normal polarity
    __LTC2499_channel[7] = 0b10111011 # thermistor: single-ended, normal polarity
    __LTC2499_LightSensor = 0b10100100 # light sensor:differential, normal polarity
    __LTC2499_channel[10] = 0b10110101 # thermistor: single-ended, normal polarity
    __LTC2499_channel[11] = 0b10111101 # thermistor: single-ended, normal polarity
    # channels 12-15 not assigned yet

    #define offset_temp list with zeros then populate with numbers
    __LTC2499_offset_temp = [0,0,0,0,0,0,0,0,0,0,0,0]
    __LTC2499_offset_temp[0] = -0.4  # adjust thermistor offset error
    __LTC2499_offset_temp[1] = -0.346
    __LTC2499_offset_temp[2] = 0.1112-0.7
    __LTC2499_offset_temp[3] = -0.2
    __LTC2499_offset_temp[4] = 0.1754
    __LTC2499_offset_temp[5] = -0.217
    __LTC2499_offset_temp[6] = -0.37
    __LTC2499_offset_temp[7] = 0.02
    __LTC2499_offset_temp[10] = -0.36
    __LTC2499_offset_temp[11] = -0.083


  # Constructor
    def __init__(self, address=0x76,sample_count = 10, debug=False):
        self.address = address
        self.sample_count = sample_count
        self.debug = debug
        print("Init LTC2499 at adr ", self.address)


    def get_adc_conversion(self, channel, config):
        """
        This configures the LTC2499 for a conversion type on a channel. Then it will perform n
        conversions on that same channel. This is more efficient than performing a config and
        read for every conversion.
        """
        result_array = []
        time.sleep(0.15) # wait for previous conversion to end
        print("get_adc_conversion set channel")
        # set adc channel to convert
        Q2Wwrite8(self.address,channel,self.__LTC2499_config)
        print("loop n times reading")

        # convert n times on the channel
        for i in range(self.sample_count):
            time.sleep(0.15)    # allow time for the conversion (Fconv ~ 7.5Hz)
            # read result into most significant Byte ... least significant Byte
            msB2, msB1, msB0, lsB = Q2WreadListNoReg(self.address,4)
            # the result is in two's complement, strip off sign bit and ms_bit for conversion to integer
            # the sign_bit is used to check for ADC overrange - implement this later
            sign_bit = msB2
            sign_bit = sign_bit >>7 # extract the sign bit
            ms_bit = msB2
            ms_bit = (ms_bit >> 6) & 0x01 #mask off the ms bit
            msB2 =   0x3F & msB2 # remove sign bit and ms_bit from msB2

            # shift the bytes by appropriate power and add together to get result
            ms_bit = ms_bit << 24
            result = (msB2 << 24) + (msB1 << 16)+ (msB0 << 8) + lsB
            result = result >> 7 # Shift the noise bits out of the result
            # convert to integer from two's complement and check for adc overflow
            if (ms_bit > 0 and sign_bit > 0):
                # this is an ADC overflow condition
                result_array.append(16777216/2 +1)
            elif(ms_bit > 0 and sign_bit == 0):
                result_array.append(result - 16777216/2)
            elif(ms_bit == 0 and sign_bit == 0):
                # this is an ADC overflow condition
                result_array.append(-16777216/2 -1)
            else:
                result_array.append(result)



        return result_array

    def get_adc_voltage(self, channel):
        v = self.get_adc_conversion(channel, self.__LTC2499_config)
        v[:] = [float(3.3 * x/16777216.0) for x in v]
        return v

    def get_adc_temperature(self):
        """
        Perform a conversion on the internal temp sensor of the LTC2499 chip and return the
        temperature in degrees F.
        """
        t = ((self.get_adc_conversion(self.__LTC2499_temperature,self.__LTC2499_config)* 3.3/1570.0)-273.0)*9.0/5.0 + 32.0
        return t

    def convert2temp(self,v):
        """
        This conversion only works for the Vishay NTCLE203E3-100k thermistor.
        It uses the Steinhart-Hart equation and data published in the NTCLE203 datasheet.
        The thermistor is connected from the bottom of RS to GND. The top of RS is connected
        to the reference voltage Vref. The value of RS is chosen for an inflection point of 25C.
        """
        open_therm = 0
        AAA = 0.000821724 # first coefficient of S-H equation
        BBB = 0.000206985 # second coefficient
        CCC =  9.89368E-8 # third coefficient
        Rs =  75000.0 # value of resistor tied from thermistor to reference voltage
        R0 = 100000.0 # Thermistor value @ T = 25C
        Vref = 3.3  # voltage at top of resistor divider
        x = -(Rs*(R0*v + Rs*v + R0*Vref))/(R0*v + Rs*v - Rs*Vref)
        if (x < 0):
            # thermistor is probably open circuit
            x = 0
            temperatureF = 150.0
        else :
            temperatureC = -273 + 1/(AAA + BBB*math.log(x)  + CCC*math.log(x)**3)
            temperatureF = temperatureC * 9.0/5.0 + 32
        return temperatureF

    def meanstdv(self,x):
        """
        Calculate mean and standard deviation of data x[]:
        mean = {\sum_i x_i \over n}
        std = math.sqrt(\sum_i (x_i - mean)^2 \over n-1)
        """
        n, mean, std = len(x), 0, 0
        for a in x:
            mean = mean + a
        mean = mean / float(n)
        for a in x:
            std = std + (a - mean)**2
        if(n > 1):
            std = math.sqrt(std / float(n-1))
        else:
            std = 0.0
        return mean, std

    def measure_temperature(self,channel):
        x = self.get_adc_voltage(self.__LTC2499_channel[channel])
        x[:] = [self.convert2temp(v) for v in x]
        mean,std = self.meanstdv(x)
        mean += self.__LTC2499_offset_temp[channel]
        return mean


    def measure_lux(self):
        """Convert voltage across CDS light sensor to Lux. """
        Rtop = 10000
        Rbot = 1000
        Rs = float(Rtop+Rbot)
        Vref = 3.3
        v = self.get_adc_voltage(self.__LTC2499_LightSensor)
        vcds,std = self.meanstdv(v)
        if (vcds < 0):
            # something is wrong
            lux = -1
        else :
            rcds = vcds*Rs/(Vref - vcds)
            lux = 4370639.808904*rcds**(-1.305050099)
        return lux


# test code:
if __name__=="__main__":

    print("Initialize LTC2499")
    adc = LTC2499(0x76) #initialize
    print(" basic read channel 0")
    raw = adc.get_adc_conversion(0, 0b10100000)
    print("raw read: "+ raw)
    
    print(" now measure temps each channel")

    mean = adc.measure_temperature(0)
    print("Channel 0 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(1)
    print("Channel 1 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(2)
    print("Channel 2 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(3)
    print("Channel 3 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(4)
    print("Channel 4 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(5)
    print("Channel 5 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(6)
    print("Channel 6 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(7)
    print("Channel 7 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(10)
    print("Channel 10 Temperature: {0:.3f} F".format(mean))
    mean = adc.measure_temperature(11)
    print("Channel 11 Temperature: {0:.3f} F".format(mean))

    lux = adc.measure_lux()
    print("Light Intensity: {0:.3f} lux".format(lux))
    
