# moTabBinaryOut a tab for moTkShell to show/control binaryOuts
import sys
import logging, logging.handlers, traceback

this = sys.modules[__name__]
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from modac.moKeys import *
from modac import moData, moLogger
from modac import moCommand, moClient

from .moTkShared import *

class moTabRelays():
    def getTitle(self):
        return self.tabTitle

    def __init__(self, frame):
        log.debug(" initialize moTabBinaryOut top")
        self.frame = frame
        self.tabTitle = "BinaryOutputs"

        this.__tabInstance = self

        self.Texts = ["12V Power", "Lower Heater", "Middle Heater", "Upper Heater",
                      "NC 4", "NC 5", "NC 6", "NC 7", "NC 8",
                      "Support Fan", "Exhaust Fan","NC 11"]
        self.CmdBVar = []
        self.RptBVar = []
        self.Commanded = []
        self.Reported = []

        log.debug(" initialize moTabRelays UI panels")

        header0 = tk.Label(frame, text="Relay Command")
        header0.grid(row=0, column=0, sticky="nsew")
        header1 = tk.Label(frame, text="Relay Reported")
        header1.grid(row=0, column=1, sticky="nsew")

        for i, z in enumerate(self.Texts):
            self.CmdBVar.append(tk.BooleanVar(frame, False))
            self.RptBVar.append(tk.BooleanVar(frame, False))
            self.Commanded.append(tk.Checkbutton(frame, text=z, onvalue=True, offvalue=False,
                                            variable=self.CmdBVar[i], command=lambda itemp=i: self.callback(itemp)))
            self.Commanded[i].grid(row=i + 1, column=0, sticky="nsew")
            self.Reported.append(
                tk.Checkbutton(frame, text=z, onvalue=True, offvalue=False, state=tk.DISABLED, variable=self.RptBVar[i]))
            self.Reported[i].grid(row=i + 1, column=1, sticky="nsew")
            self.frame.grid_rowconfigure(i+1, weight=1)
            self.frame.grid_columnconfigure(i+1, weight=1)

        self.summaryLabel = tk.Label(frame, text="ButtonStatus")
        self.summaryLabel.grid(row=len(self.Texts)+1, columnspan=2, sticky="nsew")

        log.debug(" initialize moTabKiln build script Step")
        ############
        self.updateFromMoData()
        self.frame.pack(fill=tk.BOTH, expand=1)

    def callback(self, idx):
        state = self.CmdBVar[idx].get()
        print(idx, self.Texts[idx], state)
        msg = f"update Relay {idx}, {self.Texts[idx]}, {state}"
        log.debug(msg)
        moCommand.cmdBinary(idx, state)

    # called when MoData is updated by server msg
    def updateFromMoData(self):
        states = moData.getValue(keyForBinaryOut())
        self.summaryLabel.config(text="Relay States: " + str(states))
        print("BinaryOut/Relays has ",len(states),"entries")
        print("Reported BVar ",len(self.RptBVar),"entries")
        for i, s, in enumerate(states):
            print("update rpt", i, s)
            self.RptBVar[i] = s
