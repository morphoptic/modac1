# moTkTimeoutDialog: invoked when server timeout exceeds threshold; shows dialog, updates count, waits for reset
import sys
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

this = sys.modules[__name__]

import tkinter as tk
from modac import moClient


__dialogWindow = None

def showOrUpdate(root,msg):
    log.debug("showOrUpdate TkTimeoutDialog " + msg)
    # parse msg... should be keyForTimeout() " " count
    msgList = msg.split() # split at space
    #log.debug("showOrUpdate msgList " + str(msgList))
    count = int(msgList[1])
    #log.debug("count is "+ str(count))
    # if active, update with count
    # else create and show with count
    if this.__dialogWindow == None:
        this.__dialogWindow = moTkTimeoutDialog(root, msg)
    else:
        this.__dialogWindow.update(count)
    pass

class moTkTimeoutDialog( tk.Toplevel):
    count = 0

    def __init__(self, root, count):
        tk.Toplevel.__init__(self, root)
        my_frame = tk.Frame(self)
        my_frame.pack(expand=True, padx=20, pady=20)
        self.title = "MODDAC Server Timeout Counts"

        self.strVar = tk.StringVar()
        self.strVar.set("Count = "+str(count))
        self.label = tk.Label(self, textvariable=self.strVar)
        self.label.pack()
        #self.label.grid(row=0, column=0)
        self.button = tk.Button(self, text="Reset Connection", command=self.resetConnection)
        self.button.pack()
        #self.button.grid(row=1, column=0)

    def resetConnection(self):
        moClient.reconnectServer()
        this.__dialogWindow = None
        self.destroy()

    def update(self, count):
        self.strVar.set("Count = "+str(count))
