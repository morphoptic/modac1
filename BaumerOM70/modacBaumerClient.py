# Baumer OM-70 test using Trio Sockets
# default ip address is 198.162.0.250
# our rPi is on a dedicated switch on the 198.162.2.x network
# so that needs to be changed
#TODO also changed underlying OM70Datum into namedTuple, so more rework
import sys
this = sys.modules[__name__]
import trio
import datetime
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
import json
from . import OM70Datum
from modac.moKeys import *
from modac import moData

# address is set in web interface "Process Interface
__port = 12345
__baumer_udpAddr = ('', __port) # accept any sending address

__okToRun = True
__lastPostTime = None
__secBetweenPosts = datetime.timedelta(seconds=1.0)

__currentDatum = None

async def start(nursery= None):
    __okToRun = True
    __currentDatum = OM70Datum()
    if nursery is None:
        nursery = moData.getNursery()
    nursery.start_soon(baumerAsyncReceiveTask)
    update()

def shutdown():
    __okToRun = False

def update():
    # TODO: data lock for concurrent access?
    # grab namedTuple as dict for quick access
    d = this.__currentDatum.asDict()
    # then work with dictionary
    distance = d[OM70Datum.DISTANCEMM_NAME]
    now = datetime.now()
    d[keyForTimeStamp()] = now.strftime(moData.getTimeFormat())
    moData.update(keyForBaumerOM70(), json.dumps(d))
    moData.update(keyForDistance(), distance)

async def baumerAsyncReceiveTask():
    log.info("Begin receiveOm70Data "+ str( this.__baumer_udpAddr))
    this.__lastPostTime = datetime.now()
    try:
        # udp_sock = socket.socket(
        #     socket.AF_INET,  # IPv4
        #     socket.SOCK_DGRAM,  # UDP
        # )
        udp_sock = trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM)
        await udp_sock.bind(this.__baumer_udpAddr)
    except:
        log.error("Exception caught creating socket: ", exc_info=True)
        return

    buffSize = OM70Datum.byteSize()
    while __okToRun:
        now = datetime.now()
        try:
            data, address = await udp_sock.recvfrom(buffSize)
            #print("Received data from:", address)
            # TODO async lock?
            this.__currentDatum = OM70Datum.fromBuffer(data)
        except trio.Cancelled:
            log.warning("***Trio Cancelled anotherTask")
            return
        except:
            log.error("Exception caught in Forever Loop: ", exc_info=True)
            break
