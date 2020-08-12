# moTKMenu - Top level Menu for modac TK GUI apps
# add to a window
import sys
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import os, signal

from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

from .moTkShared import *
from modac import moCSV, moCommand

def setCSVTiming():
    print("setCSVTiming")
    # dialog to get integer Seconds
    numSec = sd.askinteger(title="CSV Step:",
                           initialvalue=moTkShared().csvStep ,
                           prompt="Seconds between CSV Save:")
    # if dialog ok, put seconds into moTkShared.csvStep
    if numSec > 0:
        moTkShared().csvStep = numSec
    pass

def terminateServer():
    # send command TerminateServer
    log.debug("Shutdown Server Activated")
    moCommand.cmdShutdown()
    pass

def stopCSVRecording():
    print("stopCSVRecording")
    moTKShared().csvActive = False
    moCSV.close()
    pass

def startCSVRecording():
    print("startCSVRecording")
    log.info("startCSVRecording to "+moTkShared().csvFilename+ "Rate= "+str(moTkShared().csvStep))
    moCSV.init(moTkShared().csvFilename)
    moTkShared().csvActive = True
    pass

def setCSVFile():
    # if active, ask to stop?
    #    if not, return
    if moTkShared().csvActive == True:
        if mb.askyesno('CSV Already Running', 'Stop Previous?'):
            moCSV.close()
        else:
            return
    # ask for Filename, using last directory, and *.csv as filters; if supported
    name = fd.asksaveasfilename(initialdir=moTkShared().last_open_dir,
                                title="File to save CSV",
                                initialfile =moTkShared().csvFilename,
                                filetypes = [('CSV files', '.csv')],
                                defaultextension='.csv')
    print(name)
    # if ok, then
    if name is None or name == "":
        return
    moTkShared().csvFilename = name
    moTkShared().last_open_dir = os.path.dirname(name)

def doExit():
    print("doExit - sends signal.SIGINT")
    pid = os.getpid()
    os.kill(pid,signal.SIGINT)
    pass

def About():
    print("This is a simple example of a menu")

class moTkMenu():
    def __init__(self, root ):
        self.menu = Menu(root)
        root.config(menu=self.menu)
        moTkShared().root = root

        self.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Set CSV RecordRate", command=setCSVTiming)
        self.filemenu.add_command(label="Set CSV File", command=setCSVFile)
        self.filemenu.add_command(label="Start CSV Recording", command=startCSVRecording)
        self.filemenu.add_command(label="Stop CSV Recording", command=stopCSVRecording)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Terminate Server", command=terminateServer) # too simple?
        self.filemenu.add_command(label="Exit", command=doExit) # too simple?

        self.helpmenu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="About...", command=About)