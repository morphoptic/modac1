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
from .moPanelTempPlot import moPanelTempPlot


### couple validators for TextEntry widgets
def validPositiveInt(s):  # validates string holds positive int
    try:
        i = int(s)
        if i < 0:
            return False
        return True
    except ValueError:
        if validPositiveFloat(s):
            return True
        return False

def asPositiveInt(s):
    if validPositiveFloat(s):
        f = float(s)
        i = int(f)
        return i
    if validPositiveInt(s):
        return int(s)
    return 0

def validPositiveFloat(s):
    try:
        f = float(s)
        if f < 0.0:
            return False
        return True
    except ValueError:
        return False


class moTabKiln():
    def getTitle(self):
        return self.tabTitle

    def __init__(self, frame):
        log.debug(" initialize moTabKiln top")
        self.frame = frame
        self.tabTitle = "Kiln Control"

        self.updating = True  # used when updating current script gui to avoid stack overflow

        # some generic variables
        self.curSegIdx = 0
        self.timestamp = "none yet"
        self.dataCount = 0
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")
        self.last_open_dir = "./kilnScripts"
        self.kilnState = KilnState.Closed
        self.lastState = KilnState.Closed
        self.prevkilnState = KilnState.Closed

        self.kilnScript = KilnScript()  # need at least one simple
        self.curSeg = self.kilnScript.segments[self.curSegIdx]

        # TODO: stateName/scriptStateName could be tk.StringVar()
        self.kilnStateName = str(self.kilnState)
        self.scriptStateName = str(KilnScriptState.Unknown)

        self.kilnStatus = None  # returned by moData
        # some vars needed by UI elements
        self.nameSV = tk.StringVar(self.frame)
        self.descriptionSV = tk.StringVar(self.frame)
        self.temperatureSV = tk.StringVar(self.frame)
        self.stepTimeSV = tk.StringVar(self.frame)
        self.displacementSV = tk.StringVar(self.frame)
        self.exhaustBV = tk.BooleanVar(self.frame, False)
        self.supportBV = tk.BooleanVar(self.frame, False)
        self.holdTimeSV = tk.StringVar(self.frame)
        self.v12RelayBV = tk.BooleanVar(self.frame, False)
        self.simulateVar = tk.BooleanVar(self.frame, False)
        # fwd reference ui elements as None (also keeps list to set Disable/Normal)
        self.simulateCk = None
        self.kilnStateLabel = None
        self.kilnScriptStateLabel = None
        self.nameTxtBox = None
        self.descrTxtBox = None
        self.LoadBtn = None
        self.SaveBtn = None
        self.runBtn = None
        self.stopBtn = None
        self.stepIofNLabel = None
        self.stepSelector = None
        self.addBtn = None
        self.removeBtn = None

        self.targetTempEntry = None
        self.displacementEntry = None
        self.holdTimeEntry = None
        self.stepTimeEntry = None

        self.exhaustCk = None
        self.supportCk = None
        self.twelveVCk = None

        log.debug(" initialize moTabKiln build UI panels")

        # now build the UI Panel
        # statusFrame: simulate CkBox; KilnState; KilnScriptState
        # infoFrame: scriptBtnFrame; scriptNameDescrFrame
        #    infoBtnFrame: Load; Save; Run Stop
        #    infoTxtFrame: Name; Description
        # scriptStepFrame: stepBtnFrame; stepDataFrame; stepScrollFrame
        #    stepBtnFrame: stepSelect; Add; Remove
        #    stepDataFrame: TargetTempSelect; displacement; holdTime; exhaust;support; 12v; pidStepTime
        #    scrollFrame: scroll box of kilnStatus json
        # tempPlotFrame: moPanelTempPlot

        ############
        self.build_StatusFrame()
        ############
        self.build_InfoFrame()

        log.debug(" initialize moTabKiln build script Step")

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

        stepScrollFrame = tk.Frame(self.scriptStepFrame, bg="blue")
        self.scrolledBox = tk.scrolledtext.ScrolledText(stepScrollFrame, height=12)
        self.scrolledBox.insert(tk.END, "This is\n the first\n text")
        self.scrolledBox.pack(fill=tk.Y, )
        stepScrollFrame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # self.scriptStepFrame.pack(side=tk.BOTTOM, pady=2, expand=1, fill=tk.BOTH)
        self.scriptStepFrame.pack(pady=1, expand=1, fill=tk.BOTH)

        self.temperatureFrame = tk.Frame(self.frame, bg="blue")
        self.moTempPanel = moPanelTempPlot(self.temperatureFrame)
        self.temperatureFrame.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

        ############
        self.updateFromScript()
        self.updating = False  # used when updating current script gui to avoid stack overflow
        self.frame.pack(fill=tk.BOTH, expand=1)

    def build_InfoFrame(self):
        # infoFrame: scriptBtnFrame; scriptNameDescrFrame
        #    infoBtnFrame: Load; Save; Run Stop
        #    infoTxtFrame: Name; Description
        log.debug(" build_InfoFrame top")

        infoFrame = tk.Frame(self.frame, bg='azure')
        ##
        infoBtnFrame = tk.Frame(infoFrame, bg='azure2')
        self.LoadBtn = tk.Button(infoBtnFrame, text="Load Script",
                                 command=self.on_LoadKilnScript_clicked)
        self.LoadBtn.pack()
        self.SaveBtn = tk.Button(infoBtnFrame, text="Save Script",
                                 command=self.on_SaveKilnScript_clicked)
        self.SaveBtn.pack()
        self.runBtn = tk.Button(infoBtnFrame, text="Run Script",
                                command=self.on_RunKilnScript_clicked)
        self.runBtn.pack()
        self.stopBtn = tk.Button(infoBtnFrame, text="Stop Script",
                                 command=self.on_StopKilnScript_clicked,
                                 state=tk.DISABLED)
        self.stopBtn.pack()
        infoBtnFrame.pack(side=tk.LEFT)
        ##
        infoTxtFrame = tk.Frame(infoFrame, bg='azure2')
        #
        log.debug(" build_InfoFrame b4 name")

        nameFrame = tk.Frame(infoTxtFrame, bg='azure3')
        nameLabel = tk.Label(nameFrame, text="Name:")
        nameLabel.pack(side=tk.LEFT, fill=tk.X)
        self.nameSV.trace_add("write", self.on_NameChanged)
        self.nameTxtBox = tk.Entry(nameFrame, textvariable=self.nameSV)
        self.nameTxtBox.insert(tk.END, "nameTxtBox tk starting")
        self.nameTxtBox.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        nameFrame.pack(side=tk.TOP, fill=tk.X)
        #
        log.debug(" build_InfoFrame b4 descrFrame")
        descrFrame = tk.Frame(infoTxtFrame, bg='azure4')
        descrLabel = tk.Label(descrFrame, text="Description:")
        descrLabel.pack(side=tk.LEFT, fill=tk.BOTH)
        # while Entry can have textvariable; Text/ScrolledText cannot
        # so we try a lil magic from
        # https://stackoverflow.com/questions/10593027/how-can-i-connect-a-stringvar-to-a-text-widget-in-python-tkinter
        self.descrTxtBox = tk.Text(descrFrame, height=4)#, textvariable=self.descriptionSV)
        self.descrTxtBox.insert(tk.END, "descrTxtBox tk starting")
        self.descrTxtBox.bind('<KeyRelease>', self.on_DescriptionChanged)
        self.descrTxtBox.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        descrFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        infoTxtFrame.pack(side=tk.RIGHT, fill=tk.BOTH)
        ##
        infoFrame.pack(pady=1, fill=tk.X)
        log.debug(" build_InfoFrame done")

    def build_StepBtnFrame(self, parentFrame):
        stepBtnFrame = tk.Frame(parentFrame)
        scriptStepsLabel = tk.Label(stepBtnFrame, text="Script Steps")
        scriptStepsLabel.pack(side=tk.TOP)
        self.stepSelector = ttk.Combobox(stepBtnFrame, values=["0"], exportselection=0,
                                         state="readonly", justify="center", width=4)
        self.stepSelector.bind("<<ComboboxSelected>>", self.on_stepSelectorChanged)
        self.stepSelector.pack(fill=tk.X)
        self.addBtn = tk.Button(stepBtnFrame, text="Add",
                                command=self.on_AddButton_clicked)
        self.addBtn.pack(fill=tk.X)
        self.removeBtn = tk.Button(stepBtnFrame, text="Remove",
                                   command=self.on_RemoveButton_clicked)
        self.removeBtn.pack(fill=tk.X)
        stepBtnFrame.pack(side=tk.LEFT, fill=tk.Y)

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
        self.targetTempEntry = tk.Entry(targetTempFrame, textvariable=self.temperatureSV,
                                        validatecommand=validPositiveInt)
        self.targetTempEntry.pack(side=tk.RIGHT)
        targetTempFrame.pack()
        #
        displacementFrame = tk.Frame(stepDataFrame)
        displacementLabel = tk.Label(displacementFrame, text="Displacement (mm):")
        displacementLabel.pack(side=tk.LEFT)
        self.displacementSV.trace_add("write", self.on_DisplacemenChanged)
        self.displacementEntry = tk.Entry(displacementFrame, textvariable=self.displacementSV,
                                          validatecommand=validPositiveFloat)
        self.displacementEntry.pack(side=tk.RIGHT)
        displacementFrame.pack()
        #
        holdTimeFrame = tk.Frame(stepDataFrame)
        holdTimeLabel = tk.Label(holdTimeFrame, text="Hold Time (minutes):")
        holdTimeLabel.pack(side=tk.LEFT)
        self.holdTimeSV.trace_add("write", self.on_holdTimeChanged)
        self.holdTimeEntry = tk.Entry(holdTimeFrame, textvariable=self.holdTimeSV,
                                      validatecommand=validPositiveInt)
        self.holdTimeEntry.pack(side=tk.RIGHT)
        holdTimeFrame.pack()
        #
        stepTimeFrame = tk.Frame(stepDataFrame)
        stepTimeLabel = tk.Label(stepTimeFrame, text="PID Step Time (seconds):")
        stepTimeLabel.pack(side=tk.LEFT)
        self.stepTimeSV.trace_add("write", self.on_stepTimeChanged)
        self.stepTimeEntry = tk.Entry(stepTimeFrame, textvariable=self.stepTimeSV,
                                      validatecommand=validPositiveInt)
        self.stepTimeEntry.pack(side=tk.RIGHT)
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
        self.twelveVCk = tk.Checkbutton(stepDataFrame, text='KilnHeater 12V',
                                        variable=self.v12RelayBV, onvalue=True, offvalue=False,
                                        command=self.on_12vRelay_toggled)
        self.twelveVCk.pack(fill=tk.X)

        stepDataFrame.pack(fill=tk.BOTH, expand=1)

    def build_StatusFrame(self):
        statusFrame = tk.Frame(self.frame, bg="blue")
        #
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

    def updateFromScript(self):
        log.debug("Update From Script ")
        # used in init and after loading script
        # Tk uses *Var while GTK and various set methods
        self.updating = True  # avoid infinite loops

        self.simulateVar.set(self.kilnScript.simulate)
        if self.kilnScript.simulate:
            self.simulateCk.config(bg="yellow")
        else:
            self.simulateCk.config(bg="white")

        # assuming kilnScript is a KilnScript object
        self.nameSV.set(self.kilnScript.name)

        self.descrTxtBox.delete(1.0, tk.END)
        self.descrTxtBox.insert(1.0, self.kilnScript.description)

        # keyForScriptCurrentSegmentIdx(): kilnScript.curSegmentIdx,
        self.curSegIdx = self.kilnScript.curSegmentIdx
        indices = [i for i in range(0, self.kilnScript.numSteps())]
        self.stepSelector.config(values=indices)

        self.updateScriptElements()

        self.updating = False

    def getKilnStatusFromMoData(self):
        # status message received: update text and perhaps some others
        # kilnStatus is Dictionary from Json msg from MODAC Server
        self.kilnStatus = moData.getValue(keyForKilnStatus())

        # extract variables we need
        self.timestamp = self.kilnStatus[keyForTimeStamp()]
        self.kilnStateName = self.kilnStatus[keyForState()]
        self.kilnState = KilnState[self.kilnStateName]
        self.scriptStateName = self.kilnStatus[keyForKilnScriptState()]

        if self.kilnState == KilnState.RunningScript:
            # kiln thinks it is running, so lock out edits and up date display from values
            self.curSegIdx = self.kilnStatus[keyForSegmentIndex()]

        # print("KilnStatus", self.kilnStatus)
        return True

    def updateScriptElements(self):
        # update elements based on current Script Status
        # update UI from current script and moData
        log.debug("updateScript Elements")

        if self.curSegIdx < 0 or self.curSegIdx >= self.kilnScript.numSteps():
            msg = "curSegIdx " + str(self.curSegIdx) + " out of range max " + str(self.kilnScript.numSteps())
            log.error(msg)
            mb.showerror("Segment Index Out of Range", message=msg)
            self.curSegIdx = 0

        self.updating = True

        self.simulateVar.set(self.kilnScript.simulate)

        self.curSeg = self.kilnScript.segments[self.curSegIdx]
        self.kilnStateLabel.config(text="KilnState:" + self.kilnStateName)
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
        self.supportBV.set(self.curSeg.supportFan)
        log.debug("Set 12v Relay BV and thus ckbox " + str(self.curSeg.v12Relay))
        self.v12RelayBV.set(self.curSeg.v12Relay)
        self.stepTimeSV.set(str(self.curSeg.stepTime))
        self.updating = False

    def updateScriptStatusElements(self):
        # kilnStatus Elements
        self.kilnStateLabel.config(text="KilnState: " + self.kilnStateName)
        self.kilnScriptStateLabel.config(text="KilnState: " + self.scriptStateName)
        # basically only the scroll box showing the status from moData and thus MODAC Server
        textScriptStatus = json.dumps(self.kilnStatus, indent=4)
        # TODO: index/see should scroll back to same point but doesnt
        scrollPoint = self.scrolledBox.index("@0,0")  # save and restore scroll point
        self.scrolledBox.delete(1.0, tk.END)
        self.scrolledBox.insert(tk.END, textScriptStatus)
        self.scrolledBox.see("end")  # str(scrollPoint))

    # called when MoData is updated by server msg
    def updateFromMoData(self):
        self.getKilnStatusFromMoData()
        if self.prevkilnState == KilnState.RunningScript and self.kilnState == KilnState.Idle:
            # really should have gotten EndScript command but...
            log.debug("noticed kilnState went back to Idle, so endScript")
            self.endScript()

        self.prevkilnState = self.kilnState

        # state is the name or string rep of KilnState
        log.debug("KilnPanel setData Reported state: " + self.kilnStateName)

        if self.kilnState == KilnState.RunningScript:
            # only update the script elements when running; to show current segment
            self.curSegIdx = self.kilnStatus[keyForSegmentIndex()]
            self.updateScriptElements()
            print("Script is in segment " + str(self.curSegIdx))

        self.updateScriptStatusElements()  # json scrolling text box
        self.moTempPanel.updateFromMoData()

        pass

    def endScript(self):
        log.debug("Kiln endScript")
        self.curSegIdx = 0
        self.kilnScript.getSegment(0)
        self.setEditingAllowed(True)

    def on_SimulateCk_activate(self):
        # ck box updated, move value to script
        if self.simulateCk is None:
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
        self.setEditingAllowed(False)

        print("\n**** Send RunKiln: ", param)
        moCommand.cmdRunKilnScript(param)

    def on_StopKilnScript_clicked(self):
        log.debug("onTerminateRun")
        self.endScript()
        moCommand.cmdStopKilnScript()
        self.setEditingAllowed(True)

    def setEditingAllowed(self, boolState):
        log.debug("setEditingAllowed :" + str(boolState))
        # if True, enable all edit boxes
        # if False, disable all edits
        if boolState:
            # state=tk.NORMAL, bg="light grey"
            self.runBtn.config(state=tk.NORMAL, bg="light grey")
            self.stopBtn.config(state=tk.DISABLED, bg="pink")
            self.LoadBtn.config(state=tk.NORMAL, bg="light grey")
            self.simulateCk.config(state=tk.NORMAL, bg="light grey")
            self.nameTxtBox.config(state=tk.NORMAL, bg="light grey")
            self.descrTxtBox.config(state=tk.NORMAL, bg="light grey")
            self.LoadBtn.config(state=tk.NORMAL, bg="light grey")
            self.SaveBtn.config(state=tk.NORMAL, bg="light grey")
            self.stepIofNLabel.config(state=tk.NORMAL, bg="light grey")
            self.stepSelector.config(state=tk.NORMAL)  # , bg="light grey")
            self.addBtn.config(state=tk.NORMAL, bg="light grey")
            self.removeBtn.config(state=tk.NORMAL, bg="light grey")

            self.targetTempEntry.config(state=tk.NORMAL, bg="light grey")
            self.displacementEntry.config(state=tk.NORMAL, bg="light grey")
            self.holdTimeEntry.config(state=tk.NORMAL, bg="light grey")
            self.stepTimeEntry.config(state=tk.NORMAL, bg="light grey")

            self.exhaustCk.config(state=tk.NORMAL, bg="light grey")
            self.supportCk.config(state=tk.NORMAL, bg="light grey")
            self.twelveVCk.config(state=tk.NORMAL, bg="light grey")
        else:  # state=tk.DISABLED, bg="pink"
            self.runBtn.config(state=tk.DISABLED, bg="pink")
            self.stopBtn.config(state=tk.NORMAL, bg="light grey")
            self.LoadBtn.config(state=tk.DISABLED, bg="pink")
            self.simulateCk.config(state=tk.DISABLED, bg="pink")
            self.nameTxtBox.config(state=tk.DISABLED, bg="pink")
            self.descrTxtBox.config(state=tk.DISABLED, bg="pink")
            self.LoadBtn.config(state=tk.DISABLED, bg="pink")
            self.SaveBtn.config(state=tk.DISABLED, bg="pink")
            self.stepIofNLabel.config(state=tk.DISABLED, bg="pink")
            self.stepSelector.config(state=tk.DISABLED)  # , bg="pink")
            self.addBtn.config(state=tk.DISABLED, bg="pink")
            self.removeBtn.config(state=tk.DISABLED, bg="pink")

            self.targetTempEntry.config(state=tk.DISABLED, bg="pink")
            self.displacementEntry.config(state=tk.DISABLED, bg="pink")
            self.holdTimeEntry.config(state=tk.DISABLED, bg="pink")
            self.stepTimeEntry.config(state=tk.DISABLED, bg="pink")

            self.exhaustCk.config(state=tk.DISABLED, bg="pink")
            self.supportCk.config(state=tk.DISABLED, bg="pink")
            self.twelveVCk.config(state=tk.DISABLED, bg="pink")

        pass

    def on_LoadKilnScript_clicked(self):
        log.debug("on_LoadKilnScript_clicked")
        name = fd.askopenfilename(initialdir=self.last_open_dir,
                                  title="Kiln Script File To Open",
                                  filetypes=[('JSON files', '.json')],
                                  defaultextension='.json')
        if name is None or name == "":
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
        self.updateFromScript()
        log.debug("after Load update is "+str(self.updating))

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
        if name is None or name == "":
            return
        self.filename = name
        log.debug("saveScript to file: " + str(self.filename))
        self.last_open_dir = os.path.dirname(name)
        self.kilnScript.saveScript(self.filename)

    def on_stepSelectorChanged(self, event):
        if self.updating == True:
            return  # avoid repeated triggers and stack overflow
        # a step was selected... make that index current
        curId = self.stepSelector.current()
        log.debug("stepSelector Changed id now " + str(curId) + " was " + str(self.kilnScript.curSegmentIdx))
        if curId == self.kilnScript.curSegmentIdx:
            log.debug("same as current, ignore")
        else:
            log.debug("new current, update")
            self.kilnScript.getSegment(curId)
            self.updateFromScript()

    def on_AddButton_clicked(self):
        # add one to end, update display
        log.debug("before Add Segment script is: " + str(self.kilnScript))
        self.kilnScript.addNewSegment()
        self.updateFromScript()
        log.debug("after Add Segment script is: " + str(self.kilnScript))
        pass

    def on_RemoveButton_clicked(self):
        # remove current, update display
        log.debug("before Remove Segment script is: " + str(self.kilnScript))
        self.kilnScript.removeCurrentSegment()
        self.updateFromScript()
        log.debug("after Remove Segment script is: " + str(self.kilnScript))
        pass

    def on_NameChanged(self, name='', index='', mode=''):
        log.debug("on_NameChanged top" + self.temperatureSV.get())
        if self.updating:
            # log.debug("on_NameChanged updating")
            return  # avoid repeated triggers and stack overflow
        self.kilnScript.name = self.nameSV.get()
        #log.debug("on_NameChanged after" + self.temperatureSV.get())


    def on_DescriptionChanged(self, event):
        # log.debug("on_DescriptionChanged top")
        #print("on_DescriptionChanged top", event)
        if self.updating:
            # log.debug("on_DescriptionChanged updating")
            return  # avoid repeated triggers and stack overflow
        self.kilnScript.description = self.descrTxtBox.get("1.0", tk.END)

    def on_TargetTempChanged(self, name='', index='', mode=''):
        # log.debug("TargetTempChanged top" + self.temperatureSV.get())
        if self.updating:
            # log.debug("TargetTempChanged updating")
            return  # avoid repeated triggers and stack overflow
        if not validPositiveInt(self.temperatureSV.get()):
            log.debug("TargetTempChanged not positive int")
            return
        log.debug("TargetTempChanged middle" + self.temperatureSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        i = asPositiveInt(self.temperatureSV.get())
        curSeg.targetTemperature = i
        # log.info("after set temp: " + str(curSeg.targetTemperature))
        # log.debug("Segment now reads:" + str(curSeg))
        # log.debug("Compare :" + str(self.kilnScript.getCurrentSegment()))
        pass

    def on_DisplacemenChanged(self, name='', index='', mode=''):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if not validPositiveFloat(self.temperatureSV.get()):
            return
        log.info("Target displacement Changed " + self.displacementSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.targetDistanceChange = float(self.displacementSV.get())
        log.info("after set displace: " + str(curSeg.targetDistanceChange))
        pass

    def on_holdTimeChanged(self, name='', index='', mode=''):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if not validPositiveInt(self.temperatureSV.get()):
            return
        log.info("Hold Time Changed " + self.holdTimeSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        i = asPositiveInt(self.holdTimeSV.get())
        curSeg.holdTimeMinutes = i
        log.info("after set hold: " + str(curSeg))
        pass

    def on_stepTimeChanged(self, name='', index='', mode=''):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if not validPositiveInt(self.temperatureSV.get()):
            return
        print("PIDStepTime Changed " + self.stepTimeSV.get())
        curSeg = self.kilnScript.getCurrentSegment()
        i = asPositiveInt(self.stepTimeSV.get())
        if i < 1: # asPositive might make it 0
            i = 1
        curSeg.stepTime = i
        log.info("after set pid: " + str(curSeg))
        pass

    def on_exhaustCk_activate(self):  # , button):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if self.exhaustCk is None: return
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.exhaustFan = self.exhaustBV.get()
        log.info("after toggle exhaust: " + str(curSeg.exhaustFan))

    def on_SupportFan_toggled(self):  # , button):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if self.exhaustCk is None: return
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.supportFan = self.supportBV.get()
        log.info("after toggle support: " + str(curSeg.supportFan))

    def on_12vRelay_toggled(self):  # , button):
        if self.updating: return  # avoid repeated triggers and stack overflow
        if self.twelveVCk is None: return
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.v12Relay = self.v12RelayBV.get()
        log.info("after toggle v12Relay: " + str(curSeg.v12Relay))
