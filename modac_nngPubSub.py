# modac_io_server v0
import datetime
from time import sleep
import sys
import os
import logging, logging.handlers
import argparse
import gpiozero
import json

# my stuff
import modac_OutputDevices
import modac_BME280
import modac_AD24Bit
import modac_ktype

from pynng import Pub0, Sub0, Timeout


loggerInit = False
runTests = False #True
address = 'tcp://127.0.0.1:31313'

pub = None
sub0 = None
sub1 = None
sub2 = None
sub3 = None
subscribers = []

# msg topics
topic_ktype = b'ktype'
topic_bme = b'bme'
topic_rawA = b'rawA'
topic_5vA = b'5vA'
topic_modac = b'modac' 

def startPubSub():
    global pub, sub0, sub1, sub2, sub3, subscribers
    logging.debug("startPubSub")
    pub = Pub0(listen=address)
    timeout = 100
    sub0 = Sub0(dial=address, recv_timeout=timeout, topics=[topic_ktype])
    subscribers.append(sub0)
    sub1 = Sub0(dial=address, recv_timeout=timeout, topics=[topic_bme])
    subscribers.append(sub1)
    sub2 = Sub0(dial=address, recv_timeout=timeout, topics=[topic_ktype,topic_bme])
    subscribers.append(sub2)
    sub3 = Sub0(dial=address, recv_timeout=timeout, topics=[topic_modac])
    subscribers.append(sub3)

def sendKtype():
    global topic_ktype, pub, ktypeData
    tempStr = json.dumps({"kTypes":ktypeData})
    print("tempStr for kType:",tempStr)
    msg = topic_ktype +tempStr.encode()
    pub.send(msg)
    print("pub: ",msg)
    
def parseKtype(msg):
    print("parseKType: ", msg)

def sendBme():
    global topic_bme, pub, bme_data
    tempStr = json.dumps({"bme":bme_data})
    msg = topic_bme +tempStr.encode()
    pub.send(msg)
    print("pub: ",msg)
    
def parseBme(msg):
    print("parseKType: ", msg)

def sendModac():
    global topic_ktype, pub, inputData
    tempStr = json.dumps(inputData)
    msg = topic_modac + tempStr.encode()
    pub.send(msg)
    print("pub: ",msg)
    
def parseModac(msg):
    print("parseKType: ", msg)
    
def publish():
    logging.debug("publish")
    sendKtype()
    sendBme()
    sendModac()

def modac_exit():
    logging.info("modac_exit")
    #gpioZero takes care of this: GPIO.cleanup()
    # anything else?
    exit()
    
def modac_testLogging():
    for i in range(100):
        #print(i)
        logging.info("I is now %s",i)
        sleep(0.05)

__kTypeIdx= [4,5,6] #indexs into AD24Bit array for k-type thermocouple

bme_data ={}
ad24Data =[]
ktypeData = []
inputData = {}

def modac_getInputs():
    global __kTypeIdx, bme_data, ad24Data, temps, ktypeData
    bme_data = modac_BME280.getDataAsDict()
    ad24Data = modac_AD24Bit.getAll0To5()
    ktypeData = []
    roomTemp = modac_BME280.temperature()
    for i in __kTypeIdx:
        t = modac_ktype.mVToC(ad24Data[i],roomTemp)
        #print("ktype", i, t)
        ktypeData.append(t)
    moData = {"bme":bme_data, "ad24":ad24Data, "kTypes":ktypeData}    
    return moData
    
#def testBME280():
#    logging.info("test BME temp, pressure, humidity sensor")
#    print("test BME temp, pressure, humidity sensor")
#    for i in range(0,60):
#        modac_BME280.update()
#        hStr = 'Humidity: %0.3f %%rH '% modac_BME280.humidity()
#        tStr = 'Temp: %0.3f °C '% modac_BME280.temperature()
#        pStr = 'Pressure: %0.3f hPa' % modac_BME280.pressure()
#        timeStr = timestamp().strftime("%Y-%m-%d %H:%M:%S.%f%Z : ")
#        msg = timeStr + hStr+tStr+pStr
#        print(msg)
#        logging.info(msg)
#        #print("alt :", bme)
#        sleep(1)


def handleSubscriptions():
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

def modac_eventLoop():
    global inputData
    global subscribers

    print("event Loop")
    print(subscribers)
    logging.info("Enter Event Loop")
    for i in range(30):
        #update inputs
        modac_BME280.update()
        modac_AD24Bit.update()
        inputData = modac_getInputs()
        # output
        #test_json(inputData)
        publish()
        handleSubscriptions()        
        sleep(2)

def test_json(inputData):
    print("------------ write JSON File modacData.json --------")
    with open("modacData.json",'w') as jsonFile:
        json.dump(inputData, jsonFile, indent=4)
        
    print("------------ read JSON File modacData --------")
    with open("modacData.json",'r') as jsonFile:
        data = json.load(jsonFile)
        print("Read: ", data)
        print("asJson: ", json.dumps(data, indent=4))

def log_data(inputData):
    print("moData:",inputData)
    print(json.dumps(inputData, indent=4))
    
def modac_io_server():
    logging.info("start modac_io_server()")
    # modac_testLogging()
    # load config files
    modac_loadConfig()
    # argparse ? use to override config files
    modac_argDispatch()
    # initialize data structures
    # initialize GPIO channels
    modac_initHardware()
    startPubSub()
    # run hardware tests
    # initialize message passing, network & threads
    try:
        #   run event loop
        modac_eventLoop()
    except Exception as e:
        print("Exception somewhere in modac_io_server event loop. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("Exception Happened")
    
    modac_exit()
    
__modac_argparse = argparse.ArgumentParser()
__modac_args = None

def modac_initHardware():
    """ modac_initHardware: Initialize Hardware Drivers based on config structures and hard coded stuff,"""
    logging.info("modac_initHardware")
    # init digital I/O
    modac_OutputDevices.outputDevice_init()
    # init SPI 1&2 (AD/DA HAT)
    # init I2C
    #    BME280
    modac_BME280.init()
    #    not oled, that is other tool
    # modac_BLE_Laser.init()
    modac_AD24Bit.init()
    
def modac_argparse():
    """ parse command line arguments into global __modac_args """
    #logging.info("modac_argparse")
    # add command line arg definitions here
    # then call the parser to shift them into modac_args for later routines.
    __modac_args = __modac_argparse.parse_args()

def modac_argDispatch():
    logging.info("modac_argDispatch")
    # assumes config files & structures are loaded
    # dispatches actions requested by

def modac_loadConfig():
    logging.info("modac_loadConfig")

def setupLogging():
    global loggerInit
    print("setupLogging")
    if loggerInit :
        logging.warn("Duplicate call to setupLogging()")
        return
    maxLogSize = (1024 *1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = "modac_"+nowStr+".log"
    logFormatStr = "%(asctime)s [%(threadName)-12.12s] [%(name)s] [%(levelname)-5.5s] %(message)s"
    # setup base level logging to stderr (console?)
    # consider using logging.config.fileConfig()
    # consider using log directory ./log
    logDirName = os.path.join(os.getcwd(),"logs")
    if os.path.exists(logDirName) == False:
        os.mkdir(logDirName)
        
    logName = os.path.join(logDirName, logName)
    print("print Logging to stderr and " + logName)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    rootLogger = logging.getLogger()
    
    logFormatter = logging.Formatter(logFormatStr)
    #consoleHandler = logging.StreamHandler()
    #consoleHandler.setFormatter(logFormatter)
    #rootLogger.addHandler(consoleHandler);
    # chain rotating file handler so logs go to stderr as well as logName file
    fileHandler = logging.handlers.RotatingFileHandler(logName, maxBytes=maxLogSize, backupCount=10)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    
    logging.captureWarnings(True)
    logging.info("Logging Initialized")
    print("Logging Initialized? should have echo'd on line above")
    loggerInit = True
    
  
if __name__ == "__main__":
    modac_argparse() # capture cmd line args to modac_args dictionary for others
    setupLogging() # start logging (could use cmd line args config files)
    print("modac_nngPubSub testing nng publish-subscribe")
    try:
        modac_io_server()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main")
    modac_exit()
    

