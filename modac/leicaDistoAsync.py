# MODAC leicaDisto D1 distance Ashync Trio version
# initial version uses separate gatttool in spawned pexpect process
# future versions might go direct to blueZ python
#
# ok so this version of async is a bit dirty but it works
# usual init() and update() are here but should NOT be used
# instead use a Trio nursery to spawn initAsync
# which will try to spawn the gattTool pexpect process

import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData

# locally required for this module
import sys
#from time import sleep
import datetime
import json
#
import pexpect
import struct
import signal
import trio

# this is BLE MAC address, specific to unit. It needs to be in config file
__defaultAddrStr = "D3:9D:70:68:8B:F2"
__leicaAddressStr = None

# gatt is pexpect spawned process w comm pipe
__gatt= None
__distMeters = -1
__leicaTimeoutsThisSession = 0
__leicaRestartsThisSession = 0
__gattSpawnTimeout = 5
__spawning = False

# these two are here to keep moHardware pattern of init() and update()
# however really need to use the async versions now
def init(addrStr=this.__defaultAddrStr):
    loggin.error("leicaPanel requires use of initAsync with nursery")
    pass
def update():
    # empty routine to keep moHardware pattern
    pass

async def initAsync(addrStr, nursery):
    log.debug("leicaDisto.initAsync begin")
    if addrStr == "default" or addrStr == None:
        addrStr=this.__defaultAddrStr
    if nursery == None:
        log.error("leica initAsync no nursery")
        return
    if this.isRunning() :
        log.error("leicaDistro attempt to initAsync but already running")
        log.error(str(this.__gatt))
        return
    this.__leicaAddressStr = addrStr
    this.__distMeters = -1
    this.updateModata() # stuff some data in there
    this.__timeoutCount = 0
    
    #try spawning
    await this.__attemptSpawn(nursery)    
    
    # if it started, run update loop
    if this.isRunning():
        log.debug("Leica GattTool started, spawn update task")
        nursery.start_soon(this.__updateLeicaLoop,nursery)
    else:
        log.error("Leica init failed to start gattool")

async def __startGattool():
    this.__timeoutCount = 0
    this.__leicaRestartsThisSession +=1
    this.__spawning = True
    # Run gatttool interactively.
    gatcmd = 'gatttool -b %s -t random -I' % this.__leicaAddressStr
    try: 
        this.__gatt = pexpect.spawn(gatcmd)
        #print("gatt spawned")
        # Connect to the device.
        this.__gatt.sendline('connect')
        # if dont get response in short time, no Leica found
        this.__gatt.expect('Connection successful', timeout=5)
        await trio.sleep(1)
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
        log.info("gttTool seems to have started, give couple sec")
        await trio.sleep(2) # was 3 give it time to settle?
    this.__spawning = False
    #print("gattool spawned init end", this.__gatt)

async def __attemptSpawn(nursery):
    log.debug("Leica __attemptSpawn")
    nursery.start_soon(this.__startGattool)
    this.__spawning = True
    while this.__spawning:
        await trio.sleep(1)
    log.debug(" after spawning running = "+ str(isRunning()))

async def __updateLeicaLoop(nursery):
    log.debug("Leica update task spawned")
    while True:
        await this.__update(nursery)
        if not this.isRunning():
            break
        await trio.sleep(1)
    log.debug("Leica update task ending")
        
async def __update(nursery):
    # send command to Leica, parse results
    # error handling
    #print("leica.__update() entered")
    if not this.isRunning():
        log.debug("No gattTool for Leica, attempt restart")
        await this.__attemptSpawn(nursery)
        #if still not running
        if not this.isRunning(): return
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
            await trio.sleep(0.5)
    except pexpect.EOF:
        log.error("leicaDisto.update() EOF - process died " + str(this.__gatt))
        # TODO: restart gatt Process... async
        this.__gatt = None
        gotEOF = true

    #print("LeicaDisto.update = ", this.distance())
    
def updateModata():
    d = {keyForTimeStamp(): this.timestampStr(), keyForDistance(): this.distance()}
    #print("update Leica Modata:", d)
    moData.update(keyForLeicaDisto(), d)
    
def timestampStr():
    this.timestamp = datetime.datetime.now()
    #print("timestamp:", this.timestamp)
    return this.timestamp.strftime("%Y-%m-%d %H:%M:%S%Z")

def distance():
#    if this.__distMeters < 0:
#        log.warn("LeicaDisto is negative")
    return this.__distMeters

def shutdown():
    log.info("Shutdown Leica Disto, total Timeouts: "+str(this.__leicaTimeoutsThisSession))
    log.info("   leica restarts this session"+str(this.__leicaRestartsThisSession))
    if not this.__gatt == None:
        this.__gatt.close()
        this.__gatt = None

def isRunning():
    if this.__gatt == None:
        return False
    return True

if __name__ == "__main__":
    print("modac.leicaDisto has no self test")
    exit(0)
  

