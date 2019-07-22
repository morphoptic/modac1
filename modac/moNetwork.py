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
from . import moData
# locally required for this module
from pynng import Pub0, Sub0, Timeout

pubAddress = 'tcp://127.0.0.1:31313'

def shutdownNet():
    pass

# pub sub messages
publisher = None
subscribers = []

# msg topics, dont really need these here
# as they are just local copies of moData topics
topic_ktype = moData.kType.topic() #b'ktype'
topic_enviro = moData.enviro.topic() # b'enviro'
topic_rawA = moData.ad24.topicRaw() #b'rawA'
topic_5vA = moData.ad24.topicVv05() #b'5vA'
topic_ad24 = moData.ad24.topic()
topic_allData = moData.topic() #b'allData' 

def init():
    startPubSub()
    
def startPublisher():
    logging.debug("startPublisher")
    this.publisher = Pub0(listen=this.pubAddress)
    logging.debug("startPublisher: ", this.publisher)
    
def startSubscriber():
    timeout = 100
    subscriber = Sub0(dial=this.pubAddress, recv_timeout=timeout, topics=[moData.topic()])
    this.subscribers.append(subscriber)
    logging.debug("startSubscriber: ", subscriber)
    return subscriber

def sendData(topic, key, value):
    tempStr = json.dumps({key:value})
    print("dataStr: ", tempStr)
    msg = topic + tempStr.encode()
    this.publisher.send(msg)
    print("pub: ", msg)
    
def sendKtype():
    sendData(this.topic_ktype, "kTypes", moData.kType.asArray())
    
def parseKtype(msg):
    print("parseKType: ", msg)

def sendEnviro():
    sendData(this.topic_enviro, "enviro", moData.enviro.asDict())
    
def parseEnvrio(msg):
    print("parseKType: ", msg)

def sendAllData():
    sendData(this.topic_allData, "allData", moData.asDict())
    
def parseAllData(msg):
    print("parseKType: ", msg)
    
def publish():
    logging.debug("publish - only AllData for now")
#    sendKtype()
#    sendEnviro()
    sendAllData()
    
def receive():
    for i in range(len(subscribers)):
        try:
            while(1): #stays here till timeout or receive
                msg = this.subscribers[i].recv()
                print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
                logging.info("sub %d rcv: %s"%(i,msg.decode()))  # prints b'wolf...' since that is the matching message
        except Timeout:
            logging.debug("receive timeout on subsciber %d"%(i))
        except :
            print("Some other exeption! on sub ", i)
            
