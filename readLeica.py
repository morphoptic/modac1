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

leicaAddressStr = "D3:9D:70:68:8B:F2"

#parser = argparse.ArgumentParser()
#parser.add_argument("interval_seconds", type=float, 
#                    help="Interval between readings start.  If faster than sensors can go, just reads as fast as possible.")
#parser.add_argument("--disto", type=str,
#                    help="Bluetooth address of leica (Look for DISTO line in `sudo hcitool lescan`).  If ommitted, no temperature measured.")
#
#args = parser.parse_args()

int_sec = 2 #args.interval_seconds

measure_dist = True
#if args.disto is not None:
#    measure_dist = True
#    addr = args.disto
addr = leicaAddressStr
    
meas_str = ""
head_str = ""
if measure_dist:
    meas_str+="_distance"
    head_str+="\tdistance_meters"
    
    import pexpect
    
    # Run gatttool interactively.
    gatcmd = 'gatttool -b %s -t random -I' % addr
    gatt = pexpect.spawn(gatcmd)

    # Connect to the device.
    gatt.sendline('connect')
    gatt.expect('Connection successful', timeout=5)
    time.sleep(1)

    print('Leica connected ')
    print("gatt=",str(gatt))

    # Enable Indications
    # (Ian) Wish I knew what this did?
    gatt.sendline('char-write-cmd 0x000b 0200')
    gatt.sendline('char-write-cmd 0x000f 0200')
    gatt.sendline('char-write-cmd 0x0012 0200')
    time.sleep(1)
    print("gatt=",str(gatt))
    
# (Ian) Filename for now is just the date
date_str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
filename = "logs/%s%s.tsv" % (date_str, meas_str)
f = open(filename, "a")
print('Started logfile %s' % (filename))

# Create a more graceful exit
def exit_gracefully(sig, frame):
    print(" SIGINT received, closing log file and exiting")
    f.close()
    sys.exit(0)
signal.signal(signal.SIGINT, exit_gracefully)

# Simple logging function
def log(out):
    print(out)
    print(out, file=f)

# Create output header
log("t_seconds_post_read"+head_str)


# Enter main loop.
i=0
t_0 = time.perf_counter()
while True:
    if measure_dist:
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
    if measure_dist:
        out+= "\t%s" % (distance, )

    log(out)

    i+=1         
    sleep_time = (t_0 + i*int_sec - time.perf_counter())
    if sleep_time <= 0:                            
        i = ceil( (time.perf_counter() - t_0)/int_sec ) 
    else:                                          
        time.sleep(sleep_time)    
    