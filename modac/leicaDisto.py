# MODAC leicaDisto D1 distance
# initial version uses separate gatttool in spawned pexpect process
# future versions might go direct to blueZ python 

import sys
this = sys.modules[__name__]
#import rest of modac
#from . import someModule
from .moKeys import *
from . import moData

# locally required for this module
import logging, logging.handlers
import sys
from time import sleep
import datetime
import json
#
import pexpect
import struct
import signal

# this is BLE MAC address, specific to unit. It needs to be in config file
__defaultAddrStr = "D3:9D:70:68:8B:F2"
__leicaAddressStr = None

# gatt is pexpect spawned process w comm pipe
__gatt= None
__distMeters = -1

def init(addrStr=this.__defaultAddrStr):
    logging.info("leicaDisto.init")
    this.__leicaAddressStr = addrStr
    assert not this.__leicaAddressStr == None

    # Run gatttool interactively.
    gatcmd = 'gatttool -b %s -t random -I' % this.__leicaAddressStr
    this.__distMeters = -1
    this.updateModata()
    try: 
        this.__gatt = pexpect.spawn(gatcmd)
        #print("gatt spawned")
        # Connect to the device.
        this.__gatt.sendline('connect')
        this.__gatt.expect('Connection successful', timeout=5)
        sleep(1)
        this.__gatt.sendline('char-write-cmd 0x000b 0200')
        this.__gatt.sendline('char-write-cmd 0x000f 0200')
        this.__gatt.sendline('char-write-cmd 0x0012 0200')

        logging.info("leicaDisto Connection Successful")
    except pexpect.TIMEOUT:
        logging.warn("leicaDisto.init() timeout "+ str(this.__gatt))
        this.__distMeters=-1
    except pexpect.EOF:
        logging.warn("leicaDisto.init EOF - process died " + str(this.__gatt))
        this.__distMeters = -1
        this.__gatt = None
    print("leicaDisto.init after Try: ")#, str(this.__gatt))
    sleep(3) # give it time to settle?
    this.update()

def update():
    # send command to Leica, parse results
    # error handling
    #print("disto.update() entered")
    if this.__gatt == None:
        # no process, update with -1 and return quietly
        this.__distMeters = -1
        moData.update(keyForLeicaDisto(), this.distance())
        return
    
    try:
        this.__gatt.sendline('char-write-cmd 0x0014 67')
        this.__gatt.expect('handle = 0x000e value: ', timeout=1)
        this.__gatt.expect('Indication')

        value = this.__gatt.before

        # (Ian) Convert to bytes from hex, struct bs?   This is some serious BS right here! 
        this.__distMeters = struct.unpack('<f', bytes.fromhex(''.join(value[:11].decode().split())) )[0]
    except pexpect.TIMEOUT:
        logging.warn("leicaDisto.update() timeout "+ str(this.__gatt))
        this.__distMeters=-1
    except pexpect.EOF:
        logging.warn("leicaDisto.update() EOF - process died " + str(this.__gatt))
        this.__distMeters = -1
        this.gatt = None
    this.updateModata()
    #moData.update(keyForLeicaDisto(), this.distance())
    print("LeicaDisto.update = ", this.distance())
    
def updateModata():
    d = {keyForTimeStamp(): this.timestampStr(), keyForDistance(): this.distance()}
    print("update Leica Modata:", d)
    moData.update(keyForLeicaDisto(), d)
    
def timestampStr():
    this.timestamp = datetime.datetime.now()
    print("timestamp:", this.timestamp)
    return this.timestamp.strftime("%Y-%m-%d %H:%M:%S%Z")

def distance():
    if this.__distMeters < 0:
        logging.warn("LeicaDisto is negative")
    return this.__distMeters


if __name__ == "__main__":
    print("modac.leicaDisto has no self test")
    exit(0)
  

