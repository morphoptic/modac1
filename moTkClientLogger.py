# moTkClientLogger - modac client msg/data logger with TK GUI
#

import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
import signal
import datetime
from time import sleep
import os
import argparse
import json

from modac import moLogger

moLogger.init("moTKLogger")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


import tkinter as tk
from tkinter.ttk import *
from tkinter import scrolledtext
from tkinter import messagebox

import trio #adding async functions use the Trio package

# modac stuff
from modac import moData, moClient, moCSV

###############
# ugh globals
__killLoops = False


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        signalExit()
    pass

def clicked():
    res = "Welcome to " + txt.get()
    this.l1.configure(text=res)

def createTKWindow():
    ####
    # first we build and show the UI
    # later this gets encapsulated...
    this.window = tk.Tk()  # could be root instead of window
    this.window.protocol("WM_DELETE_WINDOW", on_closing)
    this.window.geometry('600x400')
    this.window.title("MODAC Data Logger")

    this.scrolledBox = scrolledtext.ScrolledText(this.window, width=80,height=40)
    this.scrolledBox.grid(column=0, row=0)
    this.scrolledBox.insert(tk.END,"This is\n the first\n text")

##############################
# Trio stuff to wrap TK into async

def updateFromMoData():
    moMsg = moData.asJson()
    this.scrolledBox.delete(1.0, tk.END)
    this.scrolledBox.insert(tk.END, moMsg)

async def tkAsyncLoop(receive_channel):
    count = 0
    while not this.__killLoops:  # need a semiphore here
        try:
            msg = receive_channel.receive_nowait()
            log.info("tkAsyncLoop received from modac " +msg)
            updateFromMoData()

        except trio.WouldBlock:
            #nothing to see here
            pass
        try:
            count += 1
            log.debug("try TK Update count %d"%(count))
            # await modac_asyncClientEventLoop()
            this.window.update()
        except trio.Cancelled:
            log.warning("***Trio propagated Cancelled to modac_asyncServer, time to die")
            this.__killLoops = True
            break;
        except:
            this.__killLoops = True
            log.error("Exception caught in the nursery loop: " + str(sys.exc_info()[0]))
            exc = traceback.format_exc()
            log.error("Traceback is: " + exc)
            # TODO need to handle Ctl-C on server better
            # trio has ways to catch it, then we need to properly shutdown spawns
            print("Exception somewhere in modac_io_server event loop.")
            print(exc)
            break
        await trio.sleep(0.1)


##############################

def log_data():
    log.info(moData.asJson())

async def modacAsyncLoop(sendChannel):
    log.info("Begin modacAsyncLoop")
    count = 0
    while not this.__killLoops: # need a semiphore here
        log.debug("top modacAsyncLoop")
        try:
            count += 1
            # wait for one receive or timeout
            log.debug("modacAsyncLoop receive count %d"%(count))
            rcvd = await moClient.asyncClientReceive()
            #client received something. log it?
            if rcvd == True:
                log_data()
                # maybe a semiphore to tell UI to update?
                msg = "modata updated %d"%(count)
                await sendChannel.send(msg)
            await trio.sleep(1)
        except trio.Cancelled:
            log.error("***modacLoop caught trioCancelled, exiting")
            this.__killLoops = True
            break # a bit redundant but ok
    log.info("End modacAsyncLoop")

def modacExit():
    log.info("modacExit")
    if moCSV.isOpen():
        moCSV.close()
    moClient.shutdownClient()

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    log.error("signal exit! someone hit ctrl-C?")
    this.__killLoops = True
    #this.window.destroy()
    modacExit()

async def modacTKClient():
    async with trio.open_nursery() as nursery:
        log.info("start with nursery")
        moData.setNursery(nursery)
        send_channel, receive_channel = trio.open_memory_channel(0)
        nursery.start_soon(modacAsyncLoop, send_channel)
        nursery.start_soon(tkAsyncLoop, receive_channel)
        log.info("end with nursery")

##############################
# now the main loop stuff
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalExit)
    moData.init()
    moClient.startClient()  # open the hailing frequencies
    createTKWindow()
    try:
        trio.run(modacTKClient)
    except trio.Cancelled:
        log.warning("Trio Cancelled - ending server")
    except Exception as e:
        print("Exception somewhere in modacTKClient. see log files")
        log.error("Exception happened", exc_info=True)
    finally:
        print("end main")
    moData.setNursery(None)
    log.debug("modac nursery try died");
    log.error("Exception happened?", exc_info=True)
    signalExit()

