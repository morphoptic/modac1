# Disto Laser Control With Bluez
# Author: Joshua Benjamin & Jackson 
# Written for Python 3.6
#
# Dependencies:
# - You must install the pexpect library, typically with 'sudo pip install pexpect'.
# - You must have bluez installed and gatttool in your path (copy it from the
#   attrib directory after building bluez into the /usr/bin/ location).
#

import struct

import sys

import time

from datetime import datetime

import pexpect

import configLeica

addr = configLeica.leicaAddressStr

SLEEP_SEC = 2

if SLEEP_SEC < 2:
    print('Time_Interval_Sec must be >= 2')
    sys.exit(1)

now = datetime.now()
print('Note: Given measurement units signify most significant unit.')
# Run gatttool interactively.

gatcmd = 'gatttool -b %s -t random -I' % addr
gatt = pexpect.spawn(gatcmd)

# Connect to the device.
try:
    gatt.sendline('connect')
    gatt.expect('Connection successful', timeout=5)#120)
    print('Connected')
except pexpect.TIMEOUT:
    print("timeout starting uflLeica")
    exit(0)
    
# Enable Indications
gatt.sendline('char-write-cmd 0x000b 0200')
gatt.sendline('char-write-cmd 0x000f 0200')
gatt.sendline('char-write-cmd 0x0012 0200')

print('Indications Enabled')
tim = 3
print('Starting Measurements')

print('Date, Time, Measurement, Unit, DateTime (Use for Spreadsheet Analysis)')
# Enter main loop.

while True:
    # Take Measurement
    now = datetime.now()
    print("get data at", now)
    gatt.sendline('char-write-cmd 0x0014 67')
    gatt.expect('handle = 0x000e value: ')
    gatt.expect('Indication')

    bvalue = gatt.before
    print(bvalue)
    svalue = bvalue.decode()
    value = svalue.replace(" ", "")
    value = value.encode()
    value = value[:8]
    a = [value[6], value[7], value[4], value[5], value[2], value[3], value[0], value[1]]

    value = ''.join(a)

    number = struct.unpack('!f', value.decode('hex'))[0]
    gatt.expect('handle = 0x0011 value:')
    gatt.expect('\n')
    unit = gatt.before
    unit = unit.replace(" ", "")
    u = unit[1]
    unitText = "UNKNOWN_UNITS"
    if u == '0':
        unitText = "millimeters"
    elif u == '1':
        unitText = "10th millimeter meters"
    elif u == '2':
        unitText = "centimeters"
    elif u == '3':
        unitText = "10th millimeter"
    elif u == '4':
        unitText = "feet"
    elif u == '5':
        unitText = "feet inch 1/32"
    elif u == '6':
        unitText = "feet inch 1/16"
    elif u == '7':
        unitText = "feet inch 1/8"
    elif u == '8':
        unitText = "feet inch 1/4"
    elif u == '9':
        unitText = "inch"
    elif u == 'a':
        unitText = "inch 1/32"
    elif u == 'b':
        unitText = "inch 1/16"
    elif u == 'c':
        unitText = "inch 1/8"
    elif u == 'd':
        unitText = "feet inch 1/4"
    elif u == 'e':
        unitText = "yard"

    print('%s/%s/%s, %s:%s:%s, %f, %s, %s/%s/%s %s:%s:%s' % (
        now.month, now.day, now.year, now.hour, now.minute, now.second, number, unitText, now.month, now.day, now.year,
        now.hour, now.minute, now.second))
    time.sleep(2)

