# modacGUI kiln Panel 2
# supports multi-step kiln control scripts
# TODO properly connect Panel2.glade with this code
#

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import datetime
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gio, Gdk, Gtk
from gi.repository import GObject as Gobj
import json
from modac.moKeys import *
from modac import moData, moLogger
from modac import moCommand

from kilnControl.kilnState  import *
from kilnControl.kilnScript import *

defaultTargetTemp = 100.0
defaultDisplacement = 5.0
defaultMaxTime = (60*24)
defaultStepTime = 2

class kilnPanel():
    def __init__(self):        
        self.lastState = KilnState.Closed
        #print("initPanel")
        self.label = Gtk.Label("Kiln Ctrl")
        self.timestamp = "none yet"
        self.dataCount = 0
        self.builder = Gtk.Builder.new_from_file("modacGUI/kilnPanel2.glade")
        self.builder.connect_signals(self)
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")
        self.kilnScript = KilnScript()
        self.last_open_dir = "."

        # because i forgot to add one in Glade and its too painful to go back and edit
        self.box = Gtk.VBox()
        
        self.panel = self.builder.get_object("ScriptPanel")

        self.scriptNameBox = self.builder.get_object(keyForScriptName())
        self.scriptDescriptionBox = self.builder.get_object(keyForScriptDescription())
        self.currentSegmentIdxBox = self.builder.get_object(keyForSegmentIndex())

        # GtkSpinButton config(value, lower, upper, step_incr, page_incr, page_size)
        self.targetTSpinner = self.builder.get_object(keyForTargetTemp())
        adj = self.targetTSpinner.get_adjustment()
        adj.configure(defaultTargetTemp, 20.0,800.0, 5, 10, 10)
        
        self.holdTimeSpinner = self.builder.get_object(keyForKilnHoldTime())
        adj = self.holdTimeSpinner.get_adjustment()
        adj.configure(5, 0.0, (30*60.0), 5, 10, 10) # max 30min hold
        
        self.displacementSpinner = self.builder.get_object(keyForTargetDisplacement())
        adj = self.displacementSpinner.get_adjustment()
        adj.configure(defaultDisplacement, 0,100.0, 0.1, 10, 10)

#        self.maxTimeSpinner = self.builder.get_object(keyForMaxTime())
#        adj = self.maxTimeSpinner.get_adjustment()
#        maxMaxTime = 2*24*60 # 2 days, 24 hr/day, 60 min/hr - later convert to sec
#        adj.configure(defaultMaxTime, 1, maxMaxTime, 1, 10, 10)
        
        self.timeStepSpinner = self.builder.get_object(keyForPIDStepTime())
        adj = self.timeStepSpinner.get_adjustment()
        adj.configure(defaultStepTime, 1,100.0, 1, 10, 10)
        
        self.simulateBtn = self.builder.get_object(keyForSimulate())
        # TODO change checkbox label color - default white on gray is terrible
        #   need function to find GTK.Label child and change color to black
        self.simulateBtn.set_active(False) # for debugging start w simulated
        
        ## grab handles on some Buttons for later use
        self.loadBtn = self.builder.get_object("LoadKilnScript")
        self.saveBtn = self.builder.get_object("SaveKilnScript")
        self.runBtn = self.builder.get_object(keyForRunKilnScript())
        self.stopBtn = self.builder.get_object(keyForStopKilnScript())

        self.addBeforeBtn = self.builder.get_object("AddBeforeButton")
        self.addAfterBtn = self.builder.get_object("AddAfterButton")
        self.removeBtn = self.builder.get_object("RemoveButton")

        # and text area to display ScriptStatus
        self.scriptStatusBox = self.builder.get_object(keyForKilnStatus())
        self.scriptStatusBuffer = self.scriptStatusBox.get_buffer()

        # disable Abort until a run starts
        self.stopBtn.set_sensitive(False)
        self.runBtn.set_sensitive(True)

        # fill in script from default values
        self.setFromScript()
        # fill in the readOnly values
        self.update()
        self.box.add(self.panel)

        self.panel.show()
        self.box.show()

    def setFromScript(self):
        # assuming kilnScript is a KilnScript object
        self.scriptNameBox.set_text(self.kilnScript.name)
        self.scriptDescriptionBox.set_text(self.kilnScript.description)
        # self.currSegmentIdex is lable so rest value with             keyForScriptCurrentSegmentIdx(): kilnScript.curSegmentIdx,
        self.currentSegmentIdxBox.set_text("Step Index: "+str(self.kilnScript.curSegmentIdx))

        curSeg = self.kilnScript.segments[self.kilnScript.curSegmentIdx]
        # fill in for current segment: targetTime, dist, hold
        pass

    def update(self):
        log.debug("KilnPanel Update")
        self.setData()
        
    def getKilnStatus(self):
        self.kilnStatus = moData.getValue(keyForKilnStatus())
        if self.kilnStatus == keyForNotStarted():
            self.stateName = keyForNotStarted()
            return False
        self.stateName = self.kilnStatus[keyForState()]
        self.timestamp = self.kilnStatus[keyForTimeStamp()]
        print("KilnStatus", self.kilnStatus)
        return True
        
    def setData(self):
        # TODO most of this (all?) becomes put JSON text into ScriptStatus box
        if not self.getKilnStatus():
            log.debug("kiln not started")
            widget = self.builder.get_object(keyForState())
            widget.set_text(keyForState()+ " : "+ keyForNotStarted())
            return
        
        # state is the name or string rep of KilnState
        log.debug("KilnPanel setData state: "+self.stateName)

        if not self.stateName== KilnState.RunningScript.name:
            # not running script, reset start/abort btns
            self.resetRunAbort()

        # extract kiln current step
        # move display to that step if not already there

        textScriptStatus = json.dumps(self.kilnStatus, indent=4)
        self.scriptStatusBuffer.set_text(textScriptStatus)

    def on_RunKilnScript_clicked(self, button):
        # start kiln schedule
        log.debug("on_RunKilnScript_clicked")
        scriptName = self.scriptNameBox.get_value()
        scriptDescription = self.scriptNameBox.get_value()

        # collect targetTemp, deflection, maxTime, startTime)
        targetT = self.targetTSpinner.get_value()
        
        deflection = self.displacementSpinner.get_value()
        
        maxTime = self.maxTimeSpinner.get_value()
        
        timeStep = self.timeStepSpinner.get_value_as_int()

        simulate = self.simulateBtn.get_active()
        
        kilnHoldTime = self.holdTimeSpinner.get_value_as_int()

        #def startRun(holdTemp=default_holdTemp,
        #             deflectionDist=default_deflectionDist,
        #             maxTime = default_maxTime,
        #             stepTime= default_stepTime):
        param = {
            keyforScriptName(): scriptName,
            keyforScriptDescription():scriptDescripton(),

            # TODO multiple steps
            keyForTargetTemp(): targetT,
            keyForTargetDisplacement(): deflection,
            keyForMaxTime(): maxTime,
            keyForTimeStep(): timeStep,
            keyForSimulate(): simulate,
            keyForKilnHoldTime(): kilnHoldTime,
        }
        
        # Disable Run, Enable Terminate
        self.runBtn.set_sensitive(False)
        self.abortBtn.set_sensitive(True)

        print("\n**** Send RunKiln: ", param)
        moCommand.cmdRunKilnScript(param)
        
    def on_StopKilnScript_clicked(self, button):
        log.debug("onTerminateRun")
        self.resetRunAbort()
        moCommand.cmdStopKilnScript()

    def resetRunAbort(self):
        log.debug("Reset Abort/Run Buttons")
        self.stopBtn.set_sensitive(False)
        self.runBtn.set_sensitive(True)
        
    def onEmergencyOff(self, button):
        log.warn("Emergency OFF clicked")
        moCommand.cmdEmergencyOff()

    def on_LoadKilnScript_clicked(self, button):
        pass

    def on_SaveKilnScript_clicked(self, button):
        log.debug("on_SaveKilnScript_clicked")
        # dialog to get filename
        topLevel = button.get_toplevel()
        dialog = Gtk.FileChooserDialog(
            # title="Select CSV File",
            "Save KilnScript File As:", topLevel,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_current_name(self.filename)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_folder(self.last_open_dir)
        dialog.set_create_folders(True)
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON Files")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)
        response = dialog.run()
        print("FileChooserDialog response: ", response, "OK=",Gtk.ResponseType.OK)
        self.filename = dialog.get_filename()
        self.last_open_dir = dialog.get_current_folder()
        print("filename: ",dialog.get_filename(), " folder:", self.last_open_dir)

        if response != Gtk.ResponseType.CANCEL:
            self.kilnScript.saveScript(self.filename)
            print("wrote file")

        dialog.destroy()

