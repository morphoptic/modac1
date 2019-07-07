# MODAC Test OLED + BME280
# displays CPU Stats and Ambient Env on OLED display
#
# portions derived from stats.py from Adafruit_PythonSSD1306 Example stats.py
# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import datetime
import bme280
import smbus2
from time import sleep

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

#######################
print ("OLED/BME280 Test")
i2cport = 1 
bme280Address = 0x77 # Adafruit BME280 address. Other BME280s may be different
i2cbus = smbus2.SMBus(i2cport)
calibration_params = bme280.load_calibration_params(i2cbus,bme280Address)
#sleep(1)
bme280_data = bme280.sample(i2cbus,bme280Address)
print (bme280_data)

#######################
#def oledSetup():  too many globals for function at present
# Raspberry Pi pin configuration:
OLED_RST = 4     # on the PiOLED this pin isnt used

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=OLED_RST, i2c_address=0x3D)
# Initialize library.
disp.begin()
print("disp.begin()")

# Clear display.
disp.clear()
disp.display()
print("disp.clear()")

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
print("Display w: ", width, "Height: ", height)

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)
print("disp.draw rectangle()")

# Load default font.
font = ImageFont.load_default()
#  define some constants for draw.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 2
#######################

print("start forever loop")

lineHeight = 9
while True:
    bme280_data = bme280.sample(i2cbus,bme280Address)
    hStr = 'Humidity:  %0.3f %%rH'% bme280_data.humidity
    tStr = 'Temp:      %0.3f °C'%bme280_data.temperature
    pStr = 'Pressure: %0.3f hPa'% bme280_data.pressure
    print(hStr)
    print(tStr)
    print(pStr)
    
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((x, top+8),   hStr,  font=font, fill=255)
    draw.text((x, top+16),  tStr,  font=font, fill=255)
    draw.text((x, top+25),  pStr,  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(1)

