# trio2Sensors: testing Trio w AD16 and BME280 sensors in diff threads
# create two 'threads', one to read AD16, one to read bme280. spawn them with 10 sec delays
# uses local versions of sensors and logger
# should be easy to swap in different sensors that maintain the init/update/shutdowm interface
# update here is simply to log.info() current data values
# Primary purpose is to see if i2c conflicts are happening with bme280 & ad16/ads1115 code

import sys
this = sys.modules[__name__]

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import trio #adding async functions use the Trio package

import myLogger

# import as should allow us to hide all the sensor details as long as they init/update/shutdown
import bme280 as sensor1
import ads1115_AF as sensor2

okToRunMainLoop = False
# use same/different read rates for testing
sensor1ReadRate = 10
sensor2ReadRate = 5

def sensor1Init():
    sensor1.init()

async def sensor1Loop():
    log.info("Sensor1 Loop Begins")
    while this.okToRunMainLoop: # hopefully CtrlC will kill it
        sensor1.update()
        try:
            await trio.sleep(this.sensor1ReadRate)
        except trio.Cancelled:
            log.warning("***Trio Cancelled caught in Sensor1 Loop")
            break

    log.info("Sensor1 Loop Ending")

def sensor2Init():
    sensor2.init()

async def sensor2Loop():
    log.info("Sensor2 Loop Begins")
    while this.okToRunMainLoop: # hopefully CtrlC will kill it
        sensor2.update()
	try:
            await trio.sleep(this.sensor2ReadRate)
        except trio.Cancelled:
            log.warning("***Trio Cancelled caught in Sensor2 Loop")
            break
    log.info("Sensor2 Loop Ending")

async def initSensors():
    sensor1Init()
    sensor2Init()

def doExit():
    sensor1.shutdown()
    sensor2.shutdown()
    exit(0)

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    log.error("signal exit! someone hit ctrl-C?")
    doExit()


async def asyncMainLoop():
    # await trio.sleep(2)
    log.info("start asyncMainLoop()")

    await initSensors()

    # Trio is our async multi-threaded system.
    # it uses the Nursery metaphor for spawning and controlling
    async with trio.open_nursery() as nursery:
        this.okToRunMainLoop = True
        log.info("Nursery Open, start async sensor loops")
        nursery.start_soon(sensor1Loop)
        nursery.start_soon(sensor1Loop)
    log.info("End asyncMainLoop()")


if __name__ == "__main__":
    myLogger.init()  # start logging (could use cmd line args config files)
    log.info("that may be the 2nd logger init. not a problem")
    signal.signal(signal.SIGINT, signalExit)
    time.sleep(1)
    try:
        trio.run(asyncMainLoop)
    except trio.Cancelled:
        log.warning("Trio Cancelled - ending server")
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        log.error("Exception happened", exc_info=True)
    finally:
        print("end main")
