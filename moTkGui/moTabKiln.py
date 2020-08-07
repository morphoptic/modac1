# moTabAllData a tab for moTkShell
import sys
import logging, logging.handlers, traceback

this = sys.modules[__name__]
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from modac import moData, moLogger
from modac import moCommand, moClient
from kilnControl.kilnScript import *
from .moTkShared import *

defaultTargetTemp = 100.0
defaultDisplacement = 5.0
defaultMaxTime = (60 * 24)
defaultStepTime = 2


### couple validators for TextEntry widgets
def validPositiveInt(s):  # validates string holds positive int
    try:
        i = int(s)
        if i < 0:
            return False
        return True
    except ValueError:
        return False


def validPositiveFloat(s):
    try:
        f = float(s)
        if f < 0.0:
            return False
        return True
    except ValueError:
        return False


class moTabKiln():
    def __init__(self, frame):
        # TODO build out by copying in from kilnPanel2.py (GTK)
        self.frame = frame
        self.tabTitle = "Kiln Control"

        # some generic variables
        self.kilnScript = KilnScript()  # need at least one simple
        self.updating = True  # used when updating current script gui to avoid stack overflow
        self.timestamp = "none yet"
        self.dataCount = 0
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")
        self.last_open_dir = "./kilnScripts"
        self.kilnState = KilnState.Closed
        self.lastState = KilnState.Closed
        self.prevkilnState = KilnState.Closed

        # TODO: stateName/scriptStateName could be tk.StringVar()
        self.stateName = str(self.kilnState)
        self.scriptStateName = str(KilnScriptState.Unknown)

        self.curSegIdx = 0
        self.kilnStatus = None # returned by moData
        # some vars needed by UI elements
        self.temperatureSV = tk.StringVar(self.frame)
        self.stepTimeSV = tk.StringVar(self.frame)
        self.displacementSV = tk.StringVar(self.frame)
        self.exhaustBV = tk.BooleanVar(self.frame, False)
        self.supportBV = tk.BooleanVar(self.frame, False)
        self.twelvevBV = tk.BooleanVar(self.frame, False)
        self.exhaustCk = None
        self.supportCk = None
        self.twelvevCk = None

        # statusFrame: simulate CkBox; KilnState; KilnScriptState
        # infoFrame: scriptBtnFrame; scriptNameDescrFrame
        #    infoBtnFrame: Load; Save; Run Stop
        #    infoTxtFrame: Name; Description
        # scriptStepFrame: stepBtnFrame; stepDataFrame; stepScrollFrame
        #    stepBtnFrame: stepSelect; Add; Remove
        #    stepDataFrame: TargetTempSelect; displacement; holdTime; exhaust;support; 12v; pidStepTime
        #    scrollFrame: scroll box of kilnStatus json

        ############
        self.build_StatusFrame()
        ############
        self.build_InfoFrame()

        ############
        # scriptStepFrame: stepBtnFrame; stepDataFrame; stepScrollFrame
        #    stepBtnFrame: stepSelect; Add; Remove
        #    stepDataFrame: TargetTempSelect; displacement; holdTime; exhaust;support; 12v; pidStepTime
        #    stepScrollFrame: vertical scroll window w/json txt
        self.scriptStepFrame = tk.Frame(self.frame, bg="red")
        leftFrame = tk.Frame(self.scriptStepFrame, bg="yellow")

        self.build_StepBtnFrame(leftFrame)  # self.scriptStepFrame
        self.build_StepDataFrame(leftFrame)
        leftFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        stepScrollFrame = tk.Frame(self.scriptStepFrame, bg="green")
        self.scrolledBox = tk.scrolledtext.ScrolledText(stepScrollFrame)
        self.scrolledBox.insert(tk.END, "This is\n the first\n text")
        self.scrolledBox.pack(fill=tk.Y, expand=1)
        stepScrollFrame.pack(side=tk.RIGHT, expand=1, fill=tk.BOTH)

        self.scriptStepFrame.pack(side=tk.BOTTOM, pady=2, expand=1, fill=tk.BOTH)

        ############
        self.setFromScript()  # coming back from this will have self.updating=False
        # fill in the readOnly values
        self.updateFromMoData()
        self.frame.pack(fill=tk.BOTH, expand=1)

    def build_StepDataFrame(self, parent):
        # stepDataFrame in middle
        # lable step N of N
        # TargetTemp (comboBox by 5?)
        # TargetDisplacement (combobox by 1mm)
        # HoldTime (comboBox by 5)
        # Exhaust Fan ckbox
        # supportFan ckbox
        # 12vRelay ckbox
        # PID StepTime (seconds by 1)
        stepDataFrame = tk.Frame(parent)
        self.stepIofNLabel = tk.Label(stepDataFrame, text="Step x of y")
        self.stepIofNLabel.pack()
        ## each item is a row/Frame w label, tk.StrVar,tk.Entry
        ## entry gets validated, StrVar gets a Write trace (changed) to callback()
        targetTempFrame = tk.Frame(stepDataFrame)
        tempLabel = tk.Label(targetTempFrame, text="Temp DegC:")
        tempLabel.pack(side=tk.LEFT)
        self.temperatureSV.trace_add("write", self.on_TargetTempChanged)
        tempEntry = tk.Entry(targetTempFrame, textvariable=self.temperatureSV, validatecommand=validPositiveInt)
        tempEntry.pack(side=tk.RIGHT)
        targetTempFrame.pack()
        #
        displacementFrame = tk.Frame(stepDataFrame)
        displacementLabel = tk.Label(displacementFrame, text="Displacement (mm):")
        displacementLabel.pack(side=tk.LEFT)
        self.displacementSV.trace_add("write", self.on_DisplacemenChanged)
        displacementEntry = tk.Entry(displacementFrame, textvariable=self.displacementSV,
                                     validatecommand=validPositiveFloat)
        displacementEntry.pack(side=tk.RIGHT)
        displacementFrame.pack()
        #
        self.holdTimeSV = tk.StringVar(self.frame)
        holdTimeFrame = tk.Frame(stepDataFrame)
        holdTimeLabel = tk.Label(holdTimeFrame, text="Hold Time (minutes):")
        holdTimeLabel.pack(side=tk.LEFT)
        self.holdTimeSV.trace_add("write", self.on_holdTimeChanged)
        holdTimeEntry = tk.Entry(holdTimeFrame, textvariable=self.holdTimeSV,
                                 validatecommand=validPositiveInt)
        holdTimeEntry.pack(side=tk.RIGHT)
        holdTimeFrame.pack()
        #
        stepTimeFrame = tk.Frame(stepDataFrame)
        stepTimeLabel = tk.Label(stepTimeFrame, text="PID Step Time (seconds):")
        stepTimeLabel.pack(side=tk.LEFT)
        self.stepTimeSV.trace_add("write", self.on_stepTimeChanged)
        stepTimeEntry = tk.Entry(stepTimeFrame, textvariable=self.stepTimeSV,
                                 validatecommand=validPositiveInt)
        stepTimeEntry.pack(side=tk.RIGHT)
        stepTimeFrame.pack()
        # CheckBox vars and standins created in __init__
        self.exhaustCk = tk.Checkbutton(stepDataFrame, text='Exhaust Fan',
                                        variable=self.exhaustBV, onvalue=True, offvalue=False,
                                        command=self.on_exhaustCk_activate)
        self.exhaustCk.pack(fill=tk.X)
        self.supportCk = tk.Checkbutton(stepDataFrame, text='Support Fan',
                                        variable=self.supportBV, onvalue=True, offvalue=False,
                                        command=self.on_SupportFan_toggled)
        self.supportCk.pack(fill=tk.X)
        self.twelvevCk = tk.Checkbutton(stepDataFrame, text='KilnHeater 12V',
                                        variable=self.twelvevBV, onvalue=True, offvalue=False,
                                        command=self.on_12vRelay_toggled)
        self.twelvevCk.pack(fill=tk.X)

        stepDataFrame.pack(fill=tk.BOTH, expand=1)

    def build_StepBtnFrame(self, parentFrame):
        stepBtnFrame = tk.Frame(parentFrame)
        scriptStepsLabel = tk.Label(stepBtnFrame, text="Script Steps")
        scriptStepsLabel.pack(side=tk.TOP)
        self.stepSelector = ttk.Combobox(stepBtnFrame, values=["0"], exportselection=0,
                                         state="readonly", justify="center", width=4)
        self.stepSelector.bind("<<ComboboxSelected>>", self.on_stepSelectorChanged)
        self.stepSelector.pack(fill=tk.X)
        self.addBtn = tk.Button(stepBtnFrame, text="Add", command=self.on_AddButton_clicked)
        self.addBtn.pack(fill=tk.X)
        self.removeBtn = tk.Button(stepBtnFrame, text="Remove", command=self.on_RemoveButton_clicked)
        self.removeBtn.pack(fill=tk.X)
        stepBtnFrame.pack(side=tk.LEFT, fill=tk.Y)

    def build_InfoFrame(self):
        # infoFrame: scriptBtnFrame; scriptNameDescrFrame
        #    infoBtnFrame: Load; Save; Run Stop
        #    infoTxtFrame: Name; Description
        infoFrame = tk.Frame(self.frame, bg='azure')
        ##
        infoBtnFrame = tk.Frame(infoFrame, bg='azure2')
        self.LoadBtn = tk.Button(infoBtnFrame, text="Load Script", command=self.on_LoadKilnScript_clicked)
        self.LoadBtn.pack()
        self.SaveBtn = tk.Button(infoBtnFrame, text="Save Script", command=self.on_SaveKilnScript_clicked)
        self.SaveBtn.pack()
        self.runBtn = tk.Button(infoBtnFrame, text="Run Script", command=self.on_RunKilnScript_clicked)
        self.runBtn.pack()
        self.stopBtn = tk.Button(infoBtnFrame, text="Stop Script", command=self.on_StopKilnScript_clicked,
                                 state=tk.DISABLED)
        self.stopBtn.pack()
        infoBtnFrame.pack(side=tk.LEFT)
        ##
        infoTxtFrame = tk.Frame(infoFrame, bg='azure2')
        #
        nameFrame = tk.Frame(infoTxtFrame, bg='azure3')
        nameLabel = tk.Label(nameFrame, text="Name:")
        nameLabel.pack(side=tk.LEFT, fill=tk.BOTH)
        self.nameTxtBox = tk.Text(nameFrame, height=2)
        self.nameTxtBox.insert(tk.END, "nameTxtBox tk starting")
        self.nameTxtBox.pack(side=tk.RIGHT)
        nameFrame.pack(side=tk.TOP, fill=tk.X)
        #
        descrFrame = tk.Frame(infoTxtFrame, bg='azure4')
        descrLabel = tk.Label(descrFrame, text="Description:")
        descrLabel.pack(side=tk.LEFT, fill=tk.BOTH)
        self.descrTxtBox = tk.Text(descrFrame, height=4)
        self.descrTxtBox.insert(tk.END, "descrTxtBox tk starting")
        self.descrTxtBox.pack(side=tk.RIGHT)
        descrFrame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        infoTxtFrame.pack(side=tk.RIGHT, fill=tk.BOTH)
        ##
        infoFrame.pack(pady=2, fill=tk.X)

    def build_StatusFrame(self):
        statusFrame = tk.Frame(self.frame, bg="blue")
        #
        self.simulateVar = tk.BooleanVar(self.frame, False)
        self.simulateCk = None
        self.simulateCk = tk.Checkbutton(statusFrame, text='Simulate?',
                                         variable=self.simulateVar, onvalue=True, offvalue=False,
                                         command=self.on_SimulateCk_activate)
        self.simulateCk.pack(side=tk.LEFT, fill=tk.BOTH, padx=2, expand=1)
        #
        self.kilnStateLabel = tk.Label(statusFrame, text="KilnState: tkStarting")
        self.kilnStateLabel.pack(fill=tk.BOTH, expand=1)
        self.kilnScriptStateLabel = tk.Label(statusFrame, text="Kiln ScriptState: tkStarting")
        self.kilnScriptStateLabel.pack(fill=tk.BOTH, side=tk.RIGHT, expand=1)
        #
        statusFrame.pack(side=tk.TOP, pady=2, fill=tk.X)  # expand=1,

    def setFromScript(self):
        # used in init and after loading script
        # Tk uses *Var while GTK and various set methods
        self.updating = True  # avoid infinite loops

        self.simulateVar.set(self.kilnScript.simulate)
        if self.kilnScript.simulate:
            self.simulateCk.config(bg="yellow")
        else:
            self.simulateCk.config(bg="white")

        # assuming kilnScript is a KilnScript object
        self.nameTxtBox.delete(1.0,tk.END)
        self.nameTxtBox.insert(1.0,self.kilnScript.name)
        self.descrTxtBox.delete(1.0, tk.END)
        self.descrTxtBox.insert(1.0, self.kilnScript.description)

        self.getKilnStatus()  # grabs rest from moData?

        # self.currSegmentIdex is lable so rest value with
        # keyForScriptCurrentSegmentIdx(): kilnScript.curSegmentIdx,
        self.curSegIdx = self.kilnScript.curSegmentIdx
        #
        indicies = [i for i in range(0, self.kilnScript.numSteps())]
        self.stepSelector.config(values=indicies)

        self.setCurSegDisplay()

        self.updating = False

    def getTitle(self):
        return self.tabTitle

    def getKilnStatus(self):
        # status message received: update text and perhaps some others
        self.kilnStatus = moData.getValue(keyForKilnStatus())
        self.stateName = self.kilnStatus[keyForState()]

        self.kilnState = KilnState[self.stateName]
        self.scriptStateName = self.kilnStatus[keyForKilnScriptState()]
        if self.kilnState == KilnState.RunningScript:
            # kiln thinks it is running, so lock out edits and up date display from values
            self.curSegIdx = self.kilnStatus[keyForSegmentIndex()]
        self.timestamp = self.kilnStatus[keyForTimeStamp()]

        # print("KilnStatus", self.kilnStatus)
        return True

    def setCurSegDisplay(self):
        # update elements based on current Script Status
        # update UI from current script and moData
        # if runningScript, then update ScriptData but
        # if kiln is Idle, then dont update from moData
        self.simulateVar.set(self.kilnScript.simulate)

        if self.curSegIdx < 0 or self.curSegIdx >= self.kilnScript.numSteps():
            msg = "curSegIdx " + str(self.curSegIdx) + " out of range max " + str(self.kilnScript.numSteps())
            log.error(msg)
            mb.showerror("Segment Index Out of Range", message=msg)
            self.curSegIdx = 0
        self.updating = True
        self.curSeg = self.kilnScript.segments[self.curSegIdx]
        self.kilnStateLabel.config(text="KilnState:" + self.stateName)
        self.kilnScriptStateLabel.config(text="Kiln ScriptState:" + self.scriptStateName)

        self.stepSelector.current(self.curSegIdx)
        msg = "Step Index: " + str(self.curSegIdx) + " of " + str(self.kilnScript.numSteps() - 1)
        self.stepIofNLabel.config(text=msg)
        #
        # # now snag the current segment for reference
        # # fill in for current segment: targetTime, dist, hold
        self.temperatureSV.set(str(self.curSeg.targetTemperature))
        self.displacementSV.set(str(self.curSeg.targetDistanceChange))
        self.holdTimeSV.set(str(self.curSeg.holdTimeMinutes))
        self.exhaustBV.set(self.curSeg.exhaustFan)
        self.supportBV.set(curSeg.supportFan)
        self.twelvevBV.set(self.curSeg.v12Relay)
        self.updating = False

    def setData(self):
        # from moData, we only want to update the kilnStatus, unless KilnScriptRunning
        # then we want to update the script state idx, and show that one
        #
        self.getKilnStatus()
        self.setCurSegDisplay()

        if self.prevkilnState == KilnState.RunningScript and self.kilnState == KilnState.Idle:
            # really should have gotten EndScript command but...
            log.debug("noticed kilnState went back to Idle, so endScript")
            self.endScript()

        self.prevkilnState = self.kilnState

        # state is the name or string rep of KilnState
        log.debug("KilnPanel setData Reported state: "+self.stateName)

        self.updateScriptStatusBox()

    def updateScriptStatusBox(self):
        textScriptStatus = json.dumps(self.kilnStatus, indent=4)
        scrollPoint = self.scrolledBox.index("@0,0")  # save and restore scroll point
        self.scrolledBox.delete(1.0, tk.END)
        self.scrolledBox.insert(tk.END, textScriptStatus)
        self.scrolledBox.see(scrollPoint)

    # called on setup and when MoData is updated by server msg
    def updateFromMoData(self):
        self.setData()
        pass

    def endScript(self):
        log.debug("Kiln endScript")
        self.curSegIdx = 0
        self.kilnScript.getSegment(0)
        self.resetRunStop()

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

    def setEditing(self, boolState):
        log.debug("setEditing :"+ str(boolState))
        # if True, enable all edit boxes
        # if False, disable all edits

        pass
    def setRunStop(self):
        self.runBtn.config(state=tk.DISABLED)
        self.stopBtn.config(state=tk.ENABLED)
        # TODO need to disable editing script entirely at this point
        self.setEditing(False)
        # perhaps something akin to the resetBtn stuff

    def resetRunStop(self):
        log.debug("Reset Abort/Run Buttons")
        self.stopBtn.config(state=tk.DISABLED)
        self.runBtn.config(state=tk.ENABLED)
        # TODO reset editing of current step
        self.setEditing(True)

    def on_LoadKilnScript_clicked(self):
        log.debug("on_LoadKilnScript_clicked")
        name = fd.askopenfilename(initialdir=self.last_open_dir,
                                  title="Kiln Script File To Open",
                                  filetypes=[('JSON files', '.json')],
                                  defaultextension='.json')
        if name == None or name == "":
            return  # canceled
        self.filename = name
        log.debug("Load Script from file: " + str(self.filename))
        self.last_open_dir = os.path.dirname(name)
        try:
            retVal = loadScriptFromFile(self.filename)
        except:
            msg = "Failed to load script from " + self.filename
            log.error("Failed to load script from " + self.filename)
            # Error Dialog
            mb.showerror(title="Failed to load script", message=msg)
            return
        log.debug("on_LoadScript  succeeded file: " + self.filename)
        self.kilnScript = retVal
        self.kilnScript.curSegmentIdx = 0  # force load to step 0
        self.setFromScript()

    def on_SaveKilnScript_clicked(self):
        log.debug("on_SaveKilnScript_clicked")
        # ask for Filename, using last directory, and *.csv as filters; if supported
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")
        name = fd.asksaveasfilename(initialdir=self.last_open_dir,
                                    title="File to Save Script",
                                    initialfile=self.filename,
                                    filetypes=[('JSON files', '.json')],
                                    defaultextension='.json')
        print("saveScript to file", name)
        # if ok, then
        if name == None or name == "":
            return
        self.filename = name
        log.debug("saveScript to file: " + str(self.filename))
        self.last_open_dir = os.path.dirname(name)
        self.kilnScript.saveScript(self.filename)

    def on_stepSelectorChanged(self):
        if self.updating == True:
            return  # avoid repeated triggers and stack overflow
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
        log.debug("before Add Segment script is: " + str(self.kilnScript))
        self.kilnScript.addNewSegment()
        self.setFromScript()
        log.debug("after Add Segment script is: " + str(self.kilnScript))
        pass

    def on_RemoveButton_clicked(self):
        # remove current, update display
        log.debug("before Remove Segment script is: " + str(self.kilnScript))
        self.kilnScript.removeCurrentSegment()
        self.setFromScript()
        log.debug("after Remove Segment script is: " + str(self.kilnScript))
        pass

    def on_TargetTempChanged(self, name='', index='', mode=''):
        if self.updating == True: return  # avoid repeated triggers and stack overflow
        log.info("TargetTempChanged " + self.temperatureSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.targetTemperature = int(self.temperatureSV.get())
        log.info("after set temp: " + str(curSeg.targetTemperature))
        pass

    def on_DisplacemenChanged(self, name='', index='', mode=''):
        if self.updating == True: return  # avoid repeated triggers and stack overflow
        log.info("Target displacement Changed " + self.displacementSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.targetDistanceChange = float(self.displacementSV.get())
        log.info("after set displace: " + str(curSeg.targetDistanceChange))
        pass

    def on_holdTimeChanged(self, name='', index='', mode=''):
        if self.updating == True: return  # avoid repeated triggers and stack overflow
        log.info("Hold Time Changed " + self.holdTimeSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.holdTimeMinutes = int(self.holdTimeSV.get())
        log.info("after set hold: " + str(curSeg))
        pass

    def on_stepTimeChanged(self, name='', index='', mode=''):
        if self.updating == True: return  # avoid repeated triggers and stack overflow
        print("PIDStepTime Changed " + self.stepTimeSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.stepTime = int(self.stepTimeSV.get())
        log.info("after set pid: " + str(curSeg))
        pass

    def on_exhaustCk_activate(self, button):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if self.exhaustCk is None: return
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.exhaustFan = self.exhaustBV.get()
        log.info("after toggle exhaust: " + str(curSeg.exhaustFan))

    def on_SupportFan_toggled(self, button):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if self.exhaustCk is None: return
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.supportFan = self.supportBV.get()
        log.info("after toggle support: " + str(curSeg.supportFan))

    def on_12vRelay_toggled(self, button):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if self.exhaustCk is None: return
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.v12Relay = self.twelvevBV.get()
        log.info("after toggle v12Relay: " + str(curSeg.v12Relay))
