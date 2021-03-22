# modacGUI ad16Panel Panel 1

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

class binaryOutPanel():
    def __init__(self):        
        #print("initRelayPanel")
        self.label = Gtk.Label("BinaryOut/Relay Ctrl")

        self.dataCount = 0
        builder = Gtk.Builder.new_from_file("modacGUI/binaryOutPanel.glade")
        builder.connect_signals(self)

        # because i forgot to add one in Glade and its too painful to go back and edit
        self.box = Gtk.VBox()
        
        self.panel = builder.get_object("Panel")
        self.relayBtns = []
        self.relayLabels = []
        states = moData.getValue(keyForBinaryOut())
        assert len(states) == moData.numBinaryOut()
        for i in range(moData.numBinaryOut()):
            state = states[i]
            relayName = "Relay"+str(i)
            btn = builder.get_object(relayName)
            assert not btn is None
            btn.set_active(state)
            btn.connect("toggled", self.on_toggled_button, i)
            self.relayBtns.append(btn)
            self.updateBtn(i, state)

            labelName = "label"+str(i)
            #print("labelName", labelName)
            label = builder.get_object(labelName)
            assert not label is None
            self.relayLabels.append(label)
            self.updateLabel(i, state)
            pass
        self.box.add(self.panel)

        self.allBtn = Gtk.Button("All OFF")
        self.allBtn.show()
        self.allBtn.connect("clicked", self.on_clicked_allOff)
        # add 
        self.box.add(self.allBtn)

        self.summaryLabel = Gtk.Label("summary")
        self.summaryLabel.set_text(str(states))
        self.box.add(self.summaryLabel)
        self.panel.show()
        self.summaryLabel.show()
        self.box.show()

    def update(self):
        self.getData()
        
    def getData(self):
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.dataCount += 1
        #moData.logData()
        states = moData.getValue(keyForBinaryOut())
        self.summaryLabel.set_text(str(states))
        #print("update BinOut lables:",states)
        for i in range(len(states)):
            self.updateLabel(i,states[i])
    
    def on_toggled_button(self, button, idx):
        state = button.get_active()
        #print("toggled button idx state",idx, state)
        self.updateBtn(idx,state)
        moCommand.cmdBinary(idx, state)
        pass
    
    def on_clicked_allOff(self, button):
        #print("clicked All Off")
        moCommand.cmdAllOff()
        # turn off the relay buttons
        for idx in range(len(self.relayBtns)):
            self.updateBtn(idx, False)
        
    def updateLabel(self, idx, state):
        label = self.relayLabels[idx]
        assert not label is None
        nameState = "Relay ["+str(idx) + "] = " 
        if state:
            nameState += "ON  "
        else:
            nameState += "OFF  "
        #print("nameState", nameState)
        label.set_text(nameState)
    
    def updateBtn(self,idx,state):
        btn = self.relayBtns[idx]
        assert not btn is None
        nameState = "Relay ["+str(idx) + "] = " 
        if state: # changed to active
            nameState += "ON  "
        else:
            nameState += "OFF  "
        #print("nameState", nameState)
        btn.set_label(nameState)
        
        