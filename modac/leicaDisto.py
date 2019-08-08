# MODAC leicaDisto D1 distance
# initial version uses separate gatttool in spawned pexpect process
# future versions might go direct to blueZ python 

import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData

# locally required for this module
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
__leicaTimeoutsThisSession = 0

def __startGattool():
    this.__timeoutCount = 0
    # Run gatttool interactively.
    gatcmd = 'gatttool -b %s -t random -I' % this.__leicaAddressStr
    try: 
        this.__gatt = pexpect.spawn(gatcmd)
        #print("gatt spawned")
        # Connect to the device.
        this.__gatt.sendline('connect')
        # if dont get response in short time, no Leica found
        this.__gatt.expect('Connection successful', timeout=5)
        sleep(1)
        # send some magic words to Leica
        # TODO: find out what these mean
        this.__gatt.sendline('char-write-cmd 0x000b 0200')
        this.__gatt.sendline('char-write-cmd 0x000f 0200')
        this.__gatt.sendline('char-write-cmd 0x0012 0200')

        log.info("leicaDisto Connection Successful")
    except pexpect.TIMEOUT:
        log.warn("leicaDisto.init() timeout "+ str(this.__gatt))
        print("Did Leica turn Off? need to turn leica back on")
        # TODO retry after N seconds
        this.__leicaTimeoutsThisSession += 1
        this.__distMeters=-1
        this.__gatt = None
    except pexpect.EOF:
        log.warn("leicaDisto.init EOF - process died " + str(this.__gatt))
        this.__distMeters = -1
        this.__gatt = None
    #print("leicaDisto.init after Try: "+ str(this.__gatt))
    if this.__gatt == None:
        print("Failed to start Gatttool")
    else:
        print("seems to have started, give it 3 sec")
        sleep(3) # give it time to settle?
    print("gattool init end")#, this.__gatt)

def init(addrStr=this.__defaultAddrStr):
    log.info("leicaDisto.init")
    this.__leicaAddressStr = addrStr
    assert not this.__leicaAddressStr == None

    this.__distMeters = -1
    this.updateModata()
    this.__timeoutCount = 0
    
    this.__startGattool()
    # if it started, update
    if not this.__gatt == None:
        this.update()

def update():
    # send command to Leica, parse results
    # error handling
    #print("disto.update() entered")
    if this.__gatt == None:
        log.debug("No gattTool for Leica")
        # no process, update with -1 and return quietly
        #this.__distMeters = -1
        #moData.update(keyForLeicaDisto(), this.distance())
        #dont update
        return
    noTimeout = True
    gotEOF = False
    #while noTimeout and not gotEOF:
    try:
        this.__gatt.sendline('char-write-cmd 0x0014 67')
        this.__gatt.expect('handle = 0x000e value: ', timeout=0.5)
        this.__gatt.expect('Indication')

        value = this.__gatt.before

        # (Ian) Convert to bytes from hex, struct bs?
        # This is some serious BS right here! 
        # Jerry: some very fancy data extraction from string to structure
        # gets first entry from unpacked struct created from bytes converted from hexStr
        # which starts in the bytes before received 'Indication'
        #    bytes.fromhex(''.join(value[:11].decode().split())) 
        #    value[:11] .decode()  .split()
        #''.join(value[:11].decode.split())
        this.__distMeters = struct.unpack('<f', bytes.fromhex(''.join(value[:11].decode().split())) )[0]
        this.updateModata()
        this.__timeoutCount = 0
    except pexpect.TIMEOUT:
        log.warn("leicaDisto.update() timeout ")#+ str(this.__gatt))
        #noTimeout = False
        this.__leicaTimeoutsThisSession += 1
        this.__timeoutCount +=1
        if this.__timeoutCount > 3:
            log.error("Leica timeout count exceeded, closing device")
            this.__timeoutCount = 0
            this.__gatt.close()
            this.__gatt = None
            sleep(0.5)
    except pexpect.EOF:
        log.error("leicaDisto.update() EOF - process died " + str(this.__gatt))
        # TODO: restart gatt Process... async
        this.__gatt = None
        gotEOF = true

    #if gotEOF or noTimeout == False:
    if this.__gatt == None:

        # try to re-init
        print ("GATTTool died, try restarting")
        this.__startGattool()
        if this.__gatt == None:
            loggin.error("Leica Restart Failed")
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
#    if this.__distMeters < 0:
#        log.warn("LeicaDisto is negative")
    return this.__distMeters

def shutdown():
    print ("Shutdown Leica Disto, total Timeouts:",this.__leicaTimeoutsThisSession)
    if not this.__gatt == None:
        this.__gatt.close()
def isRunning():
    if this.__gatt == None:
        return False
    return True

if __name__ == "__main__":
    print("modac.leicaDisto has no self test")
    exit(0)
  

