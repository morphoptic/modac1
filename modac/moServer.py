# moServer - modac Server networking stuff using PyNNG
# https://github.com/codypiersall/pynng
#   Publish puts out tagged JSON messages of encrypted key,data (clients subscribe)
#       actually publishing is synchronous
#   Listen Thread: async to listen for client commands and serverDispatch() them

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json
#from simplecrypt import encrypt, decrypt
from binascii import hexlify, unhexlify
import trio #adding async functions use the Trio package

#import rest of modac
from .moKeys import *
from . import moData, moNetwork, moHardware
from kilnControl import kiln

# locally required for this module
from pynng import Pub0, Sub0, Pair1, Timeout

# pub sub messages
__Publisher = None
__CmdListener = None 
__killCmdListener = False

def shutdownServer():
    log.debug("try to kill moServer")
    this.__killCmdListener = True # this should stop the serverReceive() from pair1
    if not this.__Publisher == None:
        this.publish() # one last time
        this.publishData(keyForShutdown(), keyForShutdown())
        this.__Publisher.close()
        this.__Publisher = None

async def startServer(nursery):
    # publisher is synchronous for now
    startPublisher()
    # spawn off async cmd listener
    nursery.start_soon(startCmdListener, nursery)

def startPublisher():
    log.debug("start_Publisher")
    this.__Publisher = Pub0(listen=moNetwork.pubSubAddress())
    
def publish():
    log.debug("publish - only AllData for now")
    publishData(keyForAllData(), moData.asDict())

def publishData(key, value):
    if this.__Publisher == None:
        log.debug("publisher offline "+key)
        return
    #print("publish: key/value: ", key, value)
    msg = moNetwork.mergeTopicBody(key, value)
    eMsg = msg.encode('utf8')
    this.__Publisher.send(eMsg)
    #log.debug("sendTopic %s"%msg)

def publishKilnScriptEnded():
    if this.__Publisher == None:
        log.debug("publisher offline publishKilnScriptEnded")
        return
    print("publish: publishKilnScriptEnded")
    msg = moNetwork.mergeTopicBody(keyForKilnScriptEnded(), " ")
    eMsg = msg.encode('utf8')
    this.__Publisher.send(eMsg)


async def startCmdListener(nursery):
    this.__CmdListener =  Pair1(listen=moNetwork.cmdAddress(),
                                # poly means we listen to many
                                polyamorous=True,
                                recv_timeout = moNetwork.rcvTimeout())
    print("Cmd Listener: ",this.__CmdListener,moNetwork.rcvTimeout())
    nursery.start_soon(cmdListenLoop)

__killCmdListener = False
async def cmdListenLoop():
    # async forever loop
    # sorta semiphore to signal we are shutting down
    log.debug("Start cmdListenLoop")
    while not this.__killCmdListener:
        try:
            retval = await this.serverReceive()
        except trio.Cancelled:
            log.error("***cmdListenLoop caught trioCancelled, exiting")
            break
        if not retval:
            this.__killCmdListener = True
    log.error("***cmdListenLoop stopping")
    if not this.__CmdListener == None:
        this.__CmdListener.close()
        this.__CmdListener = None

async def serverReceive():
    if this.__CmdListener == None:
        log.error("aserverReceive() but CmdListener not initialized")
        this.__killCmdListener = True
        return False
    msg = None
    try:
        log.debug("serverReceive await msg")
        msgObj = await this.__CmdListener.arecv_msg()
        # async read will block here
        #msgObj is a pyNNG Message with gives info on sender
        # body of msg is byteArray version of string keyforModacCommand()|cmd
        # where cmd is an encrypted Topic/body pairing
        # most of the guts of encrypt/decrypt is in moNetwork
        # by the time it gets back here as topic/body
        # it should be a string key and Object body (converted from json text)
        print("Server Receive msgObj", msgObj)
        source_addr = str(msgObj.pipe.remote_address)
        # do we need to verify the source address?
        msgStr = msgObj.bytes.decode('utf8')
        #print("Server Receive msgStr",msgStr)
        topic, body = moNetwork.decryptCommand(msgStr)
        
        log.info("\n\nCommand Received")
        log.info("Command recieved from: %s = (%s,%s)"%(str(source_addr),str(topic), str(body)))
        
        print("Cmd topic,body:", topic,body)
        if topic == "error":
            log.warning("CmdListener got non-modac command %s"%topic)
            return True
        # ok... body should hold modac encrypted command
        serverDispatch(topic,body)
        return True
    except trio.Cancelled:
        log.debug("trio canclled exception")
        this.__killCmdListener = True
        return False
    except Timeout:
        # be quiet about it
        #log.debug("serverReceive() receive timeout")
        return True
    except AttributeError as e:
        log.error("AttributeError while handling command " + topic)
        log.exception(e)
        return True
    except:
        log.error("serverReceive() caught exception %s"%sys.exc_info()[0])
        traceback.print_exc()#sys.exc_info()[2].print_tb()
        #log.exception("Some other exeption! on sub%d "%(i))
        this.__killCmdListener = True
        return False
    log.error("server receive end")
    return True

def serverDispatch(topic,body):
    log.info("\n*******serverDispatch: Topic:'%s' Obj:'%s'"%(topic,body))
    if topic == keyForEmergencyOff():
        log.debug("EmergencyOff Cmd dispatching")
        moHardware.EmergencyOff() #patches thru to kiln.emergencyOff()
        
    elif topic == keyForBinaryCmd():
        payload = body # json.loads(body)
        #print("serverDispatch payload")
        #print(payload)
        moHardware.binaryCmd(payload[0],payload[1]) # channel, onOff
    elif topic == keyForAllOffCmd():
        moHardware.allOffCmd()
    elif topic == keyForResetLeica():
        moHardware.resetLeicaCmd()
        
    # kiln control commands: runScript, stopScript
    elif topic == keyForStopKilnScript():
        print("\n====== doing Kiln Abort script :", topic)
        log.info("Received StopKilnScript Command")
        if kiln.kilnInstance == None:
            log.info("no kiln object, ignore abort")
            return
        kiln.handleEndKilnScriptCmd()
        
    elif topic == keyForRunKilnScript():
        # where do we have the kiln stashed?
        # print("\n====== doing Kiln RUN :", topic)
        # print("\n\nload and run kiln script, body == ", body)
        if body == []:
            log.error("No data on runKiln")
        else:
            log.info("=== RunKiln param:"+ body)
            # need to unpack body?
            log.info("kiln cmd rcv with body: "+str(body))
            kiln.handleRunKilnScriptCmd(body)
    elif topic == keyForHello():
        log.info("Received Hello from Client ")
    else:
        log.warning("Unknown Topic in ClientDispatch %s"%topic)
        pass
        

if __name__ == "__main__":
    print("moServer has no self test")
    exit(0)
