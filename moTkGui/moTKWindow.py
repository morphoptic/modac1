# moTkWindow- Class to provide TK GUI shell with menu+ notebook
# this module/class is the top level to which the client app will add notebook pages, etc
# it defines a number of the top/bottom status areas (ad16, moServer, timestamp)
# and provides a Notebook for adding different moPanels
########################################################
### First all the imports
import sys
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

## UI
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

## Trio for async
import trio

# modac stuff
from modac.moKeys import *
from modac import moData, moCommand, moClient, moCSV
from modac.moStatus import *
from .moTkShared import *
from .moTkMenu import moTkMenu

class moTkWindow():

    def __init__(self, title="MODAC Tk Gui", closeMethod= None):
        self.window = tk.Tk()  # could be root instead of window
        self.setCloseMethod(closeMethod)
        self.window.geometry('800x700') # if dont specify, it fill out too big
        self.window.title(title)
        self.moObjects = [] # an array into which we will store panels that hold modac data
        self.shared = moTkShared()

        # put in the common Modac Menu
        self.menu = moTkMenu(self.window)

        ##################################################################
        # status bar below Menu
        self.moStatus = tk.StringVar()
        self.moStatus.set("ModacStatus: notYet " )
        self.ad16Status = tk.StringVar()
        self.ad16Status.set("Ad16: notYet")

        self.topFrame = tk.Frame(self.window, bg="blue")
        # self.l1 = ttk.Label(self.topFrame, text=self.str_modacStatus)#, textvariable=self.moStatus)
        mostat = tk.Label(self.topFrame, textvariable=self.moStatus)
        mostat.pack(side=tk.LEFT,fill=tk.X, padx=2, expand=1)
        self.moStatus.set("ModacStatus: waiting for data.")

        self.adStatusLabel = tk.Label(self.topFrame, textvariable=self.ad16Status)
        self.ad16Status.set("Ad16: tk starting")
        self.adStatusLabel.pack(side=tk.RIGHT,fill=tk.X, padx=1, expand=1)
        self.topFrame.pack(side=tk.TOP, pady=2, expand=1, fill=tk.X)
        #self.topFrame.grid(row=0, sticky='NW')

        ##################################################################
        # MidFrame: Tabbed Notebook in center; addTab() will add more tabs
        self.midFrame = tk.Frame(self.window, bg="blue")

        #self.midScrolledBox = tk.scrolledtext.ScrolledText(self.midFrame, width=90)

        #self.nb = ttk.Notebook(self.midScrolledBox)
        self.nb = ttk.Notebook(self.midFrame, height =650)
        #self.nb.grid(row=1, sticky='NSEW')
        self.nb.pack(fill=tk.X, side=tk.TOP)#, expand=1)

        self.midFrame.pack(fill= tk.X)

        ##################################################################
        # bottom status (last message received)
        # why does this not display at bottom of window
        self.moUpdateStr = tk.StringVar()
        self.moUpdateStr.set("No Data Yet")
        self.bottomFrame = tk.Frame(self.window,bg="green")
        self.bottomLabel = ttk.Label(self.bottomFrame,  textvariable=self.moUpdateStr)
        self.bottomLabel.pack(fill=tk.BOTH, padx=1, expand=1)

        #self.bottomFrame.grid(row=2, sticky='NSEW')
        self.bottomFrame.pack(side=tk.BOTTOM, pady=2, expand=1, fill=tk.X)
        #self.moUpdateStr.set("No Data Yet")

        self.dataCount = 0

    def root(self):
        return self.window

    def notebook(self):
        return self.nb

    def setCloseMethod(self, closeMethod):
        if closeMethod != None:
            self.window.protocol("WM_DELETE_WINDOW", closeMethod)

    def addTab(self, frame,moObject=None, frameTitle=None):
        #try and get name from frame
        print("AddTab", frame, moObject, frameTitle)
        if frameTitle is None:
            try:
                frameTitle = moObject.getTitle()
            except:
                log.error("addTab doesnt seem to have a getTabTitle")
                frameTitle = "None"
        self.nb.add(frame, text=frameTitle)
        if moObject != None:
            self.moObjects.append(moObject)
        pass

    def updateFromMoData(self):
        self.dataCount +=1
        log.debug("updatefromMoData %d"%(self.dataCount))
        # moData has changed, tell all children to update
        # note this is NOT very thread safe data access

        timestamp = moData.getValue(keyForTimeStamp())
        self.moStatus.set("ModacStatus: " + moData.getValue(keyForStatus()))

        adStatus = None
        try:
            adStatus = moData.getValue(keyForAD16Status())
        except KeyError:
            log.error("KeyError getting ad16 status, set to error")
            adStatus = moStatus.Error.name

        self.ad16Status.set("Ad16: "+ adStatus)
        if adStatus == moStatus.Error.name:
            self.adStatusLabel.configure(bg="red")
        elif adStatus == moStatus.Simulated.name:
            self.adStatusLabel.configure(bg="yellow")
        else:
            self.adStatusLabel.configure(bg="green")

        self.moUpdateStr.set("Data Updated: #%d at "%self.dataCount +timestamp)

        # update top/bottom status
        for tab in self.moObjects:
            # tell tab to do its moUpdate
            tab.updateFromMoData()
        pass
