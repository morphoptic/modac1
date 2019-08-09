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
from kilnControl import kiln

class kilnPanel():
    def __init__(self):        
        #print("initPanel")
        self.label = Gtk.Label("Kiln Ctrl")

        self.dataCount = 0
        builder = Gtk.Builder.new_from_file("modacGUI/kilnPanel.glade")
        builder.connect_signals(self)

        # because i forgot to add one in Glade and its too painful to go back and edit
        self.box = Gtk.VBox()
        
        self.panel = builder.get_object("Panel")
        self.statusLabels = []

        self.box.add(self.panel)

        self.panel.show()
        self.box.show()

    def update(self):
        self.getData()
        
    def getData(self):
        if kiln == None:
            return
        kilnStaus = kiln.getStatus()
        
        
    def on_StartSchedule_activate(self, button):
        # start kiln schedule
        pass
    def on_AbortSchedule_activate(self, button):
        pass
    
        