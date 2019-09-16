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
#
# NOTE: Leica reads in METERS so we scale by 1000 to mm
#
'''
LeicaDisto Module holds singleton State and methods to talk with BLE Device
    via interactive conversation with a pexpect process running gatttool
    (caveat this doc is out of date. read code)
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
log.setLevel(logging.INFO)

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

#########
# some Enum classes for states
class GattState(Enum):
    '''States of the GattProcess internal to LeicaDisto Module'''
    Closed = 0 # before start and when done w no error
    Error = -1 # done and error occured
    Starting = 1 # between closed and open
    Open = 2

class LeicaState(Enum):
    '''States for the LeicaDisto module'''
    Closed = 0
    Error = -1
    Shutdown = -2
    Offline = 1
    Online = 2
    Looping = 3
    CloseRequested = 4

######
# some module globals that might get Config overrides someday
maxGattTimeoutTilClose = 3
maxGattRestartsTilDead = 5#sys.maxsize
TimeBetweenMeasurements = 5

# this is BLE MAC address, specific to unit. It shouold be in a config
# you can override it with setAddress() BEFORE calling init()
__defaultAddrStr = "D3:9D:70:68:8B:F2"

####
# module dunder variables
__leicaAddressStr = None
__gattProc = None
__leicaRestartsThisSession = 0
__leicaTimeoutsThisSession = 0
_state = LeicaState.Closed

######
# methods to access dunders
# maybe there is an attr way to do this
def incrementRestarts():
    this.__leicaRestartsThisSession += 1
def getRestartsThisSession():
    return this.__leicaRestartsThisSession

def incrementTimeouts():
    this.__leicaTimeoutsThisSession += 1
def getTimeoutsThisSession():
    return this.__leicaTimeoutsThisSession

def getLeicaAddress():
    return this.__leicaAddressStr
def setAddress(address= this.__defaultAddrStr):
    this.__leicaAddressStr = address
    log.debug("Address set to "+ this.__leicaAddressStr)
    
class gattProcess:
    '''spawns and runs the gatttool pexpect conversation'''
    state = this.GattState.Closed
    timestamp = datetime.datetime.now()
    distance = -1
    gatt = None
    timeoutCount = 0
    measureSuccess = False
    
    def hasGoodMeasurement(self):
        return self.measureSuccess

    def dumpDebug(self):
#        print("gattProc dump ",
#              self.state,
#              self.timeoutCount, self.measureSuccess
#              self.distance,self.timestamp)
#        #print("   gatt = ",self.gatt)
        pass
    #good place for attr ?
    def __init__(self):
        ''' setup instance; state Closed'''
        if this._state == LeicaState.Error or self.state == LeicaState.Shutdown:
            self.state = GattState.Error
            log.debug("cant create gattProcess, leica Error|Shutdown state")
            return
        self.state = this.GattState.Closed
        self.timestamp = datetime.datetime.now()
        self.distance = -1
        self.gatt = None
        self.timeoutCount = 0
#        print("gattProcess initialized %r"%(this))
        pass
    
    def getTimeouts():
        return self.timeoutCount()
    
    async def open(self):
        '''setup pexpect interprocess conversation and configure Disto
        thows exceptions
        its async so must await start()
        state: Open or Error '''
        log.debug("open Leica")
        if self.state == GattState.Error :#or this._state == LeicaState.Error:
            self.close()
            self.state = GattState.Error
            log.debug("Cant open gattProcess when in error state")
            return
        self.state = this.GattState.Starting
        self.measureSuccess = False
        # Run gatttool interactively.
        this.incrementRestarts()
        gatcmd = 'gatttool -b %s -t random -I' % this.getLeicaAddress()
        try: 
            await trio.sleep(0) # checkpoint,
            self.gatt = pexpect.spawn(gatcmd) #timeout=30 by default
            # if spawn fails -> exception probably
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
#            print("\n\n*** looks like success opening")
        except pexpect.TIMEOUT:
            log.warn("GattProcess start timeout Closing")
            log.error("Did Leica turn Off? need to turn leica back on")
            self.close()
            return
            # either the spawn or expect failed, close
        except pexpect.EOF:
            log.warn("leicaDisto.init EOF - process died " + str(self.gatt))
            self.close()
            return
        except trio.TooSlowError:
            # would we ever get this?
            log.warn("Trio TooSlowError. what to do? what to do?")
            self.close()
            self.state = GattState.Error
            return
        except trio.Cancelled:
            log.warn("Trio Canceled. Leica close up forever")
            self.close()
            self.state = GattState.Error
            this._state = LeicaState.Error
            return
        else:
            self.state = this.GattState.Open
            log.info("leicaDisto Connection Successful %r"%self.state)
            
        try:
            await trio.sleep(0) # checkpoint
        except trio.Cancelled:
            log.info("gattOpen ignoring checkpoint cancelled")
            pass
        
        log.debug("bottom of gattProcOpen, after checkpoint\n\n")
        pass

    def close(self):
        '''closes down the pexpect state Closed or Error'''
        log.info("gatt process close() start")
        self.dumpDebug()
        if not self.gatt == None:
            # still out there? kill it
            log.info("leica send SIGINT to its spawn")
            self.gatt.sendintr() # SIGINT CtrlC to gatttool, might block a bit
        del self.gatt # release/destroy object
        self.gatt = None # forget about it
        self.state = GattState.Closed
        if this.getRestartsThisSession() >= maxGattRestartsTilDead:
            self.state = GattState.Error
            this._state = LeicaState.Error
        log.info("gatt process close() end")
        self.dumpDebug()

    async def measure(self):
        '''sends query cmds/parses output, returns (distance, timestamp)
        thows exceptions
        state Open or Error'''
        self.measureSuccess = False
        if self.state == GattState.Error or this._state == LeicaState.Error:
            self.close()
            self.state = GattState.Error
            return
        if self.state == GattState.Closed:
            return
        try:
            #need to add some trio pauses
            #await trio.sleep(0) # checkpoint,
            self.gatt.sendline('char-write-cmd 0x0014 67')
            #await trio.sleep(0) # checkpoint,
            self.gatt.expect('handle = 0x000e value: ', timeout=1)
            #await trio.sleep(0) # checkpoint,
            self.gatt.expect('Indication')
            #await trio.sleep(0) # checkpoint,
            
            # parse the before buffer
            value = self.gatt.before 
            # Jerry: some very fancy data extraction voodoo here
            # gets first element [0] from unpacked struct,
            #    created from bytes converted from hexStr
            # which starts in the [:11] bytes before received 'Indication'
            #    bytes.fromhex(''.join(value[:11].decode().split())) 
            #       value[:11] .decode()  .split()
            meters = struct.unpack('<f',
                            bytes.fromhex(''.join(value[:11].decode().split())) )[0]
            self.distance = meters * 1000 #  We Want mm
            self.timeoutCount = 0
            self.state= GattState.Open
            # and we were successful!!
            self.measureSuccess = True
        except pexpect.TIMEOUT:
            this.incrementTimeouts()
            self.timeoutCount +=1
            log.warn("gatt measure timeout %d of %d (total: %d)"%
                (self.timeoutCount,
                 this.maxGattTimeoutTilClose,
                 this.getTimeoutsThisSession()))
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
            log.warn("gatt measure caughtTrio Cancelled.")
            self.close()
            self.state = GattState.Error
            this._state = LeicaState.Error
## end of gattProcess Class

def reset():
    log.debug("RESET Leica")
    if this._state == LeicaState.Shutdown:
        log.warn("tried to reset, but state is shutdown")
        return
    this._state = LeicaState.Closed
    this.__leicaRestartsThisSession = 0
    this.__leicaTimeoutsThisSession = 0
    if not this.__gattProc == None:
        this.__gattProc.close()
    this.__gattProc = None
    init()
 
def init():
    log.debug("leica init")
    d = {
    keyForTimeStamp(): "no data yet",
    keyForDistance(): -1,
    keyForStatus(): this._state.name
    }
    moData.update(keyForLeicaDisto(), d)

    if not this._state == LeicaState.Closed:
        log.error("trying to Init Leica when not Closed, needs Reset")
        return
    this._state = LeicaState.Offline
    if not this.__gattProc == None:
        log.error("we have a gattProc but are in init, ERROR")
        dumpDebug()
        this._state = LeicaState.Error
        return
    # get address string from config?
    # this *should* be in the module, not gattProcess
    if this.getLeicaAddress() == None:
        this.setAddress() # use default
    pass

def update():
    # empty routine to keep moHardware pattern
    #log.debug("leicaDisto update() does nothing state="+str(this._state))
    #log.info("leica last data: %r"%moData.getValue(keyForLeicaDisto()))
    pass

async def runLoop():
    ''' async task method nursery.start_soon(leicaDistoAsync.runloop())
    Double loop that keeps Leica alive and measuring until told to stop
        Outter loop creates a gattProcess, starts it, and if successful
        enter innerloop of measure/post/sleep until error or stop signal
        after innerloop, release gattProcess and continue outter loop '''
    #
    log.debug("starting runLoop")
    dumpDebug()
    while this._state == LeicaState.Looping:
        log.warn("leica is already looping!, trying to kill it")
        dumpDebug()
        this.close()
        await trio.sleep(TimeBetweenMeasurements*2)
        log.warn("ok maybe its dead now state= %d"%this._state)
    #
    while this.canRun():
        try:
            log.debug("runLoop top restarts="+str(this.getRestartsThisSession()))
            this.__gattProc = gattProcess() #init object
            if this.__gattProc == None:
                log.error("Error creating gattProc, break from runLoop outter")
                dumpDebug()
                break
            
            await this.__gattProc.open() # spawn process, wake Leica
            log.debug(" outter loop after try Proc Open")
            
            if this.__gattProc == None:
                log.debug("gattProc is gone?! end canRun loop")
                break;
            
            if this.__gattProc.state == GattState.Open:                
                this._state = LeicaState.Online
            else:
                log.error("gattProc failed to open")
                
            log.debug("runLoop before Outter While restarts="+str(this.getRestartsThisSession()))
            dumpDebug()
            while this.__gattProc.state == GattState.Open:
                this._state = LeicaState.Looping
                try:
                    def updateModata():                        
                        this.distance = this.__gattProc.distance
                        this.timestamp = datetime.datetime.now()
                        # update Modata
                        this.timestampStr = this.timestamp.strftime("%Y-%m-%d %H:%M:%S%Z")
                        d = {
                            keyForTimeStamp(): this.timestampStr,
                            keyForDistance(): this.distance,
                            keyForStatus(): this._state.name
                            }
                        log.debug("update Leica Modata: %r"%d)
                        moData.update(keyForLeicaDisto(), d)
                        
                    log.debug("wait for measurement")
                    dumpDebug()
                    await this.__gattProc.measure()
                    #if successful update, otherwise wait
                    if this.__gattProc.hasGoodMeasurement() :
                        updateModata()
                except trio.Cancelled:
                    log.info("caught trio Cancelled, close up")
                    this.close()
                # bottom of measure loop
#                if not this.canRun():
#                    log.debug("this.cant run at bottom of inner loop")
#                    break #get out!
#                print("bottom of measure loop")
                dumpDebug()
                #try:
                await trio.sleep(TimeBetweenMeasurements)
                #except trio.Cancelled:
                #    log.debug("cancelled sleep?")
#                print("bottom after sleep")
            # end measure forever loop 
            if this.__gattProc.state == GattState.Error:
                log.debug("runLoop sees gattError state")
                # drop out of while canRun loop
                this._state = LeicaState.Error
#                dumpDebug()
            else:
                this._state = LeicaState.Offline
#                dumpDebug()
            if not this.__gattProc == None:
                log.debug("bottom of outer while loop, close and discard gattProc") 
                this.__gattProc.close()
                del this.__gattProc
                this.__gattProc = None
#                dumpDebug()
            #print("outter loop try succeeded"); dumpDebug()
        except trio.Cancelled:
            log.info("runLoop caught trio Cancelled")
#            dumpDebug()
            this._state = LeicaState.Error
            pass
        # bottom of outter loop, either error, or timeoutClose
        # if not error, just Offline, can try restarting gattProc
        #print("bottom Outter: ");dumpDebug()
    #after while outter loop
    log.debug("runLoop after outter while")
#    dumpDebug()
    # cleanup and terminate
    
def canRun():
#    print("leica can run? dump")
#    dumpDebug()
    
    if this._state == LeicaState.Offline:
        return True
    if this._state == LeicaState.Looping:
        return True
    # easier to say what can run
    log.debug("canRun False in state "+this._state.name)
    return False

def close():
    this._state = LeicaState.CloseRequested
    if not this.__gattProc == None:
        this.__gattProc.close()
    
def isRunning():
    if this._state == LeicaState.Looping:
        return True
    return False

def shutdown():
    log.info("Shutdown Leica Disto, total Timeouts: "+str(this.getTimeoutsThisSession()))
    log.info("   leica restarts this session"+str(this.getRestartsThisSession()))
    this.close()
    this._state = LeicaState.Shutdown
    # is there some way to send signal to async proc?
    
def dumpDebug():
#    print("Leica state: ", this._state)
#    print("  address:",this.__leicaAddressStr )
#    print("  timeouts This Session: %d"%this.getTimeoutsThisSession())
#    print("  restarts this session: %d"%this.getRestartsThisSession())
#    if this.__gattProc== None:
#        print("  gattProc is None")
#    else:
#        print("  gattProc: ", this.__gattProc)
#        this.__gattProc.dumpDebug()
    pass

if __name__ == "__main__":
    print("modac.leicaDisto has no self test")
    exit(0)
  

