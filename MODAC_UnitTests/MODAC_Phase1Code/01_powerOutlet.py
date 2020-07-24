#not really led but relay
import RPi.GPIO as GPIO     # Importing the GPIO library to use the GPIO pins of Raspberry pi
from time import sleep      # Importing the time library to provide the delays in program
outletPin = 5
GPIO.setmode(GPIO.BCM)      # Using BCM numbering
GPIO.setup(outletPin, GPIO.OUT) # Declaring the pin 21 as output pin
for x in range(5):             # Loop will run only five times
    GPIO.output(outletPin, True) # Turn LED ON
    print ('LED ON')
    sleep(2)                   # Delay of 1 sec
    GPIO.output(outletPin, False) # Turn LED OFF
    print('LED OFF')
    sleep(2)                    # Delay of 1 sec
    
GPIO.cleanup()                  # Making all the output pins LOW