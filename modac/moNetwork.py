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

pubAddress = 'tcp://127.0.0.1:31313'

def shutdownNet():
    pass

# pub sub messages
publisher = None
subscribers = []
topicDivider = '|'.encode('utf8')

def init():
    startPubSub()
    
def startPubSub():
    startPublisher()
    startSubscriber()
    
def startPublisher():
    logging.debug("startPublisher")
    this.publisher = Pub0(listen=this.pubAddress)

def startSubscriber(keys=[keyForAllData()]):#topics=[moTopicForKey(keyForAllData)]):
    timeout = 100
#    subtopics = []
#    for i in range(len(keys)):
#        subtopics.append(topicForKey(keys[i]))
    subscriber = Sub0(dial=this.pubAddress, recv_timeout=timeout, topics=keys)
    this.subscribers.append(subscriber)
    #logging.debug("startSubscriber: ", subscriber)
    return subscriber
 
def sendData(key, value):
    tempStr = json.dumps(value)
    #print("dataStr: ", tempStr)
    msg = key.encode('utf8') + topicDivider+tempStr.encode('utf8')
    this.publisher.send(msg)
    #print("pub: ", msg)
    logging.debug("sendTopic %s"%msg)
    
def sendKtype():
    sendData(keyForKType(), moData.kType.asArray())
    
def sendEnviro():
    sendData(keyForEnviro(), moData.enviro.asDict())

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
    
def receive():
    for i in range(len(subscribers)):
        try:
            while(1): #stays here till timeout or receive
                msgRaw = this.subscribers[i].recv()
                #print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
                logging.info("sub %d rcv: %s"%(i,msgRaw.decode()))  # prints b'wolf...' since that is the matching message
                topic, body = splitTopicBody(msgRaw)
                dispatch(topic,body)
        except Timeout:
            logging.debug("receive timeout on subsciber %d"%(i))
        except :
            logging.exception("Some other exeption! on sub%d "%(i))
            
def dispatch(topic,body):
    print("Dispatch: Topic:%s Obj:%s"%(topic,body))
    if topic == keyForAllData():
        moData.updateAllData(body)
    # need to extract the Topic    
