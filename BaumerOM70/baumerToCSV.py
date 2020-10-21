# Baumer OM-70 test using Trio Sockets
# default ip address is 198.162.0.250
# our rPi is on a dedicated switch on the 198.162.2.x network
# so that needs to be changed
import sys
this = sys.modules[__name__]
import socket
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import struct
import signal
import datetime

if __name__ == "__main__":
    import OM70Datum
else:
    from . import OM70Datum


# address is set in web interface "Process Interface
port = 12345
baumer_udpAddr = ('', port) # accept any sending address

__runable = True
def signalExit(*args):
    __runable = False
    print("caught ctrlC end loop")

def packetLittleVsBigEndian(data):
    """unpack and show first int32 as little and big endian"""
    print("Packet", data)
    idLittle = struct.unpack('<I',data[0:4])
    idBig = struct.unpack('>I',data[0:4])
    print("   ID as little/big:", idLittle, idBig)

def receiveOm70Data():
    print("Begin receiveOm70Data ", baumer_udpAddr)
    t = datetime.datetime.now()
    name = t.strftime("om70_%H_%M_%S.csv")
    f = open(name, 'w')
    try:
        # udp_sock = socket.socket(
        #     socket.AF_INET,  # IPv4
        #     socket.SOCK_DGRAM,  # UDP
        # )
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(baumer_udpAddr)
    except:
        log.error("Exception caught creating socket: ", exc_info=True)
        return
    data = bytearray(OM70Datum.byteSize())
    buffSize = OM70Datum.byteSize()
    while __runable:
        # recvfrom
        try:
            data, address = udp_sock.recvfrom(buffSize)
            #print("Received data from:", address)
            #print("  raw:", data)
            #packetLittleVsBigEndian(data)
            datum = OM70Datum.fromBuffer(data)
            print("  OM70 dist:", datum.distancemm())
            #print("  OM70: ", datum)
            #print("  OM70: ", datum.asJsonIndent())
            dist = datum[OM70Datum.DISTANCEMM_IDX]
            t = datetime.datetime.now()
            time = t.strftime("%H:%M:%S.%f")
            print(time,dist, file= f)
            f.flush()
        except:
            log.error("Exception caught in Forever Loop: ", exc_info=True)
            break
    print("End receiveOm70Data")
    f.close()


if __name__ == "__main__":
    print("Receive Client for Baumer OM70 distance Sensor")
    signal.signal(signal.SIGINT, signalExit)
    receiveOm70Data()
