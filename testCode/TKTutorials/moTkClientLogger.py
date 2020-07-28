# moTkClientLogger - modac client msg/data logger with TK GUI
#

import datetime
from time import sleep
import sys
this = sys.modules[__name__]
import os
import argparse
import json

import tkinter as tk
from tkinter.ttk import *
from tkinter import scrolledtext
from tkinter import messagebox

# modac stuff
#from modac import moData, moClient, moLogger,moCSV
import logging
moLogger.init("netLogger")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

###############
# ugh globals
__killLoops = False


####
# first we build and show the UI
# later this gets encapsulated...
window = tk.Tk()  # could be root instead of window
window.geometry('600x400')
window.title("MODAC Data Logger")

def on_closing():

### some stand in gui elements
l1 = tk.Label(window, text="edureka!", font=("Arial Bold", 20) )
l1.grid(column=0, row=0)

txt = tk.Entry(window, width=10)
txt.grid(column=0, row=1)

def clicked():
    res = "Welcome to " + txt.get()
    l1.configure(text=res)

bt = tk.Button(window, text="Copy To Label",bg="orange", fg="green", command = clicked)
bt.grid(column=1, row=1)

combo = Combobox(window)
combo['values']= (1, 2, 3, 4, 5, "Text")
combo.current(5)
combo.grid(column=0, row=2)

stxt = scrolledtext.ScrolledText(window, width=20,height=10)
stxt.grid(column=0, row=5)
stxt.insert(tk.END,"This is\n the first\n text")

# simple version would stop here, using one or other technique here to show UI
#window.mainloop()
#while 1:
#    window.update()

##############################
# Trio stuff to wrap TK

async def asyncTkUpdate():
    tk.update() # TK runs thru its pending operations

async def tkUpdateLoop():
    while not this.__killLoops: # need a semiphore here
        await asyncTKUpdate()

async def start_TK_GUI(nursery):
    nursery.start_soon(tkUpdateLoop(),nursery)

##############################
# now the trio stuff for logging
# cp/pastes from modac_netLogger.py

async def modacStep():
    # wait for modac messages
    print("Modac Step")

async def modacLoop():
    while not this.__killLoops: # need a semiphore here
        log.debug("Start cmdListenLoop")
        try:
            retval = await this.modacStep()
        except trio.Cancelled:
            log.error("***modacLoop caught trioCancelled, exiting")
            break
        if not retval:
            this.__killLoops = True


async def start_modac_logger(nursery):
    nursery.start_soon(modacLoop, nursery)


##############################
# now the main loop stuff

while 1:
    window.update()

