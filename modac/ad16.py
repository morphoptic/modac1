# modac.ad16 : 16 bit Analog-Digital Inputs
# built on ADS1115 adafruit library 16bit i2c A/D module
# initial version supports single ADS1115.
# future will need to configure multiple but still collect them all in one shot

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import sys
from time import sleep
import time

#from . import moduleName
from .moKeys import *
from . import moData
from .moStatus import *


#for AD1115 support
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

__isAlive = False
__status = moStatus.Default

# Create the I2C bus
__ad16_i2c = None
def get_i2c():
    return __ad16_i2c

# Create the ADC objects using the I2C bus and deviceAddresses
# for each device enter its address in this array
# default is one at 72
__ad16devAddr = [72]
__ad16dev = []

# Define channels of single-ended inputs
# each entry of array is a Dict that specifies
#  * the device index (used for the __ad16dev arrays),
#  * the channel on device,
#  * slot for the Analog() object

# chan Config is list of tuples, each giving idx of Device and ADS channel
__ad16chanConfig = [
    ( 0, ADS.P0),
    ( 0, ADS.P1),
    ( 0, ADS.P2),
    ( 0, ADS.P3)
]
__channels = []
__values = [0,0,0,0]
__numChannels = 4  # its 5 in PoC version, may be different, might be better to use len(ad16chanConfig)?

#each moAD16Device has 4 ADChannels defined in the chanConfig above
class moAD16Device:
    address = -1
    device = None
    def __init__(self, address= 72):
        self.address = address
        if self.device != None:
            log.error("moAD16device already initialized")
            return
        print("Init AD16Device at i2c address", address)
        
#        if this.get_i2c() is None:
#            logger.debug("AD16Device initializing busio I2C")
#            __ad16_i2c = busio.I2C(board.SCL, board.SDA)
        if this.get_i2c() is None:
            log.error("moAD16device error getting i2c bus")
            this.__status = moStatus.Error
            return
        # now add the Adafruit Object for device
        self.device = ADS.ADS1115(this.get_i2c(),address=self.address)

# a channel is one AD input, an ADS1115 has 4 channels
class AD16Channel:
    myDevice = None
    deviceChannel = -1
    analogIn = None
    
    def __init__(self, dev, devChan):
        assert not dev is None
        assert isinstance(dev, moAD16Device)
        #print("InitAD16Channel dev ", dev)
        #print("InitAD16Channel devChan ", devChan)
        self.myDevice = dev.device
        assert not self.myDevice is None
        self.deviceChannel = devChan
        self.analogIn = AnalogIn(ads=self.myDevice, positive_pin=self.deviceChannel)
                
        assert isinstance(self.analogIn,AnalogIn)

        #print("InitAD16Channel analogIn:", self.analogIn)
        #print("InitAD16Channel myDevice ", self.myDevice)
        #print("Initialized device chan: ", self.deviceChannel)
        #print("   gives value: ", self.value())

    def value(self):
        #print("enter ad16channel value()")
        assert isinstance(self.analogIn,AnalogIn)
        return self.analogIn.voltage    

def init():
    log.warning("initialize AD16 - 16bit A-D converter")
    # init the adafruit i2c bus
    this.__ad16_i2c = busio.I2C(board.SCL, board.SDA)
    if this.__ad16_i2c is None:
        log.error("error getting i2c bus for AD16")
        this.__status = moStatus.Error
        moData.update(keyForAD16(), this.__values)
        return
    # init each defined device
    print(" AD16 numDevices: ",len(this.__ad16devAddr))
    for idx in range(len(this.__ad16devAddr)):
        d = None
        try:
            d = moAD16Device(address=this.__ad16devAddr[idx])
        except:
            log.error(" Cant create device %d "%this.__ad16devAddr[idx]+str( sys.exc_info()[0]))
            this.__status = moStatus.Error

        this.__ad16dev.append(d)
        if d is None:
            log.error("No AD16 device found")
            this.__status = moStatus.Error

    if this.__status == moStatus.Error:
        log.error("some error initializing ad16")
        __isAlive = False
        if this.__status == moStatus.Error:
            this.__values = [0] * this.__numChannels
        #
        moData.update(keyForAD16(), this.__values)
        moData.update(keyForAD16Status(), this.__status.name)
        print("Bad Values "+str(this.__values))
        return

    print("Initialized AD16 devices: ", this.__ad16dev)
        
    # init each channel
    #loop thru config array (deviceIdx, chanId)
    for idx in range(len(this.__ad16chanConfig)):
        #print("create channel ",idx,this.__ad16chanConfig[idx])
        t = this.__ad16chanConfig[idx]
        deviceIdx = t[0]
        moDevice = this.__ad16dev[deviceIdx]
        #print("device= ",moDevice)
        chanId = t[1]
        if moDevice is None or moDevice.device is None:
            channel = None
        else:
            channel = AD16Channel(moDevice, chanId)
        this.__channels.append(channel)
        this.__values.append(0)
    this.__isAlive = True
    
    # now get initial values
    this.update()
    this.__status = moStatus.OK

    #print("ad16 Initialized")
    #print("__ad16devAddr ",__ad16dev)
    #print("__ad16chanConfig ",__ad16chanConfig)
    #print("__channels ",__channels)
    #print("__values ",__values)
     
def update():
    if this.__ad16_i2c is None:
        return
    if this.__isAlive == False:
        return
    moData.update(keyForAD16Status(), this.__status.name)

    #log.debug("ad16 update()")
    #print("ad16 has",len(__ad16chanConfig),"channels and ", len(this.__values),"values")
    #print (this.__values)
    # currently crude get all 8 with same default configutation
    try:
        for i in range(len(this.__channels)):
            channel = this.__channels[i]
            #print(i, "channel", channel)
            if channel != None:
                this.__values[i] = channel.value()
    except:
        log.error(" Error reading AD16 values, disable device")
        log.exception("Exception follows")
        # need to put at least one record in moData
        moData.update(keyForAD16(), this.__values)
        this.__ad16_i2c = None
        this.__isAlive = False
        this.__status = moStatus.Error

    # force error values
    if this.__status == moStatus.Error:
        this.__values = [0]* len(this.__values)
    #
    moData.update(keyForAD16(), this.__values)

def values():
    #print("ad16 has",len(__ad16chanConfig),"channels and ", len(this.__values),"values")
    #print (this.__values)
    return this.__values

def shutdown():
    #hmm release all the channels?
    this.__ad16dev = []
    this.__channels = []
    this.__values = []    

# these two checks have slightly different meanings.  Alive may be ok until an error occurs
def isError():
    if this.__status == moStatus.Error:
        return True
    return False

def isAlive():
    return this.__isAlive()
