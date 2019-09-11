# modacGUI kiln Panel 1
# new kiln.startRun: takes holdTemp, deflectionDist, maxTime, stepTime
# these could be fields in Kiln page
# also should display Kiln.status

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gio, Gdk, Gtk
from gi.repository import GObject as Gobj

from modac.moKeys import *
from modac import moData, moLogger
from modac import moCommand
#import kilnControl
#from kilnControl import kiln

defaultTargetTemp = 500
defaultDeflection = 5.1
defaultMaxTime = (60*24)
defaultStepTime = 1

class kilnPanel():
    def getKilnStatus(self):
        self.kilnStatus = moData.getValue(keyForKilnStatus())
        print("KilnStatus", self.kilnStatus)
        
    def __init__(self):        
        #print("initPanel")
        self.label = Gtk.Label("Kiln Ctrl")

        self.dataCount = 0
        self.builder = Gtk.Builder.new_from_file("modacGUI/kilnPanel.glade")
        self.builder.connect_signals(self)

        # because i forgot to add one in Glade and its too painful to go back and edit
        self.box = Gtk.VBox()
        
        self.panel = self.builder.get_object("Panel")
        
        # Spinner config(value, lower, upper, step_incr, page_incr, page_size)
        self.targetTSpinner = self.builder.get_object(keyForTargetTemp())
        adj = self.targetTSpinner.get_adjustment()
        adj.configure(defaultTargetTemp, 20.0,800.0, 5, 10, 10)
        
        self.deflectionSpinner = self.builder.get_object(keyForDeflectionDist())
        adj = self.deflectionSpinner.get_adjustment()
        adj.configure(defaultDeflection, 0,100.0, 0.1, 10, 10)

        self.maxTimeSpinner = self.builder.get_object(keyForMaxTime())
        adj = self.maxTimeSpinner.get_adjustment()
        adj.configure(defaultMaxTime, 10, 10000.0, 1, 10, 10)
        
        self.timeStepSpinner = self.builder.get_object(keyForTimeStep())
        adj = self.timeStepSpinner.get_adjustment()
        adj.configure(defaultStepTime, 5,100.0, 1, 10, 10)
        
        self.simulateBtn = self.builder.get_object(keyForSimulate())
        self.simulateBtn.set_active(False)
        
        # fill in the readOnly values
        self.update()
        self.box.add(self.panel)

        self.panel.show()
        self.box.show()

    def update(self):
        self.getData()
        
    def getData(self):
        self.getKilnStatus()
        
        widget = self.builder.get_object(keyForState())
        widget.set_text(keyForState()+ " : "+ self.kilnStatus[keyForState()])

        widget = self.builder.get_object(keyForStartTime())
        widget.set_text(keyForStartTime()+ " : "+ self.kilnStatus[keyForStartTime()])

        widget = self.builder.get_object(keyForRuntime())
        widget.set_text("{0} : {1:5.3f}".format(keyForRuntime(),self.kilnStatus[keyForRuntime()]) )

        widget = self.builder.get_object(keyForStartDist())
        widget.set_text("{0} : {1:5.3f}".format(keyForStartDist(),self.kilnStatus[keyForStartDist()]) )

        widget = self.builder.get_object(keyForTargetDist())
        widget.set_text("{0} : {1:5.3f}".format(keyForTargetDist(),self.kilnStatus[keyForTargetDist()]) )

        widget = self.builder.get_object(keyForCurrDeflection())
        widget.set_text("{0} : {1:5.3f}".format(keyForCurrDeflection(),self.kilnStatus[keyForCurrDeflection()]) )

        widget = self.builder.get_object(keyForCurrTemp())
        widget.set_text("{0} : {1:5.2f}".format(keyForCurrTemp(),self.kilnStatus[keyForCurrTemp()]) )

        widget = self.builder.get_object(keyForCurrDeflection())
        widget.set_text("{0} : {1:5.3f}".format(keyForCurrDeflection(),self.kilnStatus[keyForCurrDeflection()]) )

        widget = self.builder.get_object(keyForAllHeaters())
        boolStr = "foo"
        if self.kilnStatus[keyForAllHeaters()]:
            boolStr = "ON"
        else:
            boolStr = "OFF"
        widget.set_text(keyForAllHeaters()+ " : " + boolStr)
        
    def onStartKiln(self, button):
        # start kiln schedule
        log.debug("onStartKiln")
        # collect targetTemp, deflection, maxTime, startTime)
        targetT = self.targetTSpinner.get_value()
        
#        widget = self.builder.get_object(keyForDeflectionDist())
        deflection = self.deflectionSpinner.get_value()
        
#        widget = self.builder.get_object(keyForMaxTime())
        maxTime = self.maxTimeSpinner .get_value()
        
#        widget = self.builder.get_object(keyForTimeStep())
        timeStep = self.timeStepSpinner.get_value_as_int()

        simulate = self.simulateBtn.get_active()

        #def startRun(holdTemp=default_holdTemp,
        #             deflectionDist=default_deflectionDist,
        #             maxTime = default_maxTime,
        #             stepTime= default_stepTime):
        param = {
            keyForTargetTemp(): targetT,
            keyForDeflectionDist(): deflection,
            keyForMaxTime(): maxTime,
            keyForTimeStep(): timeStep,
            keyForSimulate(): simulate, 
        }
        print("\n**** Send RunKiln: ", param)
        moCommand.cmdRunKiln(param)
        
    def onTerminateRun(self, button):
        log.debug("onTerminateRun")
        moCommand.cmdAbortKiln()



        