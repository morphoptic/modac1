# MODAC pyWatcher - heartbeat sent via i2c to piWatcher hardware
# https://www.tindie.com/products/omzlo/piwatcher-the-best-watchdog-for-your-raspberry-pi/#specs
# its a lil HAT that controls power into Pi via gpio pin header - plug power into this vs pi
# board is intelligent and can be configured for several functions (see link)
# of interest here (modac) is power cycling when it fails to get i2c msg Heartbeat withing Timelimit
# setup: could use piwatcher app and shell script or send codes from here
# running: piWatcher.beatHeart()  at least 2x every TimeLimit
#
# For now we dont configure and start the watcher in boot; wait till startModac.sh
# be wary of putting BOTH these in startup or you'll be in an endless loop w/o heartbeat
# to set the piwatcher to wakeup 1min after shutdown
#    piwatcher wake 60
# to start the heatbeat watcher for 1bpm
#    piwatcher watch 60
# heartbeat happens by reading piwatcher status register. shell to do this
#    piwatcher status
# in python with this module that would be
#    pyWatcher.beatheart()


import sys
this = sys.modules[__name__]

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import smbus2

__i2cAddr = 0x62
__watcher = None

def init():
    try:
       if __watcher == None:
            __watcher = PyWatcher()
    except:
        log.error("Exception happened, maybe no pi watcher board at i2c 62?", exc_info=True)
        pass

def reset():
    if this.__watcher == None:
        # if no piwatcher,
        return
    this.__watcher.reset()

def beatHeart():
    if this.__watcher == None:
        # if no piwatcher,
        return
    this.__watcher.beatHeart()

class PyWatcher:
    def __init__(self):
        self.bus = smbus2.SMBus(1)
        self.i2cAddress = this.__i2cAddr
#        self.reset()

    def reset(self):
        # send reset
        res = self.bus.write_byte_data(self.i2cAddress, 0, 0xFF);

    def setForHeartbeat(self, timeout=60):
        # setup watcher to reboot if no heartbeat in timeout (60) sec
        # piwatcher watch timeout
        pass

    def beatHeart(self):
        # send a heartbeat to piWatcher;
        # read register 0 of i2c device
        # dont care about actual status returned
        res = self.bus.read_byte_data(self.i2cAddress, 0);
        pass


