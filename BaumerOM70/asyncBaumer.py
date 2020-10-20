# Baumer OM-70 test using Trio Sockets
# default ip address is 198.162.0.250
# our rPi is on a dedicated switch on the 198.162.2.x network
# so that needs to be changed
#TODO also changed underlying OM70Datum into namedTuple, so more rework
import sys
this = sys.modules[__name__]
import signal
import trio
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from BaumerOM70 import OM70Datum

# address is set in web interface "Process Interface
port = 12345
baumer_udpAddr = ('', port) # accept any sending address

okToRun = True

async def baumerAsyncReceive():
    print("Begin receiveOm70Data ", baumer_udpAddr)
    try:
        # udp_sock = socket.socket(
        #     socket.AF_INET,  # IPv4
        #     socket.SOCK_DGRAM,  # UDP
        # )
        udp_sock = trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM)
        await udp_sock.bind(baumer_udpAddr)
    except:
        log.error("Exception caught creating socket: ", exc_info=True)
        return
    data = bytearray(OM70Datum.byteSize())
    buffSize = OM70Datum.byteSize()
    while okToRun:
        try:
            data, address = await udp_sock.recvfrom(buffSize)
            print("Received data from:", address)
            datum = OM70Datum.fromBuffer(data)
            print("  OM70 dist:", datum.distancemm())
            print("  OM70: ", datum)
            print("  OM70: ", datum.asJsonIndent())
        except trio.Cancelled:
            log.warning("***Trio Cancelled anotherTask")
            return
        except:
            log.error("Exception caught in Forever Loop: ", exc_info=True)
            break

async def anotherTask():
    print("Starting Another Task")
    count = 0
    while okToRun:
        print("Another Task here ", count)
        count += 1
        try:
            await trio.sleep(1)
        except trio.Cancelled:
            log.warning("***Trio Cancelled anotherTask")
            return

async def testBaumerReceive():
    print ("testSendRcv begin")
    moveonTime = 30
    async with trio.open_nursery() as nursery:
        # first we spawn the sender
        nursery.start_soon(baumerAsyncReceive)#, nursery)
        nursery.start_soon(anotherTask)#, nursery)
    print ("testSendRcv end")

if __name__ == "__main__":
    print("Test Baumer OM70 distance Sensor Trio Async")
    trio.run(testBaumerReceive)
