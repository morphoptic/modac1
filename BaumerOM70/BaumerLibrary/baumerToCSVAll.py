# Baumer OM-70 test saving data as CSV
# our rPi is on a dedicated switch on the 198.162.2.x network
# so that needs to be changed
import sys
this = sys.modules[__name__]
import socket
import logging, logging.handlers
import signal
import datetime
import csv
from math import isnan

if __name__ == "__main__":
    import OM70Datum
else:
    from BaumerOM70 import OM70Datum

def logInit(name, level = logging.INFO):
    maxLogSize = (1024 * 1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = name + nowStr + ".log"
    logFormatStr = "%(asctime)s [%(threadName)-12.12s] [%(name)s %(funcName)s %(lineno)d] [%(levelname)-5.5s] %(message)s"
    # setup base level logging to stderr (console?)

    print("print Logging to stderr and " + logName)

    logging.basicConfig(stream=sys.stderr, level=level, format=logFormatStr)
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(logFormatStr)

    # chain rotating file handler so logs go to stderr as well as logName file
    fileHandler = logging.handlers.RotatingFileHandler(logName, maxBytes=maxLogSize, backupCount=100)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    logging.captureWarnings(True)
    logging.info("Logging Initialized")

logInit("BaumerCSV_")
log = logging.getLogger(__name__)

__MovingAvgWindow = 100

class MovingAverage:
    """simple fast class to calculate moving average on the fly"""
    # retaining self.sum avoids re-traversing values list every time
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
        self.sum = 0.0

    def update(self, value):
        if isnan(value) :
            log.warning("NAN received in MovingAverage")
            return self.latest
        self.values.append(value)
        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
        return float(self.sum) / len(self.values)

# address is set in web interface "Process Interface
port = 12345
baumer_udpAddr = ('', port) # accept any sending address

__runable = True
onCount = False # True  # print only when count == movAvgWindow; false= print every read
hours  = 8  # stop after this many hours, or ctrl c

udp_sock = None

def doExit():
    this.udp_sock.close()
    this.__runable = False

def signalExit(*args):
    print("caught ctrlC end loop")
    this.__runable = False

def receiveOm70Data():
    print("Begin receiveOm70Data ", baumer_udpAddr)
    movingAvg = MovingAverage(__MovingAvgWindow)
    startTime = datetime.datetime.now()
    name = startTime.strftime("om70_%m%d_%H_%M_%S.csv")
    f = open(name, 'w', newline='')
    csvfile = csv.writer(f)
    headerRow = ("Date","Time", "M_Avg_"+str(__MovingAvgWindow)) + OM70Datum.names()
    csvfile.writerow(headerRow)
    try:
        this.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        this.udp_sock.settimeout(10.0)
        this.udp_sock.bind(baumer_udpAddr)
    except:
        log.error("Exception caught creating socket: ", exc_info=True)
        return
    data = bytearray(OM70Datum.byteSize())
    buffSize = OM70Datum.byteSize()
    count = 0
    while this.__runable:
        try:
            data, address = this.udp_sock.recvfrom(buffSize)
            datum = OM70Datum.fromBuffer(data)
            ma = movingAvg.update(datum[OM70Datum.DISTANCEMM_IDX])
            count += 1
            if (onCount and count == __MovingAvgWindow) or not onCount:
                now = datetime.datetime.now()
                date = now.strftime("%Y-%m-%d")
                time = now.strftime("%H:%M:%S.%f")
                row = [date, time, ma, *datum]
                print(row)
                csvfile.writerow(row)
                f.flush()
                count = 0
                elapsedTime = now - startTime
                if elapsedTime.total_seconds()/3600 > hours:
                    # stop after an hour of data collection
                    this.__runable = False
                    break
        except socket.timeout:
            log.info("Timeout waiting on Baumer")
        except:
            log.error("Exception caught in Forever Loop: ", exc_info=True)
            break
    log.info("End receiveOm70Data")
    f.close()
    doExit()



if __name__ == "__main__":
    print("Receive Client for Baumer OM70 distance Sensor")
    signal.signal(signal.SIGINT, signalExit)
    receiveOm70Data()
