#!/usr/bin/python3

# Disto Laser Control With Bluez
# Author: Joshua Benjamin & Jackson 
# Written for Python 3.6 (But not really ~Ian)
#
# Dependencies:
# - You must install the pexpect library, typically with 'sudo pip install pexpect'.
# - You must have bluez installed and gatttool in your path 
# Get laser address from command parameters (sudo hciconfig lescan).

# Ian Cunnyngham, 2019
# - Gutted most of the code except initiation and main sensor read loop
# - Did a bunch of fixes to make the code actually work with python 3
# - Details about rpi setup in install/rpi_notes.txt

import struct
import sys
import time
from datetime import datetime
import argparse
from math import ceil
import signal

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import configLeica
addr = configLeica.leicaAddressStr
int_sec = 2

measure_dist = True
meas_str = ""
head_str = ""

# setup gattTool pexpect
meas_str+="_distance"
head_str+="\tdistance_meters"

import pexpect
print("spawn gattTool")
# Run gatttool interactively.
gatcmd = 'gatttool -b %s -t random -I' % addr
gatt = pexpect.spawn(gatcmd)

# Connect to the device.
gatt.sendline('connect')
gatt.expect('Connection successful', timeout=5)
print("connected")

time.sleep(1)

log.info('Leica connected')
print("enable indications")
# Enable Indications
# (Ian) Wish I knew what this did?
gatt.sendline('char-write-cmd 0x000b 0200')
gatt.sendline('char-write-cmd 0x000f 0200')
gatt.sendline('char-write-cmd 0x0012 0200')
time.sleep(1)

# Create a more graceful exit
def exit_gracefully(sig, frame):
    log.error(" SIGINT received, closing log file and exiting")
    f.close()
    sys.exit(0)
signal.signal(signal.SIGINT, exit_gracefully)


# Create output header
log.info("t_seconds_post_read"+head_str)

print("mainloop")
# Enter main loop.
i=0
t_0 = time.perf_counter()
while True:
    print("loop", i)
    try:
        gatt.sendline('char-write-cmd 0x0014 67')

        gatt.expect('handle = 0x000e value: ', timeout=1)
        gatt.expect('Indication')

        value = gatt.before

        # (Ian) Convert to bytes from hex, struct bs?   This is some serious BS right here! 
        distance = struct.unpack('<f', bytes.fromhex(''.join(value[:11].decode().split())) )[0]

    except pexpect.TIMEOUT:
        distance="READ_ERROR"
        #input("Leica read error.  Press Enter to resume measurements or CTRL+C to end")
        i = ceil( (time.perf_counter() - t_0)/int_sec ) 
    t_after = time.perf_counter()
    out = "%s" % (t_after-t_0, )
    out+= "\t%s" % (distance, )
    log.info(out)
    print(out)

    i+=1         
    sleep_time = (t_0 + i*int_sec - time.perf_counter())
    if sleep_time <= 0:                            
        i = ceil( (time.perf_counter() - t_0)/int_sec ) 
    else:                                          
        time.sleep(sleep_time)    
    
print("end")
# Maybe someday useful 
# (Ian) Instead a bunch of conditionals, build a lookup for units
#       Ultimately though, unit lookup seems broken and the leica returns meters in my tests
#       Disabled unit read in main loop, so should probably delete this.
# Units are returned as a hex value, starting as 0,1,2->e.  These are the units in order
#unit_lookup_list = [ "millimeters", "10th millimeter meters", "centimeters", "10th millimeter", "feet", "feet inch 1/32", "feet inch 1/16", "feet inch 1/8", "feet inch 1/4", "inch", "inch 1/32", "inch 1/16", "inch 1/8", "feet inch 1/4", "yard" ]
# This is a lookup dictionary that starts from the ascii character for '0' and goes to ascii chacter 'e'
#unit_lookup_dict = { ord('0')+i: v for i, v in enumerate(unit_lookup_list) }
#def lookup_unit(hex_ascii):
#    # Return "UNKNOWN_UNITS" if lookup fails
#    return unit_lookup_dict.get(hex_ascii, "UNKNOWN_UNITS")

    # Unit lookup in main loop
    #gatt.expect('handle = 0x0011 value:')
    #gatt.expect('\n')
    #unit = gatt.before
    #unit = unit.decode().replace(" ", "").encode()
    #u = unit[1]
    #unitText = lookup_unit(u)