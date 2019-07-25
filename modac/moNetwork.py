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
from pynng import Pub0, Sub0, Timeout

# ewwww some top level public variables (module globals)
# guess they work sorta like Class variables, scope is this file
# those with __ prefix are NOT exported to other modules when import moNetwork

# TODO: convert us from raw ip to a zeroConf address
__zConfigName = "modac.local"
__pubAddress = 'tcp://127.0.0.1:31313'

# pub sub messages
__Publisher = None
__subscribers = [] # array of all subscribers, whether client or server's listener
# semantic idea is looping thru Subscribers will dipatch() all messages currently received by sockets
__topicDivider = '|'.encode('utf8')

def shutdownNet():
    if not __Publisher == None:
        __Publisher.close()
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
    startPublsiher()
    startCmdListener()

def startCmdListener():
    pass

def startPublsiher():
    logging.debug("start__Publisher")
    this.__Publisher = Pub0(listen=this.__pubAddress)

def startClient():
    startSubscriber()
    startCmdSender()
    
def startCmdSender():
    pass

# we really only have one topic at present. defaults should work until dispatch gets smarter
def startSubscriber(keys=[keyForAllData()]):#topics=[moTopicForKey(keyForAllData)]):
    timeout = 100
    subscriber = Sub0(dial=this.__pubAddress, recv_timeout=timeout, topics=keys)
    this.__subscribers.append(subscriber)
    #logging.debug("startSubscriber: ", subscriber)
    return subscriber
 
def sendData(key, value):
    tempStr = json.dumps(value)
    #print("dataStr: ", tempStr)
    msg = key.encode('utf8') + __topicDivider+tempStr.encode('utf8')
    this.__Publisher.send(msg)
    #print("pub: ", msg)
    logging.debug("sendTopic %s"%msg)
    
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

def splitTopicBody(msg):
    s = msg.decode('utf8')
    split = s.split('|')
    topic = split[0]
    body = json.loads(split[1])
    rv = (topic, body)
    print("Decoded:", rv)
    return rv
    
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
                dispatch(topic,body)
                msgReceived = True
        except Timeout:
            logging.debug("receive timeout on subsciber %d"%(i))
        except :
            logging.exception("Some other exeption! on sub%d "%(i))
    return msgReceived
            
def dispatch(topic,body):
    print("Dispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForAllData():
        moData.updateAllData(body)
    # need to extract the Topic    

def serverReceive():
    #not sure yet what this might become
    pass