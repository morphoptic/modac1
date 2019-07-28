# moNetwork - pubsub etc networking
if __name__ == "__main__":
    print("moNetwork has no self test")
    exit(0)
  
# as refactor... note the Key names for dictionaries in msgs are magicStrings
# need to put these data key names along with topic names in variables

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers
import json

#import rest of modac
from .moKeys import *
from . import moData
# locally required for this module
from pynng import Pub0, Sub0, Pair1, Timeout

# ewwww some top level public variables (module globals)
# guess they work sorta like Class variables, scope is this file
# those with __ prefix are NOT exported to other modules when import moNetwork

# TODO: convert us from raw ip to a zeroConf address
__zConfigName = "modac.local"
__pubAddress = 'tcp://127.0.0.1:31313'
__cmdAddress = 'tcp://127.0.0.1:21212'

# pub sub messages
__Publisher = None
__CmdListener = None 
__CmdSender = None
#
__subscribers = [] # array of all subscribers on PubSub in this process

def shutdownNet():
    if not __Publisher == None:
        __Publisher.close()
    if not __CmdListener == None:
        __CmdListener.close()
    if not __CmdSender == None:
        __CmdSender.close()
    for s in __subscribers:
        s.close()
    pass

def init(client=True):
    assert False, "do not init() use startServer() or startClient()"
    if client:
        startClient()
    else:
        startServer()
    pass

def startPubSub():
    startServer()
    startSubscriber()
    
def startServer():
    startPublisher()
    startCmdListener()

def startPublisher():
    logging.debug("start__Publisher")
    this.__Publisher = Pub0(listen=this.__pubAddress)

def startClient():
    startSubscriber()
    startCmdSender()
    
def startCmdListener():
    __CmdListener =  Pair1(listen=__cmdAddress, polyamorous=True, recv_timeout=100)
    pass

def startCmdSender():
    __CmdSender =  Pair1(dial=__cmdAddress, polyamorous=True, recv_timeout=100)
    pass

# we really only have one topic at present. defaults should work until dispatch gets smarter
def startSubscriber(keys=[keyForAllData()]):#topics=[moTopicForKey(keyForAllData)]):
    timeout = 100
    subscriber = Sub0(dial=this.__pubAddress, recv_timeout=timeout, topics=keys)
    this.__subscribers.append(subscriber)
    #logging.debug("startSubscriber: ", subscriber)
    return subscriber

#def sendKtype():
#    sendData(keyForKType(), moData.kType.asArray())
#    
#def sendEnviro():
#    sendData(keyForEnviro(), moData.enviro.asDict())

def sendAllData():
    sendData(keyForAllData(), moData.asDict())

def publish():
    #logging.debug("publish - only AllData for now")
#    sendKtype()
#    sendEnviro()
    sendAllData()

__topicDividerRaw = '|'
__topicDivider = __topicDividerRaw.encode('utf8')

def mergeTopicBody(key, value):
    msg = key.encode('utf8') + __topicDivider + value.encode('utf8')
    return msg
    
def splitTopicBody(msg):
    s = msg.decode('utf8')
    split = s.split('|')
    topic = split[0]
    body = json.loads(split[1])
    rv = (topic, body)
    print("Decoded:", rv)
    return rv

def sendData(key, value):
    tempStr = json.dumps(value)
    #print("dataStr: ", tempStr)
    msg = mergeTopicBody(key, tempStr)
    this.__Publisher.send(msg)
    #print("pub: ", msg)
    logging.debug("sendTopic %s"%msg)

# client Recieve Loop, server will be different
def clientReceive():
    msgReceived = False
    for i in range(len(__subscribers)):
        try:
            while(1): #stays here till timeout or receive
                msgRaw = this.__subscribers[i].recv()
                #print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
                logging.info("sub %d rcv: %s"%(i,msgRaw.decode()))  # prints b'wolf...' since that is the matching message
                topic, body = splitTopicBody(msgRaw)
                clientDispatch(topic,body)
                msgReceived = True
        except Timeout:
            logging.debug("receive timeout on subsciber %d"%(i))
        except :
            logging.exception("Some other exeption! on sub%d "%(i))
    return msgReceived
            
def clientDispatch(topic,body):
    print("Dispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForAllData():
        moData.updateAllData(body)
    else:
        logging.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   

def serverReceive():
    #not sure yet what this might become
    if __CmdListener == None:
        logging.error("attempt to serverReceive() CmdListener not initialized")
        return False
    msg = None
    try:
        rawMsg = __CmdListener.recv_msg()
        #rawMsg is a pyNNG Message with gives info on sender
        msgBytes = rawMsg.bytes
        topic, body = splitTopicBody(msgBytes)
        if not topic == keyForModacCmd():
            logging.warning("CmdListener got non-modac command %s"%topic)
            return False
        # ok... body should hold modac encrypted command
        body = modacDecrypt(body)
        topic, body = splitTopicBody(msgRaw)
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


# security encoding of commands
def modacEncode(text):
    encodedText = text
    return encodedText

def modacDecode(crypto):
    clearTxt = crypto
    return clearTxt

def sendCommand(cmd):
    if __ClientSender == None:
        logger.error("attempt to sendCommand from non-client")
        return False
    logger.info("send command: %s"%cmd)
    #package up the envelope with topic
    msg = keyForModacCmd() + __topicDividerRaw + modacEncode(cmd)
    msg = msg.encode('utf8')
    __ClientSender.send(msg)
    return True

def cmdBinary(binaryId, onOff):
    body = keyForBinaryCmd()+ json.dumps((binaryId, onOff))
    logging.debug("cmdBinary: %s"%body)
    return sendCommand(body)

def serverDispatch(topic,body):
    print("serverDispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForBinaryCmd():
        payload = json.loads(body)
        print("serverDispatch payload")
        print(payload)
        moData.binaryCmd(payload[0],payload[1]) # channel, onOff
    else:
        logging.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   



