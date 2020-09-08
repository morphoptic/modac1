#!/bin/sh -v
cd /home/pi/MODAC_Dev/
# need this to make pynng work
PYTHONUNBUFFERED=1;LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
sleep 3
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 /home/pi/MODAC_Dev/modacServer.py 

sleep 60