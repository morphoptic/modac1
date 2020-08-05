# moTabAllData a tab for moTkShell
import sys
this = sys.modules[__name__]
import datetime
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json
from collections import OrderedDict

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd

from modac.moKeys import *
from modac import moData, moLogger
from modac import moCommand, moClient
from kilnControl.kilnScript import *
from .moTkShared import *

defaultTargetTemp = 100.0
defaultDisplacement = 5.0
defaultMaxTime = (60*24)
defaultStepTime = 2

class moTabKiln():
    def __init__(self,frame):
        #TODO build out by copying in from kilnPanel2.py (GTK)
        self.frame = frame
        self.tabTitle = "Kiln Control"

        # some generic variables
        self.kilnScript = KilnScript() # need at least one simple
        self.updating = True # used when updating current script gui to avoid stack overflow
        self.timestamp = "none yet"
        self.dataCount = 0
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")
        self.last_open_dir = "."
        self.kilnState = KilnState.Closed
        self.lastState = KilnState.Closed
        self.prevkilnState = KilnState.Closed

        # statusFrame: simulate CkBox; KilnState; KilnScriptState
        # infoFrame: scriptBtnFrame; scriptNameDescrFrame
        #    infoBtnFrame: Load; Save; Run Stop
        #    infoTxtFrame: Name; Description
        # scriptStepFrame: stepBtnFrame; stepDataFrame; stepScrollFrame
        #    stepBtnFrame: stepSelect; Add; Remove
        #    stepDataFrame: TargetTempSelect; displacement; holdTime; exhaust;support; 12v; pidStepTime

        ############
        self.statusFrame = tk.Frame(self.frame, bg="blue")
        self.simulateVar = tk.BooleanVar(self.frame, False)
        self.simulateCk = None
        self.simulateCk = tk.Checkbutton(self.statusFrame, text='Simulate?',
                                         variable=self.simulateVar, onvalue=True, offvalue=False,
                                         command=self.on_SimulateCk_activate)
        self.simulateCk.pack(side=tk.LEFT,fill=tk.BOTH, padx=2, expand=1)

        self.kilnStateLabel = tk.Label(self.statusFrame, text="KilnState: tkStarting")
        self.kilnStateLabel.pack(fill=tk.BOTH, expand=1)
        self.kilnScriptStateLabel= tk.Label(self.statusFrame, text="Kiln ScriptState: tkStarting")
        self.kilnScriptStateLabel.pack(fill=tk.BOTH, side=tk.RIGHT,expand=1)

        self.statusFrame.pack(side=tk.TOP, pady=2, fill=tk.X) #expand=1,
        ############
        # infoFrame: scriptBtnFrame; scriptNameDescrFrame
        #    infoBtnFrame: Load; Save; Run Stop
        #    infoTxtFrame: Name; Description
        self.infoFrame = tk.Frame(self.frame, bg='azure')
        ##
        self.infoBtnFrame = tk.Frame(self.infoFrame, bg = 'azure2')
        self.LoadBtn = tk.Button(self.infoBtnFrame,text="Load Script", command=self.on_LoadKilnScript_clicked)
        self.LoadBtn.pack()
        self.SaveBtn = tk.Button(self.infoBtnFrame,text="Save Script", command=self.on_SaveKilnScript_clicked)
        self.SaveBtn.pack()
        self.runBtn = tk.Button(self.infoBtnFrame, text="Run Script", command=self.on_RunKilnScript_clicked)
        self.runBtn.pack()
        self.stopBtn = tk.Button(self.infoBtnFrame, text="Stop Script", command=self.on_StopKilnScript_clicked, state=tk.DISABLED)
        self.stopBtn.pack()
        self.infoBtnFrame.pack(side=tk.LEFT)
        ##
        self.infoTxtFrame = tk.Frame(self.infoFrame, bg='azure2')
        #
        self.nameFrame = tk.Frame(self.infoTxtFrame, bg='azure3')
        self.nameLabel = tk.Label(self.nameFrame,text="Name:")
        self.nameLabel.pack(side=tk.LEFT,fill=tk.BOTH)
        self.nameTxtBox = tk.Text(self.nameFrame,height=2)
        self.nameTxtBox.insert(tk.END,"nameTxtBox tk starting")
        self.nameTxtBox.pack(side=tk.RIGHT)
        self.nameFrame.pack(side=tk.TOP, fill=tk.X)
        #
        self.descrFrame = tk.Frame(self.infoTxtFrame, bg = 'azure4')
        self.descrLabel = tk.Label(self.descrFrame,text="Description:")
        self.descrLabel.pack(side=tk.LEFT,fill=tk.BOTH)
        self.descrTxtBox = tk.Text(self.descrFrame,height=4)
        self.descrTxtBox.insert(tk.END,"descrTxtBox tk starting")
        self.descrTxtBox.pack(side=tk.RIGHT)
        self.descrFrame.pack(side=tk.BOTTOM,fill=tk.BOTH )
        self.infoTxtFrame.pack(side=tk.RIGHT, fill=tk.BOTH)
        ##
        self.infoFrame.pack(pady=2,  fill=tk.X)

        ############
        # scriptStepFrame: stepBtnFrame; stepDataFrame; stepScrollFrame
        #    stepBtnFrame: stepSelect; Add; Remove
        #    stepDataFrame: TargetTempSelect; displacement; holdTime; exhaust;support; 12v; pidStepTime
        #    stepScrollFrame: vertical scroll window w/json txt
        self.scriptStepFrame = tk.Frame(self.frame, bg="red")
        #
        stepBtnFrame = tk.Frame(self.scriptStepFrame)
        scriptStepsLabel = tk.Label(stepBtnFrame,text="Script Steps")
        scriptStepsLabel.pack(side=tk.TOP)
        self.stepSelector = ttk.Combobox(stepBtnFrame, values=["0"], exportselection=0,
                                         state="readonly", justify="center",width=4)
        self.stepSelector.bind("<<ComboboxSelected>>", self.on_stepSelectorChanged)
        self.stepSelector.pack(fill=tk.X)
        self.addBtn = tk.Button(stepBtnFrame,text="Add",command=self.on_AddButton_clicked)
        self.addBtn.pack(fill=tk.X)
        self.removeBtn = tk.Button(stepBtnFrame,text="Remove",command=self.on_RemoveButton_clicked)
        self.removeBtn.pack(fill=tk.X)
        stepBtnFrame.pack(side=tk.LEFT, fill=tk.Y)
        #
        stepDataFrame = tk.Frame(self.scriptStepFrame)
        stepData = tk.Label(stepDataFrame,text="stepDataFrame will go here")
        stepData.pack()
        stepDataFrame.pack()
        #
        stepScrollFrame = tk.Frame(self.scriptStepFrame)
        self.scrolledBox = tk.scrolledtext.ScrolledText(stepScrollFrame)
        self.scrolledBox.insert(tk.END, "This is\n the first\n text")
        self.scrolledBox.pack(fill=tk.Y, expand=1)
        stepScrollFrame.pack(side=tk.RIGHT,expand=1,fill=tk.BOTH)

        self.scriptStepFrame.pack(side=tk.BOTTOM,  pady=2, expand=1, fill=tk.BOTH)

        ############
        self.setFromScript()  # coming back from this will have self.updating=False
        # fill in the readOnly values
        self.updateFromMoData()
        self.frame.pack(fill=tk.BOTH, expand=1)

    def setFromScript(self):
        # used in init and after loading script
        # Tk uses *Var while GTK and various set methods
        self.updating = True # avoid infinite loops

        self.simulateVar.set(self.kilnScript.simulate)
        if self.kilnScript.simulate:
            self.simulateCk.config(bg="yellow")
        else:
            self.simulateCk.config(bg="white")

        # assuming kilnScript is a KilnScript object
        # self.nameTxtBox.delete(1.0,tk.END)
        # self.nameTxtBox.insert(1.0,self.kilnScript.name)
        self.descrTxtBox.delete(1.0,tk.END)
        self.descrTxtBox.insert(1.0,self.kilnScript.description)

        self.getKilnStatus() # grabs rest from moData?

        # self.currSegmentIdex is lable so rest value with
        # keyForScriptCurrentSegmentIdx(): kilnScript.curSegmentIdx,
        self.curSegIdx = self.kilnScript.curSegmentIdx
        #
        indicies = [i for i in range(0,self.kilnScript.numSteps())]
        self.stepSelector.config(values=indicies)

        self.setCurSegDisplay()

        self.updating = False

    def getTitle(self):
        return self.tabTitle

    def getKilnStatus(self):
        # status message recieved: update text and perhaps some others
        self.kilnStatus = moData.getValue(keyForKilnStatus())
        self.stateName = self.kilnStatus[keyForState()]

        self.kilnState = KilnState[self.stateName]
        self.scriptStateName = self.kilnStatus[keyForKilnScriptState()]
        if self.kilnState == KilnState.RunningScript:
             # kiln thinks it is running, so lock out edits and up date display from values
             self.curSegIdx = self.kilnStatus[keyForSegmentIndex()]
        self.timestamp = self.kilnStatus[keyForTimeStamp()]

        #print("KilnStatus", self.kilnStatus)
        return True

    def setCurSegDisplay(self):
        # update elements based on current Script Status
        # update UI from current script and moData
        self.simulateVar.set(self.kilnScript.simulate)

        if self.curSegIdx < 0 or self.curSegIdx >= self.kilnScript.numSteps():
            msg = "curSegIdx " + str(self.curSegIdx) + " out of range max "+ str(self.kilnScript.numSteps())
            log.error(msg)
            mb.showerror("Segment Index Out of Range",message=msg)
            self.curSegIdx = 0
        self.updating = True
        self.curSeg = self.kilnScript.segments[self.curSegIdx]
        self.kilnStateLabel.config(text="KilnState:"+self.stateName)
        self.kilnScriptStateLabel.config(text="Kiln ScriptState:"+self.scriptStateName)

        self.stepSelector.current(self.curSegIdx)
        # self.currentSegmentIdxBox.set_text("Step Index: "+str(self.curSegIdx) + " of "+ str(self.kilnScript.numSteps()-1))
        #
        # # now snag the current segment for reference
        # # fill in for current segment: targetTime, dist, hold
        # self.targetTSpinner.set_value(self.curSeg.targetTemperature)
        # self.displacementSpinner.set_value(self.curSeg.targetDistanceChange)
        # self.holdTimeSpinner.set_value(self.curSeg.holdTimeMinutes)
        # self.timeStepSpinner.set_value(self.curSeg.stepTime)
        # self.exhaustFanBtn.set_active(self.curSeg.exhaustFan)
        # self.supportFanBtn.set_active(self.curSeg.supportFan)
        # self.v12RelayBtn.set_active(self.curSeg.v12Relay)
        # self.updating = False

    def setData(self):
        # most of kilnStatus (all?) becomes put JSON text into ScriptStatus box
        self.getKilnStatus()
        self.setCurSegDisplay()

        if self.prevkilnState == KilnState.RunningScript and self.kilnState == KilnState.Idle:
            # really should have gotten EndScript command but...
            log.debug("noticed kilnState went back to Idle, so endScript")
            self.endScript()

        self.prevkilnState = self.kilnState

        # state is the name or string rep of KilnState
        #log.debug("KilnPanel setData Reported state: "+self.stateName)

        textScriptStatus = json.dumps(self.kilnStatus, indent=4)
        #self.scriptStatusBuffer.set_text(textScriptStatus)

    # called on setup and when MoData is updated by server msg
    def updateFromMoData(self):
        self.setData()
        pass

    def endScript(self):
        log.debug("Kiln endScript")
        self.resetRunStop()
        self.curSegIdx = 0
        self.kilnScript.getSegment(0)

    def on_SimulateCk_activate(self):
        # ck box updated, move value to script
        if self.simulateCk == None:
            return
        self.kilnScript.simulate = self.simulateVar.get()
        if self.kilnScript.simulate:
            self.simulateCk.config(bg="yellow")
        else:
            self.simulateCk.config(bg="white")

    def on_RunKilnScript_clicked(self):
        # start kiln script
        # collect data for command, send command
        log.debug("on_RunKilnScript_clicked")

        param = str()
        # get JSON for of script
        param = str(self.kilnScript)

        # Disable Run, Enable Terminate
        self.setRunStop()

        print("\n**** Send RunKiln: ", param)
        moCommand.cmdRunKilnScript(param)

    def on_StopKilnScript_clicked(self):
        log.debug("onTerminateRun")
        self.endScript()
        moCommand.cmdStopKilnScript()

    def setRunStop(self):
        self.runBtn.config(state=tk.DISABLED)
        self.stopBtn.config(state=tk.ENABLED)
        # TODO may also want to disable editing script entirely at this point
        # perhaps something akin to the resetBtn stuff

    def resetRunStop(self):
        log.debug("Reset Abort/Run Buttons")
        self.stopBtn.config(state=tk.DISABLED)
        self.runBtn.config(state=tk.ENABLED)
        # TODO reset editing of current step

    def on_LoadKilnScript_clicked(self):
        log.debug("on_LoadKilnScript_clicked")
        name = fd.askopenfilename(initialdir=moTkShared().last_open_dir,
                                    title="Kiln Script File To Open",
                                    filetypes=[('JSON files', '.json')],
                                    defaultextension='.json')
        if name == None or name == "":
            return # canceled
        self.filename = name
        log.debug("Load Script from file: "+str(self.filename))
        moTkShared().last_open_dir = os.path.dirname(name)
        try:
            retVal = loadScriptFromFile(self.filename)
        except:
            msg = "Failed to load script from "+ self.filename
            log.error("Failed to load script from "+ self.filename)
            # Error Dialog
            mb.showerror(title="Failed to load script", message=msg)
            return
        log.debug("on_LoadScript  succeeded file: " + self.filename )
        self.kilnScript = retVal
        self.kilnScript.curSegmentIdx = 0  # force load to step 0
        self.setFromScript()

    def on_SaveKilnScript_clicked(self):
        log.debug("on_SaveKilnScript_clicked")
        # ask for Filename, using last directory, and *.csv as filters; if supported
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")
        name = fd.asksaveasfilename(initialdir=moTkShared().last_open_dir,
                                    title="File to Save Script",
                                    initialfile=self.filename,
                                    filetypes=[('JSON files', '.json')],
                                    defaultextension='.json')
        print("saveScript to file",name)
        # if ok, then
        if name == None or name == "":
            return
        self.filename = name
        log.debug("saveScript to file: "+str(self.filename))
        moTkShared().last_open_dir = os.path.dirname(name)
        self.kilnScript.saveScript(self.filename)

    def on_stepSelectorChanged(self):
        if self.updating == True:
            return # avoid repeated triggers and stack overflow
        # a step was selected... make that index current
        curId = selector.current()
        log.debug("stepSelector Changed")
        if curId == self.kilnScript.curSegmentIdx:
            log.debug("same as current, ignore")
        else:
            log.debug("new current, update")
            self.kilnScript.getSegment(curId)
            self.setFromScript()

    def on_AddButton_clicked(self):
        # add one to end, update display
        log.debug("before Add Segment script is: "+str(self.kilnScript))
        self.kilnScript.addNewSegment()
        self.setFromScript()
        log.debug("after Add Segment script is: "+str(self.kilnScript))
        pass

    def on_RemoveButton_clicked(self):
        # remove current, update display
        log.debug("before Remove Segment script is: "+str(self.kilnScript))
        self.kilnScript.removeCurrentSegment()
        self.setFromScript()
        log.debug("after Remove Segment script is: "+str(self.kilnScript))
        pass
