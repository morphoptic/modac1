# Baumer OM-70 test saving data as CSV
# our rPi is on a dedicated switch on the 198.162.2.x network
# so that needs to be changed
import sys
this = sys.modules[__name__]
import socket
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import signal
import datetime
import csv

if __name__ == "__main__":
    import OM70Datum
else:
    from . import OM70Datum

class MovingAverage:
    """simple fast class to calculate moving average on the fly"""
    # retaining self.sum avoids re-traversing values list every time
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
        self.sum = 0.0

    def update(self, value):
        self.values.append(value)
        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
        return float(self.sum) / len(self.values)

# address is set in web interface "Process Interface
port = 12345
baumer_udpAddr = ('', port) # accept any sending address

__runable = True
movAvgWindow = 100
onCount = True  # print only when count == movAvgWindow; false= print every read
hours  = 2

def signalExit(*args):
    this.__runable = False
    print("caught ctrlC end loop")

def receiveOm70Data():
    print("Begin receiveOm70Data ", baumer_udpAddr)
    movingAvg = MovingAverage(movAvgWindow)
    startTime = datetime.datetime.now()
    name = startTime.strftime("om70_%H_%M_%S.csv")
    f = open(name, 'w', newline='')
    csvfile = csv.writer(f)
    headerRow = ("dateTime", "M_Avg_"+str(movAvgWindow)) + OM70Datum.names()
    csvfile.writerow(headerRow)
    # datum = OM70Datum.makeRandomOm70()
    # row = [name, 100.0, *datum]
    # csvfile.writerow(row)
    # csvfile.writerow(row)
    # f.close()
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(10.0)
        udp_sock.bind(baumer_udpAddr)
    except:
        log.error("Exception caught creating socket: ", exc_info=True)
        return
    data = bytearray(OM70Datum.byteSize())
    buffSize = OM70Datum.byteSize()
    count = 0
    while this.__runable:
        # recvfrom
        try:
            data, address = udp_sock.recvfrom(buffSize)
            datum = OM70Datum.fromBuffer(data)
            ma = movingAvg.update(datum[OM70Datum.DISTANCEMM_IDX])
            count += 1
            if (onCount and count == movAvgWindow) or not onCount:
                now = datetime.datetime.now()
                time = now.strftime("%H:%M:%S.%f")
                row = [time, ma, *datum]
                print(row)
                csvfile.writerow(row)
                f.flush()
                count = 0
                elapsedTime = now - startTime
                if elapsedTime.total_seconds()/3600 > hours:
                    # stop after an hour of data collection
                    break
        except socket.timeout:
            print("Timeout on socket")
        except:
            log.error("Exception caught in Forever Loop: ", exc_info=True)
            break
    print("End receiveOm70Data")
    f.close()


if __name__ == "__main__":
    print("Receive Client for Baumer OM70 distance Sensor")
    signal.signal(signal.SIGINT, signalExit)
    receiveOm70Data()
