# moServer - modac Server networking stuff  

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers, traceback
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
        this.__Publisher = None
    __killCmdListener = True

async def startServer(nursery):
    # publisher is synchronous for now
    startPublisher()
    # spawn off async cmd listener
    nursery.start_soon(startCmdListener, nursery)

def startPublisher():
    logging.debug("start_Publisher")
    this.__Publisher = Pub0(listen=moNetwork.pubSubAddress())
    
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

async def startCmdListener(nursery):
    this.__CmdListener =  Pair1(listen=moNetwork.cmdAddress(),
                                polyamorous=True,
                                recv_timeout=moNetwork.rcvTimeout())
    print("Cmd Listener: ",this.__CmdListener)
    nursery.start_soon(cmdListenLoop)

__killCmdListener = False
async def cmdListenLoop():
    # async forever loop
    # sorta semiphore to signal we are shutting down 
    while not this.__killCmdListener:
        await this.serverReceive()
    if not this.__CmdListener == None:
        this.__CmdListener.close()
        this.__CmdListener = None

async def serverReceive():
    #not sure yet what this might become
    if this.__CmdListener == None:
        logging.error("attempt to serverReceive() CmdListener not initialized")
        return False
    msg = None
    try:
        msgObj = await this.__CmdListener.arecv_msg()
        # async read will block here
        #msgObj is a pyNNG Message with gives info on sender
        # body of msg is byteArray version of string keyforModacCommand()|cmd
        # where cmd is an encrypted Topic/body pairing
        # most of the guts of encrypt/decrypt is in moNetwork
        # by the time it gets back here as topic/body
        # it should be a string key and Object body (converted from json text)
        #print("Server Receive msgObj", msgObj)
        source_addr = str(msgObj.pipe.remote_address)
        # do we need to verify the source address?
        msgStr = msgObj.bytes.decode('utf8')
        #print("Server Receive msgStr",msgStr)
        topic, body = moNetwork.decryptCommand(msgStr)
        logging.info("Command recieved from: %s = (%s,%s)"%(str(source_addr),str(topic), str(body)))
        
        print("Cmd topic,body:", topic,body)
        if topic == "error":
            logging.warning("CmdListener got non-modac command %s"%topic)
            return False
        # ok... body should hold modac encrypted command
        serverDispatch(topic,body)
        return True
    except Timeout:
        # be quiet about it
        #logging.debug("serverReceive() receive timeout")
        return False
    except :
        logging.error("serverReceive() caught exception %s"%sys.exc_info()[0])
        traceback.print_exc()#sys.exc_info()[2].print_tb()
        #logging.exception("Some other exeption! on sub%d "%(i))
        return False

def serverDispatch(topic,body):
    print("serverDispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForBinaryCmd():
        payload = body # json.loads(body)
        print("serverDispatch payload")
        print(payload)
        moHardware.binaryCmd(payload[0],payload[1]) # channel, onOff
    elif topic == keyForAllOffCmd():
        moHardware.allOffCmd()
    elif topic == keyForResetLeica():
        moHardware.resetLeicaCmd()
    else:
        logging.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   



if __name__ == "__main__":
    print("moServer has no self test")
    exit(0)
