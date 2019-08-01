"""
moGTKclient: first experiment merging pyNNG network messaging with GTK for MODAC
"""

import math
from time import sleep
import time
import datetime
import random
import numpy as np
import sys
import os
import logging, logging.handlers
import argparse
import json

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gio, Gdk, Gtk
from gi.repository import GObject as Gobj

from modac.moKeys import *
from modac import moData, moNetwork, moClient, moCommand, moLogger
from modacGUI import enviroPanel, ktypePanel, ad24Panel, ad16Panel,leicaPanel

class TestBtnApp(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id="com.TestBtnPanel", flags=Gio.ApplicationFlags.FLAGS_NONE):
        # application_id needs to be in proper form com.modac.app1
        print("TestBtnPanel: ", application_id)
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)
        self.connect("shutdown", self.shutdown)
        print("activated")
        # TODO: is there some Gtk.Application methods needed for shutdown and other mgmt?

    def new_window(self, *args):
        TestBtnPanelWindow(self)

    def shutdown(self, *args):
        print("App Shutdown")
        modacExit()

class TestBtnPanelWindow(object):
    dataCount = 0
    def __init__(self, application):
        self.Application = application
        builder = None
        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            print("load gui from file")
            self.builder = Gtk.Builder.new_from_file("modacGUI/binaryOutPanel.glade")
            self.builder.connect_signals(self)
            print("signals connected")
        except GObject.GError:
            print("Error reading GUI file")
            raise
        # Fire up the main window
        self.MainWindow = self.builder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        
        self.viewPort = self.builder.get_object("MainViewport")
        
        self.initPanel()
        
        self.viewPort.add(self.panel)
        self.panel.show()

        # Start timer
        timer_interval = 1
        GObject.timeout_add_seconds(timer_interval, self.on_handle_timer)      

        print("and ShowTime!")
        self.MainWindow.show()
            
    def close(self, *args):
        self.MainWindow.destroy()
    
    def on_winMain_destroy(self, widget, data=None):
        print("on_winMain_destory")
        #modacExit()
        #Gtk.main_quit()

    def on_file_new_activate(self, menuitem, data=None):
        # debugging message
        print('File New selected')
        
    def on_file_open_activate(self, menuitem, data=None):
        # debugging message
        print('File OPEN selected')
        
    def on_file_quit_activate(self, widget, data=None):
        print("on_file_quit")
        self.winMain.destroy()      

    def on_handle_timer(self):
        if not self.getData():
            # no data received
            return True
#        timestamp = moData.getValue(keyForTimeStamp())
#        if timestamp == None:
#            timestamp = "no data yet"
#        #text = "Random number = " + str(random.randint(1,101))
#        self.setStatus("Data Updated: #%d at "%self.dataCount +timestamp)
        self.updatePanel()
        return True 
    
    def getData(self):
        # update from network
        if not moClient.clientReceive():
            print("no client data received")
            return False
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.dataCount += 1
        #moData.logData()
        states = moData.getValue(keyForBinaryOut())
        print("update BinOut lables:",states)
        for i in range(len(states)):
            self.updateLabel(i,states[i])
    
    def updatePanel(self):
        pass #self.panel.update()

    def on_toggled_button(self, button, idx):
        state = button.get_active()
        print("toggled button idx state",idx, state)
        self.updateBtn(idx,state)
        moCommand.cmdBinary(idx, state)
        pass
    
    def updateLabel(self, idx, state):
        label = self.relayLabels[idx]
        assert not label == None
        nameState = "Relay ["+str(idx) + "] = " 
        if state:
            nameState += "ON  "
        else:
            nameState += "OFF  "
        print("nameState", nameState)
        label.set_text(nameState)
    
    def updateBtn(self,idx,state):
        btn = self.relayBtns[idx]
        assert not btn == None
        nameState = "Relay ["+str(idx) + "] = " 
        if state: # changed to active
            nameState += "ON  "
        else:
            nameState += "OFF  "
        print("nameState", nameState)
        btn.set_label(nameState)
        
    def initPanel(self): # do all the connections here so it is easier to transfer
        print("initPanel")
        
        self.panel = self.builder.get_object("Panel")
        self.relayBtns = []
        self.relayLabels = []
        states = moData.getValue(keyForBinaryOut())
        assert len(states) == moData.numBinaryOut()
        for i in range(moData.numBinaryOut()):
            state = states[i]
            relayName = "Relay"+str(i)
            btn = self.builder.get_object(relayName)
            assert not btn == None
            btn.set_active(state)
            btn.connect("toggled", self.on_toggled_button, i)
            self.relayBtns.append(btn)
            self.updateBtn(i, state)

            labelName = "label"+str(i)
            print("labelName", labelName)
            label = self.builder.get_object(labelName)
            assert not label == None
            self.relayLabels.append(label)
            self.updateLabel(i, state)
            pass
        self.panel.show()

##################################
        
def modacExit():
    logging.info("modacExit")
    moClient.shutdownClient()
    #sys.exit(0)
    
def modacInit():
    # setup MODAC data/networking
    moData.init()
    logging.debug("try startClient()")
    moClient.startClient()
    logging.debug("client started")

if __name__ == "__main__":
    #modac_argparse() # capture cmd line args to modac_args dictionary for others
    moLogger.init("moGUI_1") # start logging (could use cmd line args config files)
    print("moGUI_1: modac from glade files")
    try:
        modacInit()
        Application = TestBtnApp("com.mioat.TestBtnPanel", Gio.ApplicationFlags.FLAGS_NONE)
        Application.run()
    except Exception as e:
        print("Exception somewhere in dataWindow. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main of moGTKclient")
    modacExit()


