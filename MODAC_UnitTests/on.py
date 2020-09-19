#!/usr/bin/python3 
from gpiozero import OutputDevice
from time import sleep
print("MODAC turn all relays ON")
sleepDelay = 0.01 # delay in seconds

relay0 = OutputDevice(5,active_high=True)
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
    relay.on()
    sleep(sleepDelay)
    
sleep(10)
#    
print ("End of relayModuleOn")
    