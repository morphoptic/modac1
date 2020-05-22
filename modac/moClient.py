# moClient - client side of modac networking using PyNNG Pair1 style polyamorous
# https://github.com/codypiersall/pynng

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json

#import rest of modac
from .moKeys import *
from . import moData, moNetwork
#from kilnControl import kiln
# locally required for this module
from pynng import Pub0, Sub0, Pair1, Timeout
import trio # adding Trio package to handle Cancelled

__CmdSender = None
#
__subscribers = [] # array of all subscribers on PubSub in this process

def shutdownClient():
    if not this.__CmdSender == None:
        this.__CmdSender.close()
    for s in this.__subscribers:
        s.close()
    log.debug("end shutdownClient")
    pass

def startClient():
    startSubscriber()
    startCmdSender()
    
# start PyNNG sender for commands to MODAC Server
def startCmdSender():
    this.__CmdSender =  Pair1(dial=moNetwork.cmdAddress(), polyamorous=True, send_timeout=moNetwork.sendTimeout())
    pass

# start PyNNG subscriber for Modac Server
def startSubscriber(keys=[keyForAllData(), keyForKilnStatus()]):
    #topics=[moTopicForKey(keyForAllData)]):
    timeout = 100
    subscriber = Sub0(dial=moNetwork.pubSubAddress(), recv_timeout=moNetwork.rcvTimeout(), topics=keys)
    if subscriber == None:
        log.error("client failed to connect to publisher")
    this.__subscribers.append(subscriber)
    # this doesnt format log.debug("startSubscriber: ", subscriber.toString())
    return subscriber

# client Recieve called from main or gtk loop 
# servers may also be doing a Pair1 sendCmd in their loop
def clientReceive():
    msgReceived = False
    for i in range(len(this.__subscribers)):
        try:
            while not msgReceived: #stays here till timeout or receive
                msgRaw = this.__subscribers[i].recv()
                #print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
                #log.info("sub %d rcv: %s"%(i,msgRaw.decode()))  # prints b'wolf...' since that is the matching message
                #print("clientReceive msgRaw", msgRaw)
                msg = msgRaw.decode('utf8')
                topic, body = moNetwork.splitTopicStr(msg)
                clientDispatch(topic,body)
                msgReceived = True
        except trio.Cancelled:
            log.warn("trio cancelled")
        except Timeout:
            log.debug("receive timeout on subsciber %d"%(i))
        except :
            log.exception("Some other exeption! on sub%d "%(i))
    return msgReceived
            
def clientDispatch(topic,body):
    log.debug("Dispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForAllData():
        moData.updateAllData(body)
    elif topic == keyForKilnStatus():
        moData.update(keyForKilnStatus(), body)
    else:
        log.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   

def sendCommand(key, value):
    print("moClient sendCommand key value ", key, value)
    log.debug("moClient sendCommand key value "+ key+" " +str( value))
    if this.__CmdSender == None:
        log.error("attempt to sendCommand from non-client")
        return False
    log.info("send command: key %s"%key)
    #package up the envelope with topic
    cmd = moNetwork.mergeTopicBody(key, value)
    msg = moNetwork.encryptCommand(cmd)
    log.info("sendCommand msg: %s"%msg)
    bmsg = msg.encode('utf8')
   #decryptCommand(msg)
    try:
        this.__CmdSender.send(bmsg)
    except trio.Cancelled:
        log.warn("trio cancelled")
    except Timeout:
        log.warn("Timeout sending message "+key)
    # for testing
    #print("decypher test: ", decryptCommand(msg))
    return True

if __name__ == "__main__":
    print("moClient has no self test")
    exit(0)
 