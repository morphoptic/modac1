from gpiozero import LED
from time import sleep

relay = LED(26)
while True:
    relay.on()
    sleep(1)
    relay.off()
    sleep(1)
