# moServer - modac Server networking stuff  

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers
import json
#from simplecrypt import encrypt, decrypt
from binascii import hexlify, unhexlify

#import rest of modac
from .moKeys import *
from . import moData, moNetwork, moHardware
# locally required for this module
from pynng import Pub0, Sub0, Pair1, Timeout

# pub sub messages
__Publisher = None
__CmdListener = None 

def shutdownServer():
    if not this.__Publisher == None:
        this.__Publisher.close()
    if not this.__CmdListener == None:
        this.__CmdListener.close()
    pass

def startServer():
    startPublisher()
    startCmdListener()

def startPublisher():
    logging.debug("start_Publisher")
    this.__Publisher = Pub0(listen=moNetwork.pubSubAddress())

def startCmdListener():
    this.__CmdListener =  Pair1(listen=moNetwork.cmdAddress(), polyamorous=True, recv_timeout=moNetwork.rcvTimeout())
    print("Cmd Listener: ",this.__CmdListener)
    pass

def publish():
    #logging.debug("publish - only AllData for now")
    publishData(keyForAllData(), moData.asDict())

def publishData(key, value):
    #print("dataStr: ", tempStr)
    msg = moNetwork.mergeTopicBody(key, value)
    eMsg = msg.encode('utf8')
    this.__Publisher.send(eMsg)
    #print("pub: ", msg)
    logging.debug("sendTopic %s"%msg)

def serverReceive():
    #not sure yet what this might become
    if this.__CmdListener == None:
        logging.error("attempt to serverReceive() CmdListener not initialized")
        return False
    msg = None
    try:
        msgObj = this.__CmdListener.recv_msg()
        #msgObj is a pyNNG Message with gives info on sender
        # body of msg is byteArray version of string keyforModacCommand()|cmd
        # where cmd is an encrypted Topic/body pairing
        # most of the guts of encrypt/decrypt is in moNetwork
        # by the time it gets back here as topic/body
        # it should be a string key and Object body (converted from json text)
        #print("Server Receive msgObj", msgObj)
        msgBytes = msgObj.bytes
        #print("Server Receive msgBytes", msgBytes)
        msgStr = msgBytes.decode('utf8')
        #print("Server Receive msgStr",msgStr)
        topic, body = moNetwork.decryptCommand(msgStr)
        print("Cmd topic,body:", topic,body)
        if topic == "error":
            logging.warning("CmdListener got non-modac command %s"%topic)
            return False
        # ok... body should hold modac encrypted command
        serverDispatch(topic,body)
        return True
    except Timeout:
        logging.debug("serverReceive() receive timeout")
        return False
    except :
        logging.error("serverReceive() caught exception %s"%sys.exc_info()[0])
        traceback.print_exc()#sys.exc_info()[2].print_tb()
        logging.exception("Some other exeption! on sub%d "%(i))
        return False


def cmdBinary(binaryId, onOff):
    #print("cmdBinary", binaryId, onOff)
    body = (binaryId, onOff)
    return this.sendCommand(keyforBinary((), body))

def serverDispatch(topic,body):
    print("serverDispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForBinaryCmd():
        payload = body # json.loads(body)
        print("serverDispatch payload")
        print(payload)
        moHardware.binaryCmd(payload[0],payload[1]) # channel, onOff
    else:
        logging.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   




if __name__ == "__main__":
    print("moServer has no self test")
    exit(0)
