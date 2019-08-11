# MODAC leicaDisto D1 distance Ashync Trio version
# interactively converses with "gatttool" process spawned with pexpect
# seems to be based on work by Josuha Benjamin & David Kaplan U. Florida
# as part of "Fine Scale Laser Based water level sensor"
# https://www.watershedecology.org/uploads/1/2/7/3/12731039/benjamin_and_kaplan_2017_ieee.pdf
# their code is refrenced there as leica.py
# first version for Modac shared March 2019 by Joe as "laser3.6.py" and "laser2.7.py"
# ian revised and hacked simple script that also read a thermocouple
# Other libs on github for leica disto include:
#    https://github.com/JohannesBakker/LeicaDistoControl
#    https://github.com/normanargiolas/disto-leica-bluetooth
# neither is in python
# neither uses gattTool
# both are very complex
# python/pexpect+gatttool work but are a bit opague
#
# TODO: Needs better Trio integration for async issues w pexpect process
#
# aug 11 reworking for better async citizen
'''
LeicaDisto Module holds singleton State and methods to talk with BLE Device
    via interactive conversation with a pexpect process running gatttool
 gattTool has two phases we must handle - setup (open?) and measure.
 You must setup/open a connection before you measure
     gattSetup: sets up the pexpect, sends config commands to Disto
     gattMeasure: sends query cmds to BLE, parses responses.
   it either succeeds (updates distance and timestamp values) or fails (exception)
   exceptions can be:
      trio.Cancel - nursery shutdown, etc
      pexpect. EOF/TIMEOUT
      pexpect dead/closed
 So our API is:
 init, initAsync, startAsync, close, update/updateBlocking, updateAsync, updateLoop
 
 init sets up leica Config... including LeicaState
     states are OFFLINE, Online_Setup, Online_Looping, waiting, Canceled ??
 startAsync gets the pexpect process running; exceptions indicate failure
     its async so must use await leica.startAsync()
     exceptions include:
      trio.Cancel - nursery shutdown, etc
      pexpect. EOF/TIMEOUT
      pexpect dead/closed
 initAsync does init and nursery.start_soon(startAsync)
     client must await initAsync(nursery)
     exceptions: trio.Cancel, modac.shutdown
     client must watch State to handle restarts
 update() : convention for moHardware
    checks that updateLoop is running
         insures local {distance, timestamp} is in moData
    if not running, should it startLoop 
         or do own updateBlocking() and expects caller to handle exceptions?
 updateBlocking is blocking call to measure + save to moData;
     caller deals with exceptions
 updateLoop - trio start_soon loop that restarts GattTool if connection lost
     respects trio.Cancel and Modac Shutdown requests
     retries N times for timeouts then cancels GattTool
     retries Spawn GattTool N times
     if MaxSpawnThreshold exceeded
         ask user to check power
         give up and declare ourselves OFFLINE
'''
# moHardware usual init() and update() are here usage questionable
# 

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
#
import math
import pexpect
import struct
import signal
import trio
from enum import Enum

# this is BLE MAC address, specific to unit. It needs to be in config file
__defaultAddrStr = "D3:9D:70:68:8B:F2"
__leicaAddressStr = None

__leicaRestartsThisSession = 0
__leicaTimeoutsThisSession = 0
maxGattTimeoutTilClose = math.max
maxGattRestartsTilDead = math.max

# dunder makes it private to this module?
class GattState(Enum):
    Closed = 0
    Error = -1
    Open = 1
class GattClosed(RuntimeError):
    pass

class LeicaState(Enum):
    Closed = 0
    Error = -1
    Offline = 1
    Online = 2
    Looping = 3

leica_state = LeicaState.Closed
__spawning = True

class gattProcess:
    '''spawns and runs the gatttool pexpect conversation'''
    state = this.GattState.Closed
    timestamp = datetime.datetime.now()
    distance = -1
    gatt = None
    timeoutCount = 0
    #good place for attr ?
    def __init__(self, address=None):
        ''' setup instance; state Closed'''
        if this.state == LeicaState.Error:
            self.state = GattState.Error
            return
        self.state = this.GattState.Closed
        self.timestamp = datetime.datetime.now()
        self.distance = -1
        self.gatt = None
        self.timeoutCount = 0
        # this *should* be in the module, not gattProcess
        if this.__leicaAddressStr == None:
            this.__leicaAddressStr = this.__defaultAddrStr
        if not address == None:
            this.__leicaAddressStr = address
        pass
    
    async def start(self):
        '''setup pexpect interprocess conversation and configure Disto
        thows exceptions
        its async so must await start()
        state: Open or Error '''
        if self.state == GattState.Error or this.state == LeicaState.Error:
            self.close()
            self.state = GattState.Error
            return
        # Run gatttool interactively.
        __leicaRestartsThisSession += 1
        gatcmd = 'gatttool -b %s -t random -I' % this.__leicaAddressStr
        try: 
            self.gatt = pexpect.spawn(gatcmd) #timeout=30 by default
            # if spawn fails?
            #print("gatt spawned")
            # Connect to the device.
            self.gatt.sendline('connect')
            # if dont get response in short time, no Leica found
            self.gatt.expect('Connection successful', timeout=5)
            await trio.sleep(1) # be Trio Friendly while giving it some time to wakeup
            # send some magic words to "Enable Indications"
            # TODO: find out what these mean
            self.gatt.sendline('char-write-cmd 0x000b 0200')
            self.gatt.sendline('char-write-cmd 0x000f 0200')
            self.gatt.sendline('char-write-cmd 0x0012 0200')
            self.state= GattState.Open
            log.info("leicaDisto Connection Successful")
        except pexpect.TIMEOUT:
            log.warn("GattProcess start timeout gatt:"+ str(self.gatt) + " Closing")
            log.error("Did Leica turn Off? need to turn leica back on")
            self.close()
            # either the spawn or expect failed, close
        except pexpect.EOF:
            log.warn("leicaDisto.init EOF - process died " + str(self.gatt))
            self.close()
        except trio.TooSlowError:
            # would we ever get this?
            log.warn("Trio TooSlowError. what to do? what to do?")
            self.close()
            self.state = GattState.Error
        except trio.Cancelled:
            log.warn("Trio Canceled. close up forever")
            self.close()
            self.state = GattState.Error
        pass

    def close(self):
        '''closes down the pexpect state Closed or Error'''
        log.info("gatt process closed")
        if not self.gatt == None:
            # still out there? kill it
            self.gatt.sendintr() # SIGINT CtrlC to gatttool
        del self.gatt # release/destroy object
        self.gatt = None # forget about it
        self.state = GattState.Closed
        if this.__leicaRestartsThisSession >= maxGattRestartsTilDead:
            self.state = GattState.Error

    def measure(self):
        '''sends query cmds/parses output, returns (distance, timestamp)
        thows exceptions
        state Open or Error'''
        if self.state == GattState.Error or this.state == LeicaState.error:
            self.close()
            self.state = GattState.Error
            return
        try:
            self.gatt.sendline('char-write-cmd 0x0014 67')
            self.gatt.expect('handle = 0x000e value: ', timeout=0.5)
            self.gatt.expect('Indication')
            
            # parse the before buffer
            value = self.gatt.before 
            # Jerry: some very fancy data extraction voodoo here
            # gets first element [0] from unpacked struct,
            #    created from bytes converted from hexStr
            # which starts in the [:11] bytes before received 'Indication'
            #    bytes.fromhex(''.join(value[:11].decode().split())) 
            #       value[:11] .decode()  .split()
            self.distanceMeters = struct.unpack('<f',
                            bytes.fromhex(''.join(value[:11].decode().split())) )[0]
            self.timeoutCount = 0
            self.state= GattState.Open
            # and we were successful!!
        except pexpect.TIMEOUT:
            #noTimeout = False
            this.__leicaTimeoutsThisSession += 1
            self.timeoutCount +=1
            log.warn("gatt measure timeout %d of %d (total: %d)"%
                (self.timeoutCount,
                 this.maxGattTimeoutTilClose,
                 this.__leicaTimeoutsThisSession))
            if self.timeoutCount >= this.maxGattTimeoutTilClose:
                self.close()
        except pexpect.EOF:
            log.error("leicaDisto.update() EOF - process died " + str(self.gatt))
            self.close()
        ## should we handle or pass on trio exceptions?
        except trio.TooSlowError:
            # would we ever get this?
            log.warn("Trio TooSlowError. what to do? what to do?")
            self.close()
            self.state = GattState.Error
        except trio.Cancelled:
            # would we ever get this?
            log.warn("Trio Cancelled. what to do? what to do?")
            self.close()
            self.state = GattState.Error
## end of gattProcess Class
-----------------------------
and that is as far as I write tonight

# gatt is pexpect spawned process w comm pipe
__gatt= None
__distMeters = -1
__leicaTimeoutsThisSession = 0
__leicaRestartsThisSession = 0
__gattSpawnTimeout = 5
__spawning = False
__shutdown = False

# these two are here to keep moHardware pattern of init() and update()
# however really need to use the async versions now
def init(addrStr=this.__defaultAddrStr):
    log.error("leicaPanel requires use of initAsync with nursery")
    pass
def update():
    # empty routine to keep moHardware pattern
    log.error("leicaDisto should not use update(), use AsyncLoop")
    pass

async def initAsync(addrStr, nursery):
    '''initAsnc sets up the address, initialize globals (incl moData)
        then uses await __attemptSpawn()
        and if successfully running, start_soon(__updateLeicaLoop)
    '''
    log.debug("leicaDisto.initAsync begin")
    if nursery == None:
        log.error("leica initAsync no nursery")
        return
    if addrStr == "default" or addrStr == None:
        addrStr=this.__defaultAddrStr
    if this.isRunning() :
        log.error("leicaDistro attempt to initAsync but already running")
        log.error(str(self.__gatt))
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

async def __attemptSpawn(nursery):
    if this.__shutdown:
        log.warn("shutdown requested, no more spawning")
        return
    log.debug("Leica __attemptSpawn")
    nursery.start_soon(this.__startGattool)
    this.__spawning = True
    while this.__spawning:
        await trio.sleep(1)
        if this.__shutdown:
            break
    log.debug(" after spawning running = "+ str(isRunning()))

async def __updateLeicaLoop(nursery):
    log.debug("Leica update task spawned")
    while True:
        await this.__update(nursery)
        if not this.isRunning():
            break
        if this.__shutdown:
            return
        await trio.sleep(1)
    log.debug("Leica update task ending")
        
async def __update(nursery):
    # send command to Leica, parse results
    # error handling
    if this.__shutdown:
        return
    #print("leica.__update() entered")
    if not this.isRunning():
        log.debug("No gattTool for Leica, attempt restart")
        await this.__attemptSpawn(nursery)
        #if still not running
        if not this.isRunning():
            return
    if this.__shutdown:
        return
    noTimeout = True
    gotEOF = False
gatt measure()

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
    this.__shutdown = True
    if not self.__gatt == None:
        self.__gatt.close()
        self.__gatt = None

def isRunning():
    if self.__gatt == None:
        return False
    return True

if __name__ == "__main__":
    print("modac.leicaDisto has no self test")
    exit(0)
  

