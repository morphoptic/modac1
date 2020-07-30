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
from . import moData, moNetwork, moCommand
# locally required for this module
from pynng import Pub0, Sub0, Pair1, Timeout
import pynng
import trio # adding Trio package to handle Cancelled

__CmdSender = None
#
__subscribers = [] # array of all subscribers on PubSub in this process

__kilnCallback = None
__running = False

def setKilnCallback(function):
    log.info("Set KilnCallback: " + repr(function))
    this.__kilnCallback = function

def shutdownClient():
    if not this.__CmdSender == None:
        this.__CmdSender.close()
    for s in this.__subscribers:
        s.close()
    log.debug("end shutdownClient")
    this.__running = False
    pass

def isRunning():
    return this.__running

def startClient():
    startSubscriber()
    startCmdSender()
    moCommand.cmdHello() # say hello to our little friend
    this.__running = True

    
# start PyNNG sender for commands to MODAC Server
def startCmdSender():
    this.__CmdSender =  Pair1(dial=moNetwork.cmdAddress(), polyamorous=True, send_timeout=moNetwork.sendTimeout())
    pass

# start PyNNG subscriber for Modac Server
#need to register for whatever published keys you want to receive
def startSubscriber(keys=[keyForAllData(), keyForKilnScriptEnded(), keyForKilnStatus(), keyForShutdown()]):
    #topics=[moTopicForKey(keyForAllData)]):
    timeout = 100
    log.debug("startClientSubscriber keys: %r"%keys)
    subscriber = Sub0(dial=moNetwork.pubSubAddress(), recv_timeout=moNetwork.rcvTimeout(), topics=keys)
    if subscriber == None:
        log.error("client failed to connect to publisher")
    this.__subscribers.append(subscriber)
    # this doesnt format log.debug("startSubscriber: ", subscriber.toString())
    return subscriber

# client Receive called from main or gtk loop  CAUTION: be sure to sync changes with asyncClientReceive
# servers may also be doing a Pair1 sendCmd in their loop
# This will do one receive: ending either with receipt and dispatch or Timeout
def clientReceive():
    msgReceived = False
    for i in range(len(this.__subscribers)):
        try:
            while not msgReceived: #stays here till timeout or receive
                log.debug("client subscriber %d rcv"%(i))
                msgRaw = this.__subscribers[i].recv()
                #print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
                log.info("sub %d rcv: %s"%(i,msgRaw.decode()))  # prints b'wolf...' since that is the matching message
                #print("clientReceive msgRaw", msgRaw)
                clientHandleRecievedMsg(msgRaw)
                msgReceived = True
        except Timeout:
            log.debug("receive timeout on subsciber %d"%(i))
        except :
            log.exception("Some other exception! on subcriber channel %d "%(i))
            exc = traceback.format_exc()
            log.error("Traceback is: " + exc)
    return msgReceived

def clientHandleRecievedMsg(msgRaw):
    msg = msgRaw.decode('utf8')
    topic, body = moNetwork.splitTopicStr(msg)
    clientDispatch(topic, body)

# async version of client Recieve; should be called in a Trio Nursery event loop
# This will do one receive: ending either with receipt and dispatch or Timeout
# either one will return to the parent loop
async def asyncClientReceive():
    msgReceived = False
    for i in range(len(this.__subscribers)):
        try:
            msgRaw = await this.__subscribers[i].arecv()
            clientHandleRecievedMsg(msgRaw)
            msgReceived = True
        # trio closed exceptions not caught here
        except pynng.exceptions.Closed:
            log.debug("Closed: subscriber %d - so terminate" % (i))
            return False
        except Timeout:
            log.debug("receive timeout on subscriber %d" % (i))
        except:
            log.exception("Some other exception! on subscriber %d " % (i))
            return False
    return msgReceived


def clientDispatch(topic,body):
    log.debug("Dispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForAllData():
        #log.debug("AllData body "+json.dumps(body, indent=4))
        moData.updateAllData(body)
    elif topic == keyForKilnStatus():
        moData.update(keyForKilnStatus(), body)
    elif topic == keyForKilnScriptEnded():
        log.debug("Topic = ScriptEnded try calling kilnCallback")
        if not this.__kilnCallback == None:
            log.info("yep one set, call it")
            this.__kilnCallback(topic, body)
        else:
            log.error("Ooops - no callback for kilnCallback")
        pass
    elif topic == keyForShutdown():
        log.warning("Shutdown Command received from Server")
        this.shutdownClient()
    else:
        log.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   

def sendCommand(key, value):
    print("moClient sendCommand key value ", key, value)
    log.debug("moClient sendCommand key value "+ key+" " +str( value))
    if this.__CmdSender == None:
        log.error("attempt to sendCommand from non-client")
        return False
    #log.info("send command: key %s"%key)
    #package up the envelope with topic
    cmd = moNetwork.mergeTopicBody(key, value)
    msg = moNetwork.encryptCommand(cmd)
    #log.info("sendCommand msg: %s"%msg)
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
 