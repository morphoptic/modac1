# moTkTimeoutDialog: invoked when server timeout exceeds threshold; shows dialog, updates count, waits for reset
import sys
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

this = sys.modules[__name__]

import tkinter as tk
from modac import moClient

__dialogWindow = None
__root = None

def showOrUpdate(root,msg):
    #log.debug("showOrUpdate TkTimeoutDialog " + msg)
    # parse msg... should be keyForTimeout() " " count
    msgList = msg.split() # split at space
    #log.debug("showOrUpdate msgList " + str(msgList))
    count = int(msgList[1])
    #log.debug("count is "+ str(count))
    # if active, update with count
    # else create and show with count
    if this.__dialogWindow == None:
        #log.debug("create new timeout dialog")
        this.__dialogWindow = moTkTimeoutDialog(root, msg)
        this.__root = root
    else:
        #log.debug("reuse existing timeout dialog")
        this.__dialogWindow.update(count)
    pass

def destroyDialog():
    if this.__dialogWindow == None:
        log.debug("DestroyDialog but it is gone")
    else:
        #this.__dialogWindow.forget()
        this.__dialogWindow.destroy()
        this.__dialogWindow = None

class moTkTimeoutDialog( tk.Toplevel):
    count = 0

    def __init__(self, root, count):
        tk.Toplevel.__init__(self, root)
        self.geometry('400x400') # if dont specify, it fill out too big
        self.protocol("WM_DELETE_WINDOW",self.closeEvent)
        my_frame = tk.Frame(self)
        my_frame.pack(expand=True, padx=20, pady=20)
        self.title("MODDAC Server Timeout")

        #tk.Label(self,text="Connection to Server Timedout!").pack(side=tk.TOP,fill=tk.X)

        self.strVar = tk.StringVar()
        self.strVar.set("Count = "+str(count))
        self.label1 = tk.Label(self, textvariable=self.strVar)
        self.label1.pack(side=tk.TOP,fill=tk.BOTH)
        #self.label.grid(row=0, column=0)
        self.button = tk.Button(self, text="Reset Connection", command=self.resetConnection)
        self.button.pack(side=tk.BOTTOM, fill= tk.BOTH)
        #self.button.grid(row=1, column=0)

    def resetConnection(self):
        moClient.reconnectServer()
        destroyDialog()

    def update(self, count):
        self.strVar.set("MODAC Timeout Count = "+str(count))

    def closeEvent(self):
        destroyDialog()
