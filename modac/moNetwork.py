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

address = 'tcp://127.0.0.1:31313'

# pub sub messages
pub = None
sub0 = None
sub1 = None
sub2 = None
sub3 = None
subscribers = []

# msg topics
topic_ktype = moData.kType.topic() #b'ktype'
topic_enviro = moData.enviro.topic() # b'enviro'
topic_rawA = moData.ad24.topicRaw() #b'rawA'
topic_5vA = moData.ad24.topicVv05() #b'5vA'
topic_ad24 = moData.ad24.topic()
topic_allData = moData.topic() #b'allData' 

def init():
    startPubSub()
    
def startPubSub():
    logging.debug("startPubSub")
    this.pub = Pub0(listen=this.address)
    timeout = 100
    this.sub0 = Sub0(dial=this.address, recv_timeout=timeout, topics=[this.topic_ktype])
    this.subscribers.append(this.sub0)
    this.sub1 = Sub0(dial=this.this.address, recv_timeout=timeout, topics=[this.topic_enviro])
    this.subscribers.append(sub1)
    this.sub2 = Sub0(dial=this.address, recv_timeout=timeout, topics=[this.topic_ktype,this.topic_enviro])
    this.subscribers.append(this.sub2)
    this.sub3 = Sub0(dial=this.address, recv_timeout=timeout, topics=[this.topic_allData])
    this.subscribers.append(this.sub3)

def sendData(topic, key, value):
    tempStr = json.dumps({key:value})
    print("dataStr: ", tempStr)
    msg = topic + tempStr.encode()
    this.pub.send(msg)
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
    logging.debug("publish")
    sendKtype()
    sendEnviro()
    sendAllData()
    
def receive():
    global subscribers
    for i in range(len(subscribers)):
        try:
            while(1):
                msg = subscribers[i].recv()
                print("sub %d rcv:"%(i),msg)  # prints b'wolf...' since that is the matching message
        except Timeout:
            print('timeout on ', i)
        except :
            print("Some other exeption! on sub ", i)
            
