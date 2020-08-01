# moTkWindow- Class to provide TK GUI shell with menu+ notebook
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

class moTkWindow():

    def __init__(self, title="MODAC Tk Gui", closeMethod= None):
        self.window = tk.Tk()  # could be root instead of window
        self.setCloseMethod(closeMethod)
        self.window.geometry('800x600')
        self.window.title(title)
        self.moObjects = [] # an array into which we will store panels that hold modac data

        # put in the common Modac Menu
        #self.menu = moTkMenu(self.window)

        # status bar below Menu
        self.moStatus = tk.StringVar()
        self.moStatus.set("ModacStatus: notYet " )
        self.ad16Status = tk.StringVar()
        self.ad16Status.set("Ad16: notYet")

        self.topFrame = tk.Frame(self.window, bg="blue")
        # self.l1 = ttk.Label(self.topFrame, text=self.str_modacStatus)#, textvariable=self.moStatus)
        mostat = ttk.Label(self.topFrame, textvariable=self.moStatus)
        mostat.grid(row=0, column=0,sticky='NW')
        self.moStatus.set("ModacStatus: waiting for data.")

        adstat = ttk.Label(self.topFrame, textvariable=self.ad16Status)
        self.ad16Status.set("Ad16: tk starting")
        adstat.grid(row=0, column=2,sticky='NE')
        self.topFrame.grid(row=0, sticky='NW')

        # Tabbed Notebook
        self.nb = ttk.Notebook(self.window)
        self.nb.grid(row=1, sticky='NSEW')

        # bottom status (last message received)
        # status bar below Menu?
        self.moUpdateStr = tk.StringVar()
        self.moStatus.set("No Data Yet")
        self.bottomFrame = tk.Frame(self.window,bg="green")
        self.l2 = ttk.Label(self.bottomFrame,  textvariable=self.moUpdateStr)
        self.l2.grid(column=0, sticky='NW')
        self.bottomFrame.grid(row=2, sticky='NSEW')
        self.moStatus.set("No Data Yet")

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
        if frameTitle == None:
            try:
                title = moObject.getTitle()
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
        self.ad16Status.set("Ad16: "+ moData.getValue(keyForAD16Status()))
        self.moUpdateStr.set("Data Updated: #%d at "%self.dataCount +timestamp)

        # update top/bottom status
        for tab in self.moObjects:
            # tell tab to do its moUpdate
            tab.updateFromMoData()
        pass
