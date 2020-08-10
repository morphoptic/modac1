#moTabAllData a tab for moTkShell

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import tkinter as tk
from tkinter import ttk
from modac import moData

class moTabAllData():
    def __init__(self,frame):
        self.frame = frame
        self.scrolledBox = tk.scrolledtext.ScrolledText(frame, width=90)
        #self.scrolledBox.grid(column=0, row=0)
        self.scrolledBox.pack(fill=tk.BOTH, expand=1)
        self.scrolledBox.insert(tk.END, "This is\n the first\n text")
        self.tabTitle = "AllData"
        self.frame.pack(fill=tk.BOTH,expand=1)

    def getTitle(self):
        return self.tabTitle

    def updateFromMoData(self):
        # TODO: remember scroll position and reset to there
        moMsg = moData.asJson() #grab the whole thing and stuff it in scrolled text
        # TODO: index/see should scroll back to same point but doesnt
        index = self.scrolledBox.index("@0,0")
        self.scrolledBox.delete(1.0, tk.END)
        self.scrolledBox.insert(tk.END, moMsg)
        self.scrolledBox.see(index)
        index = self.scrolledBox.index("@0,0")
        pass

