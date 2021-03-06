from gpiozero import OutputDevice
from time import sleep

sleepDelay = 0.5 # delay in seconds

relay1 = OutputDevice(21,active_high=False)
relay2 = OutputDevice(20,active_high=False)
relay3 = OutputDevice(16,active_high=False)
relay4 = OutputDevice(12,active_high=False)
relay5 = OutputDevice(7,active_high=False)
relay6 = OutputDevice(8,active_high=False)
relay7 = OutputDevice(25,active_high=False)
relay8 = OutputDevice(24,active_high=False)
relays = [relay1,relay2,relay3,relay4,relay5,relay6,relay7,relay8]

for index in range(len(relays)):    
    relays[index].on()
    sleep(sleepDelay)
    relays[index].off()
    sleep(sleepDelay)

for relay in relays:
    relay.on()
    sleep(sleepDelay)
    
for relay in relays:
    relay.off()
    sleep(sleepDelay)
    
print ("End of 02_relayModule unit test")
    