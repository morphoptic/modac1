#Morph Optics Data Acquistion (MODAC) Unit Tests
This folder holds python tools for testing MODAC components

blinkgpio26: use gpio to toggle #26 (led or relay) - connected to relay power strip
blinkgpio26: use gpiozero to toggle #26 (led or relay)
bme280:
    tests for the Adafruit BME280 temperature humidity pressure sensor
    tmp102: quick try using sparkfun outdated article, didnt work so rest are Adafruit
    base tests on Adafruit bme280 circuitPython class (wraps i2c)
    need to dig to find out which i2c that is based on so all compatible
    bme280TestLoop: basic read/print forever
    moBME280 is MorphOptic BME class, wraps Adafruit
    bme280Plot are tests with MatPlotLib graphing  _RT2 is latest
oldTests:
    MatPlotLib - simple plotting tests
OLED - several tests showing OLED displays data from BME280
relayModuleTest : exercises 8 discrete GPIO relays

LTC2499: trying to get AD to respond/work
    (note) tried on arduino and it isnt working there either
    
ADS1115 - alternative i2c AD
    https://circuitpython.readthedocs.io/projects/ads1x15/en/latest/
    sudo pip3 install adafruit-circuitpython-ads1x15
