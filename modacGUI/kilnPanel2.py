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
        print("init kilnPanel")
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

        # script data at the top
        self.scriptNameBox = self.builder.get_object(keyForScriptName())
        self.scriptDescriptionBox = self.builder.get_object(keyForScriptDescription())
        self.currentSegmentIdxBox = self.builder.get_object(keyForSegmentIndex())

        # segment Selector
        self.segmentSelector = self.builder.get_object("stepSelector")
        self.segmentListModel = Gtk.ListStore(str) #self.builder.get_object("ScriptStepListStore")
        self.segmentSelector.set_model(self.segmentListModel)
        self.stepIdxCell = Gtk.CellRendererText()
        self.segmentSelector.pack_start(self.stepIdxCell,True)
        self.segmentSelector.add_attribute(self.stepIdxCell,'text',0)

        # segment data
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

        self.exhaustFanBtn = self.builder.get_object(keyForExhaustFan())
        self.supportFanBtn = self.builder.get_object(keyForSupportFan())

        ## grab handles on some Buttons for later use
        self.loadBtn = self.builder.get_object("LoadKilnScript")
        self.saveBtn = self.builder.get_object("SaveKilnScript")
        self.runBtn = self.builder.get_object(keyForRunKilnScript())
        self.stopBtn = self.builder.get_object(keyForStopKilnScript())

        self.addBtn = self.builder.get_object("AddButton")
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

        # combo box
        self.segmentListModel.clear()
        for i in range(len(self.kilnScript.segments)):
            s = [str(i)]
            print("add idx to listModel "+ str(s))
            self.segmentListModel.append(s)
        self.segmentSelector.set_active(self.kilnScript.curSegmentIdx)

        self.curSeg = self.kilnScript.segments[self.kilnScript.curSegmentIdx]
        # fill in for current segment: targetTime, dist, hold
        self.targetTSpinner.set_value(self.curSeg.targetTemperature)
        self.displacementSpinner.set_value(self.curSeg.targetDistanceChange)
        self.holdTimeSpinner.set_value(self.curSeg.holdTimeMinutes)
        self.timeStepSpinner.set_value(self.curSeg.stepTime)
        self.exhaustFanBtn.set_active(self.curSeg.exhaustFan)
        self.supportFanBtn.set_active(self.curSeg.supportFan)

        # update the StepSelector

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
        # TODO reset editing of current step
        
    def onEmergencyOff(self, button):
        log.warning("Emergency OFF clicked")
        moCommand.cmdEmergencyOff()

    def on_LoadKilnScript_clicked(self, button):
        # TODO implement loadScript dialog + parsing, dialog here, json to obj in kilnScript
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
                     Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )
        # new name with current time
        self.filename = datetime.datetime.now().strftime("kilnScript_%Y%m%d_%H_%M.json")

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

    def on_KilnTargetTemp_value_changed(self, button):
        newV = button.get_value()
        log.info("TargetTempChanged " + str(newV))
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.targetTemperature = newV
        log.info("after set temp: "+str(curSeg))
        pass

    def on_KilnTargetDisplacement_value_changed(self, button):
        newV = button.get_value()
        log.info("Target displacement Changed " + str(newV))
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.targetDistanceChange = newV
        log.info("after set displace: "+str(curSeg))
        pass

    def on_KilnHoldTime_value_changed(self, button):
        newV = button.get_value()
        log.info("Hold Time Changed " + str(newV))
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.holdTimeMinutes = newV
        log.info("after set hold: "+str(curSeg))
        pass

    def on_PIDStepTime_value_changed(self, button):
        newV = button.get_value()
        print("PIDStepTime Changed " + str(newV))
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.stepTime = newV
        log.info("after set pid: "+str(curSeg))
        pass

    def on_ExhaustFan_toggled(self,button):
        state = button.get_active()
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.exhaustFan = state
        log.info("after toggle exhaust: "+str(curSeg))

    def on_SupportFan_toggled(self,button):
        state = button.get_active()
        curSeg = self.kilnScript.getCurrentSegment()
        curSeg.supportFan = state
        log.info("after toggle support: "+str(curSeg))

    def on_AddButton_clicked(self, button):
        # add one to end, update display
        log.debug("before Add Segment script is: "+str(self.kilnScript))
        self.kilnScript.addNewSegment()
        self.setFromScript()
        log.debug("after Add Segment script is: "+str(self.kilnScript))
        pass

    def on_RemoveButton_clicked(self, button):
        # remove current, update display
        log.debug("before Remove Segment script is: "+str(self.kilnScript))
        self.kilnScript.removeCurrentSegment()
        self.setFromScript()
        log.debug("after Remove Segment script is: "+str(self.kilnScript))
        pass

    def on_stepSelector_changed(self,selector):
        # a step was selected... make that index current
        curId = selector.get_active()
        log.debug("stepSelector Changed")
        if curId == self.kilnScript.curSegmentIdx:
            log.debug("same as current, ignore")
        else:
            log.debug("new current, update")
            self.kilnScript.getSegment(curId)
            self.setFromScript()

