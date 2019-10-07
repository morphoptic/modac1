# moNetwork - modac common networking methods and data
# IP addresses, encode/decode messages w/encryption etc

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

#import rest of modac
from .moKeys import *
from . import moData
# locally required for this module

# TODO: convert us from raw ip to a zeroConf address
__zConfigName = "modacServer.local"
__myIPAddress = 'tcp://127.0.0.1'
__pubAddress = None 
__cmdAddress = None

def initIPfromName():
    # insert zeroConfig stuff to get ip address
    # __zconfigName -> __myIPAddress
    # for now its pass thru
    pass

# these need to be visible by both sides of pubSub/Pair1
# note these specify protocol (TCP) in url address
def pubSubAddress():
    if this.__pubAddress == None:
        #initialize it
        initIPfromName()
        this.__pubAddress = this.__myIPAddress +':31313'
    return this.__pubAddress

def cmdAddress():
    if this.__cmdAddress == None:
        #initialize it
        initIPfromName()
        this.__cmdAddress = this.__myIPAddress +':21212'
    return this.__cmdAddress

# timeout for cmd recieve.  CmdListener loop delays any checks this long
def rcvTimeout():
    return 10

def sendTimeout():
    return 10

#################################
# parts for composing/decomposing network messages    
__topicDividerStr = '|'
__topicDivider = __topicDividerStr.encode('utf8')

def mergeTopicBody(key, value):
    #print("mergeTopicBody",key,value)
    tempStr = json.dumps(value)
    assert isinstance(tempStr, str)
    #print("value as str %s"%tempStr)
    msg = key + this.__topicDividerStr + tempStr
    #print("mergeTopicBody msg: ",msg)
    return msg
    
# def splitTopicBinary(msg):
#     #assert isinstance(msg, bytearray)
#     s = msg.decode('utf8')
#     rv = splitTopicStr(s)
#     return rv

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

# Encrypt/Decrypt for body of command messages
# Commands have clear text Topic (keyforModacCmd())
# while the body is Encrypted json pairing of cmd topic + body
# current hexlify is crude and forces us to do more to/from byteArray
# but for this iteration it is fine
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

def encryptCommand(cmd):
    log.info("encryptCommand cmd: %s"%cmd)
    #package up the envelope with topic
    encoded = modacEncrypt(cmd)
    msg = mergeTopicBody(keyForModacCmd(), encoded)
    log.info("encryptCommand msg: %s"%msg)
    # for testing
    #print("decypher test: ", decryptCommand(msg))
    return msg

def decryptCommand(cmdMsg):
    #msg should be string key|json
    # extract tuple (key, txt)
    # print("decryptCommand", cmdMsg)
    topic, body = splitTopicStr(cmdMsg)
    if not topic == keyForModacCmd():
        log.error("decryptCommand not = %s => %s",keyForModacCmd(),topic)
        # should not receive non cmd this is error
        return ("error", "notModacCmd")
    decrypted = modacDecrypt(body) #might throw exception if fails?
    #need to test if properly decrypted throw security exception
    cmd, value = splitTopicStr(decrypted)
    # print("Cmd %s Value ", cmd, value)
    rv = (cmd, value)
    # if isinstance(value, list):
    #     print("Value is list")
    #     print("v0", value[0])
    #     print("v1", value[1])
    return rv
    


if __name__ == "__main__":
    print("moNetwork has no self test")
    exit(0)
 