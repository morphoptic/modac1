#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import math
from waveshareADAC import ADS1256
import RPi.GPIO as GPIO

boardPot = 0 # board potentiometer is on AD0
boardPhotoR = 1 # board photo resistor is on AD1
myPot = 2 # test pot is on AD2
kTherm = 6 # k-type therm is on pin 7
iTherm = kTherm-4

#from LTC2499_HAT so its wrong but a start
def convert2temp(v):
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
    Vref = 5  # voltage at top of resistor divider
    #x = -(Rs*(R0*v + Rs*v + R0*Vref))/(R0*v + Rs*v - Rs*Vref)
    x=v
    print ("v ", v, " x", x)
    if (x < 0):
        # thermistor is probably open circuit
        x = 0
        temperatureC = -255
        temperatureF = 150.0
    else :
        temperatureC = -273 + 1/(AAA + BBB*math.log(x)  + CCC*math.log(x)**3)
        temperatureF = temperatureC * 9.0/5.0 + 32
    temps = [temperatureC, temperatureF]
    return temps

def readPPRT():
    ADC_Value = ADC.ADS1256_GetLower(0)
    print ("0 ADC wspot = ", ADC_Value[0]," = %lf"%(ADC_Value[0]*5.0/0x7fffff))
    print ("1 ADC Photo = %lf"%(ADC_Value[1]*5.0/0x7fffff))
    print ("2 ADC = %lf"%(ADC_Value[2]*5.0/0x7fffff))
    #print ("3 ADC = %lf"%(ADC_Value[3]*5.0/0x7fffff))
    ADC_Value = ADC.ADS1256_GetUpper(32)
    iTherm = kTherm-4
    print ("thermo = ", ADC_Value[iTherm]," = %lf"%(iTherm*5.0/0x7fffff))
    print ("thermo = %lf"%(ADC_Value[3]*5.0/0x7fffff))
    
def readThermo(gain=0):
    global ADC, kTherm,iTherm
    ADC.ADS1256_ConfigADC(gain)
    ADC.ADS1256_SyncWakeup()
    #time.sleep(0.125)
    ADC_Value = ADC.ADS1256_GetUpper(gain)
    #print("ADCUpper ", ADC_Value)
    thermoRaw = ADC_Value[iTherm] #ADC.ADS1256_GetChannalValue(kTherm)
    tV = (thermoRaw*5.0/0x7fffff)
    #print ("gain ",gain," t= ", thermoRaw," = %0.4f"%tV)
    temps = convert2temp(tV)
    print ("gain ",gain," t= ", thermoRaw," = %0.4f"%tV, " temps[c,f] ",temps)

def readThermGain():
    for i in range(0,32):
        gain = ADC.ADS1256_gainLookup(i)
        #print("i=",i," g=",gain)
        #gain = i
        readThermo(gain)
    
    
print("MODAC testing ADS1256 waveshare board")
try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    print("start loop")
    
    while(1):
        #print("forever")
        #readPPRT()
        #readThermGain()
        readThermo(1)
        time.sleep(1)

except :
    print("Exception")
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
