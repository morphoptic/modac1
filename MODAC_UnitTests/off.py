#!/usr/bin/python3 
from gpiozero import OutputDevice
from time import sleep
print("Turn all relays off")
sleepDelay = 0.01 # delay in seconds

# my setup has an IoT Relay power strip on GPIO 5
#    https://www.amazon.ca/Iot-Relay-Enclosed-High-power-Raspberry/dp/B00WV7GMA2
relay0 = OutputDevice(5,active_high=True)
# and an 8 relay board on these pins
#    https://www.amazon.ca/ELEGOO-Channel-Optocoupler-Arduino-Raspberry/dp/B06XCN5JNH
# note these relays are Active LOW and may turn on when power supplied to board
# and to pi initially as the gpio pins will be low initially
# running this script turns them off
#
# caveat: relays 6&7 on gpio 8/25 are shared with SPI
# these will be moved next hardware change
relay1 = OutputDevice(21,active_high=False)
relay2 = OutputDevice(20,active_high=False)
relay3 = OutputDevice(16,active_high=False)
relay4 = OutputDevice(12,active_high=False)
relay5 = OutputDevice(7,active_high=False)
relay6 = OutputDevice(8,active_high=False)
relay7 = OutputDevice(25,active_high=False)
relay8 = OutputDevice(24,active_high=False)
relay9 = OutputDevice(26,active_high=True) # Support Fan power outlet, active on True
relay10 = OutputDevice(19,active_high=True) # Exhaust Fan power outlet, active on True
relay11 = OutputDevice(13,active_high=True) # not used yet, active on True
relays = [
        relay0,
        relay1,
        relay2,
        relay3,
        relay4,
        relay5,
        relay6,
        relay7,
        relay8,
        relay9,
        relay10,
        relay11,
        ]
    
for relay in relays:
    relay.off()
#    sleep(sleepDelay)
    
print ("End of relayModuleOff")
    