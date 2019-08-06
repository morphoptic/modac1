# moClient - client side of modac networking

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers
import json

#import rest of modac
from .moKeys import *
from . import moData, moNetwork
# locally required for this module
from pynng import Pub0, Sub0, Pair1, Timeout

__CmdSender = None
#
__subscribers = [] # array of all subscribers on PubSub in this process

def shutdownClient():
    if not this.__CmdSender == None:
        this.__CmdSender.close()
    for s in this.__subscribers:
        s.close()
    pass

def startClient():
    startSubscriber()
    startCmdSender()
    
def startCmdSender():
    this.__CmdSender =  Pair1(dial=moNetwork.cmdAddress(), polyamorous=True, recv_timeout=moNetwork.rcvTimeout())
    pass

# we really only have one topic at present. defaults should work until dispatch gets smarter
def startSubscriber(keys=[keyForAllData()]):#topics=[moTopicForKey(keyForAllData)]):
    timeout = 100
    subscriber = Sub0(dial=moNetwork.pubSubAddress(), recv_timeout=moNetwork.rcvTimeout(), topics=keys)
    this.__subscribers.append(subscriber)
    #logging.debug("startSubscriber: ", subscriber)
    return subscriber


# client Recieve Loop, server will be different
# servers may also be doing a Pair1 sendCmd in their loop
def clientReceive():
    msgReceived = False
    for i in range(len(this.__subscribers)):
        try:
            while(1): #stays here till timeout or receive
                msgRaw = this.__subscribers[i].recv()
                #print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
                logging.info("sub %d rcv: %s"%(i,msgRaw.decode()))  # prints b'wolf...' since that is the matching message
                #print("clientReceive msgRaw", msgRaw)
                msg = msgRaw.decode('utf8')
                topic, body = moNetwork.splitTopicStr(msg)
                clientDispatch(topic,body)
                msgReceived = True
        except Timeout:
            logging.debug("receive timeout on subsciber %d"%(i))
        except :
            logging.exception("Some other exeption! on sub%d "%(i))
    return msgReceived
            
def clientDispatch(topic,body):
    #print("Dispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForAllData():
        moData.updateAllData(body)
    else:
        logging.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   

def sendCommand(key, value):
    print("moClient sendCommand key value", key, value)
    if this.__CmdSender == None:
        logging.error("attempt to sendCommand from non-client")
        return False
    logging.info("send command: key %s"%key)
    #package up the envelope with topic
    cmd = moNetwork.mergeTopicBody(key, value)
    msg = moNetwork.encryptCommand(cmd)
    logging.info("sendCommand msg: %s"%msg)
    bmsg = msg.encode('utf8')
   #decryptCommand(msg)
    this.__CmdSender.send(bmsg)
    # for testing
    #print("decypher test: ", decryptCommand(msg))
    return True

if __name__ == "__main__":
    print("moClient has no self test")
    exit(0)
 