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
#from simplecrypt import encrypt, decrypt
from binascii import hexlify, unhexlify

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
    if not this.__Publisher == None:
        this.__Publisher.close()
    if not this.__CmdListener == None:
        this.__CmdListener.close()
    if not this.__CmdSender == None:
        this.__CmdSender.close()
    for s in this.__subscribers:
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
    logging.debug("start_Publisher")
    this.__Publisher = Pub0(listen=this.__pubAddress)

def startClient():
    startSubscriber()
    startCmdSender()
    
def startCmdListener():
    this.__CmdListener =  Pair1(listen=this.__cmdAddress, polyamorous=True, recv_timeout=100)
    print("Cmd Listener: ",this.__CmdListener)
    pass

def startCmdSender():
    this.__CmdSender =  Pair1(dial=this.__cmdAddress, polyamorous=True, recv_timeout=100)
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

__topicDividerStr = '|'
__topicDivider = __topicDividerStr.encode('utf8')

def mergeTopicBody(key, value):
    print("mergeTopicBody",key,value)
    tempStr = json.dumps(value)
    assert isinstance(tempStr, str)
    print("value as str %s"%tempStr)
    msg = key + this.__topicDividerStr + tempStr
    print("mergeTopicBody msg: ",msg)
    return msg
    
def splitTopicBinary(msg):
    #assert isinstance(msg, bytearray)
    s = msg.decode('utf8')
    rv = splitTopicStr(s)
    return rv

def splitTopicStr(msg):
    #print("splitTopicStr start:", msg)
    # str.split splits at every Divider
    # max restricts it to one pair
    split = msg.split('|',1)
    #print("splitTopicStr split:", split)
    topic = split[0]
    body = json.loads(split[1])
    rv = (topic, body)
    #print("splitTopicStr rv:", rv)
    return rv

def sendData(key, value):
    #print("dataStr: ", tempStr)
    msg = mergeTopicBody(key, value)
    eMsg = msg.encode('utf8')
    this.__Publisher.send(eMsg)
    #print("pub: ", msg)
    logging.debug("sendTopic %s"%msg)

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
                topic, body = splitTopicBinary(msgRaw)
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

def serverReceive():
    #not sure yet what this might become
    if this.__CmdListener == None:
        logging.error("attempt to serverReceive() CmdListener not initialized")
        return False
    msg = None
    try:
        msgObj = this.__CmdListener.recv_msg()
        #msgObj is a pyNNG Message with gives info on sender
        #print("Server Receive msgObj", msgObj)
        msgBytes = msgObj.bytes
        #print("Server Receive msgBytes", msgBytes)
        msgStr = msgBytes.decode('utf8')
        #print("Server Receive msgStr",msgStr)
        topic, body = decryptCommand(msgStr)
        #print("topic,body:", topic,body)
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


def modacEncrypt(text):
    #print("modacEncrypt", text)
    assert isinstance(text, str)
    crypto = hexlify(text.encode('utf8'))
    #, unhexlifyencrypt("modac",text).decode('utf8') #.translate(rot13trans)
    if not isinstance(crypto,str):
        crypto = crypto.decode('utf8')
    return crypto

def modacDecrypt(crypto):
    clearTxt = unhexlify(crypto) #decrypt("modac",crypto).decode('utf8')#.translate(rot13trans)
    if not isinstance(clearTxt,str):
        clearTxt = clearTxt.decode('utf8')
    return clearTxt

def sendCommand(cmd):
    if this.__CmdSender == None:
        logging.error("attempt to sendCommand from non-client")
        return False
    logging.info("send command: %s"%cmd)
    #package up the envelope with topic
    encoded = modacEncrypt(cmd)
    msg = mergeTopicBody(keyForModacCmd(), encoded)
    bmsg = msg.encode('utf8')
    logging.info("cmd msg: %s"%msg)
    #decryptCommand(msg)
    this.__CmdSender.send(bmsg)
    # for testing
    #print("decypher test: ", decryptCommand(msg))
    return True

def decryptCommand(cmdMsg):
    #msg should be string key|json
    # extract tuple (key, txt)
    print("decryptCommand", cmdMsg)
    topic, body = splitTopicStr(cmdMsg)
    if not topic == keyForModacCmd():
        logging.error("decryptCommand not = %s => %s",keyForModacCmd(),topic)
        # should not receive non cmd this is error
        return ("error", "notModacCmd")
    decrypted = modacDecrypt(body) #might throw exception if fails?
    #need to test if properly decrypted throw security exception
    cmd, value = splitTopicStr(decrypted)
    print("Cmd %s Value ", cmd, value)
    rv = (cmd, value)
    if isinstance(value, list):
        print("Value is list")
        print("v0", value[0])
        print("v1", value[1])
    return rv
    

def cmdBinary(binaryId, onOff):
    #print("cmdBinary", binaryId, onOff)
    body = (binaryId, onOff)
    msg = mergeTopicBody(keyForBinaryCmd(), body)
    logging.debug("cmdBinary: %s"%msg)
    return sendCommand(msg)

def serverDispatch(topic,body):
    print("serverDispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForBinaryCmd():
        payload = body # json.loads(body)
        print("serverDispatch payload")
        print(payload)
        moData.binaryCmd(payload[0],payload[1]) # channel, onOff
    else:
        logging.warning("Unknown Topic in ClientDispatch %s"%topic)
    # handle other client messages   



