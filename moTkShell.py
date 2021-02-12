# moTkShell - modac TK GUI Shell - prototype for other tools using
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

from modac import moLogger, moKeys

moLogger.init("moTkGui")
log = logging.getLogger("moTKShell"+__name__)
log.setLevel(logging.DEBUG)

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

import trio #adding async functions use the Trio package

# modac stuff
from modac import moData, moClient, moCSV
from moTkGui.moTKWindow import moTkWindow
from moTkGui.moTabAllData import moTabAllData
from moTkGui.moTabKiln import moTabKiln
from moTkGui.moPanelTempPlot import moPanelTempPlot
from moTkGui.moTabDistances import moTabDistances
from moTkGui.moTkShared import *

###############
# ugh globals
__killLoops = False

def on_closing():
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    #    signalExit()
    signalExit()
    pass

def createTKWindow():
    log.debug("createTKWindow()")
    ####
    # first we build and show the UI
    # Basic Mo Menu
    # Modac Top/Bottom Status Bars
    # Tabbed Notebook in middle
    # moTKWindow takes care of those basics
    this.moWindow = moTkWindow(title="moTKShell", closeMethod=on_closing)

    #simple empty tab with no Modac connections
    #tab1 = tk.Frame(this.moWindow.notebook(), bg="red")
    #this.moWindow.addTab(tab1,frameTitle="Tab1")

    # tempDistFrame = tk.Frame(this.moWindow.notebook(), bg="green")
    # this.TempDistTab = moPanelTempPlot(tempDistFrame)
    # this.moWindow.addTab(tempDistFrame,moObject=this.TempDistTab)

    kilnFrame = tk.Frame(this.moWindow.notebook(), bg="blue")
    this.kilnTab = moTabKiln(kilnFrame)
    this.moWindow.addTab(kilnFrame, moObject=this.kilnTab)

    allDataFrame = tk.Frame(this.moWindow.notebook(), bg="cyan")
    this.allDataTab = moTabAllData(allDataFrame)
    this.moWindow.addTab(allDataFrame, moObject=this.allDataTab, frameTitle="AllData")

    distanceFrame = tk.Frame(this.moWindow.notebook(), bg="cyan")
    this.distanceTab = moTabDistances(distanceFrame)
    this.moWindow.addTab(distanceFrame, moObject=this.distanceTab, frameTitle="Distances")

    log.debug("createTKWindow() end")

##############################
# Trio stuff to wrap TK into async; vs using tkroot.mainloop()

async def tkAsyncLoop(receive_channel):
    ### coRoutine to update from data
    # takes place of normal TK update loop but for use within Trio
    count = 0
    log.debug("Start tkAsyncLoop")
    #updateFromMoData()
    while not this.__killLoops:
        #log.debug("Top tkAsyncLoop")
        try: # msg from modac -> gtk ?
            # nowait means it will throw a trio.WouldBlock if no data on channel
            msg = receive_channel.receive_nowait()
            # TODO: handle message contents; if got here, then something happened in moClient
            log.info("tkAsyncLoop received from modac " +msg)
            # usually (originally) it means data came in, so update windows from moData
            this.moWindow.updateFromMoData()
        except trio.WouldBlock:
            # nothing to see here; no updates from modac yet
            # so fall thru to the next part
            pass
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

        # now try graphic update; basically what TK mainloop would do
        try:
            count += 1
            #log.debug("try TK Update count %d"%(count))
            # await modac_asyncClientEventLoop()
            this.moWindow.root().update()
        except trio.Cancelled:
            log.warning("***Trio propagated Cancelled to modac_asyncServer, time to die")
            this.__killLoops = True
            break;
        except:
            this.__killLoops = True
            log.error("Exception caught in the nursery loop: " + str(sys.exc_info()[0]))
            exc = traceback.format_exc()
            log.error("Traceback is: " + exc)
            # TODO need to handle Ctl-C on server better?
            # trio has ways to catch it, then we need to properly shutdown spawns
            print("Exception somewhere in modac_io_server event loop.")
            print(exc)
            break
        await trio.sleep(0.1)
    log.debug("End tkAsyncLoop")

##############################

def log_data():
    log.info("moData.asJson:"+moData.asJson())

async def modacAsyncLoop(sendChannel):
    ### coRoutine to read from Modac Server and pass data to UI routine
    log.info("Begin modacAsyncLoop")
    count = 0
    while not this.__killLoops:
        #log.debug("top modacAsyncLoop")
        try:
            count += 1
            # wait for one receive or timeout
            #log.debug("modacAsyncLoop receive count %d"%(count))
            rcvd = await moClient.asyncClientReceive()
            # TODO rcvd is now an array of [(i,T/F, topic, extra)]
            log.debug ("asyncClientReceive returned:"+str(rcvd))

            for subcriptionResp in rcvd:
                #client received something. log it?
                log.debug ("response "+str(subcriptionResp))
                # two or more fields in subcriptionResp
                # first is subscription number
                # second is boolean if got pyNNG msg
                # third is topic of msg, or key for why returned w/o data
                if subcriptionResp[1] == True:
                    log_data()
                    # memoryChannel to tell UI thread to update from moData
                    msg = "modata updated %d"%(count)
                    await sendChannel.send(msg)
                # TODO else deal with timeout, repeated timeouts cause error/restart
                else:
                    log.debug("no msg received, reason is: " +str(subcriptionResp[2]))
                    # todo if topic is Timeout, next value is # consecutive timeouts
                    # if number timeouts is > threshold; Server may be dead
                    if subcriptionResp[2] == moKeys.keyForTimeout():
                        log.debug("Timeout count:"+str(subcriptionResp[3]))
            await trio.sleep(1)
        except trio.Cancelled:
            log.error("***modacLoop caught trioCancelled, exiting")
            this.__killLoops = True
            break # a bit redundant but ok
    log.info("End modacAsyncLoop")

async def csvLogger():
    # loop and log if it is time
    # note use timeDiff instead of trio.sleep() so we check canceled often
    log.info("Begin csvLogger")
    count = 0
    while not this.__killLoops:
        log.debug("top csvLogger")
        if moTkShared().csvActive:
            now = datetime.datetime.now()
            if moTkShared().lastCsvStep is None:
                log.debug("First row to CSV")
                moCSV.addRow()
                moTkShared().lastCsvStep = now
            timeDiff = now - moTkShared().lastCsvStep
            if timeDiff.seconds > moTkShared().csvStep:
                log.debug("Add row to CSV")
                moCSV.addRow()
                moTkShared().lastCsvStep = now
        try:
            await trio.sleep(2)
        except trio.Cancelled:
            log.debug("yo! trio Cancelled")
            break;
    log.info("End csvLogger")

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
    # Primary async to create nursery and fire off the async tasks
    async with trio.open_nursery() as nursery:
        log.info("start with nursery")
        moData.setNursery(nursery)
        # memory channel is used to let TK know something changed in moData
        # note that moData is still not thread safe
        send_channel, receive_channel = trio.open_memory_channel(0)
        nursery.start_soon(modacAsyncLoop, send_channel)
        nursery.start_soon(tkAsyncLoop, receive_channel)
        nursery.start_soon(csvLogger)
        log.info("end with nursery")

##############################
# now the main app stuff
if __name__ == "__main__":
    # watch for signals
    signal.signal(signal.SIGINT, signalExit)

    moData.init(client=True)
    moClient.startClient()  # open hailing frequencies (pynng comms w/server)
    createTKWindow() # builds the UI
    try:
        # fire up the Trio nursery and its tasks
        trio.run(modacTKClient)
    except trio.Cancelled:
        log.warning("Trio Cancelled - ending server")
    except Exception as e:
        print("Exception somewhere in modacTKClient. see log files")
        log.error("Exception happened", exc_info=True)
    finally:
        print("end main")
    # we done. time to die
    moData.setNursery(None)
    log.debug("modac nursery try died");
    log.error("Exception happened?", exc_info=True)
    signalExit()
