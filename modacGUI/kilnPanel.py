# modacGUI kiln Panel 1

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
import kilnControl
from kilnControl import kiln

class kilnPanel():
    def getKilnStatus(self):
        if kiln.kiln == None:
            kiln.startKiln()
            print("should have created kiln there")
        self.kilnStatus = kiln.kiln.get_state()
        print("KilnStatus", self.kilnStatus)
        
    def __init__(self):        
        #print("initPanel")
        self.label = Gtk.Label("Kiln Ctrl")

        self.dataCount = 0
        builder = Gtk.Builder.new_from_file("modacGUI/kilnPanel.glade")
        builder.connect_signals(self)

        # because i forgot to add one in Glade and its too painful to go back and edit
        self.box = Gtk.VBox()
        
        self.panel = builder.get_object("Panel")
        self.labels = {}
        self.getKilnStatus()
        for key,value in self.kilnStatus.items():
            self.labels[key] = builder.get_object(key)
        print (self.labels)

        self.update()
        self.box.add(self.panel)

        self.panel.show()
        self.box.show()

    def update(self):
        self.getData()
        
    def getData(self):
        self.getKilnStatus()
        for key,value in self.kilnStatus.items():
            l = self.labels[key]
            if not l == None:
                t = key +": "+ str(value)
                l.set_text(t)
        
    def on_StartSchedule_clicked(self, button):
        # start kiln schedule
        log.debug("StartSchedule")
        moCommand.cmdRunKiln()
        
    def on_AbortSchedule_clicked(self, button):
        log.debug("AbortSchedule")
        moCommand.cmdAbortKiln()



        