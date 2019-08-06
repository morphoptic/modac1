"""
Modac testLeicaPanel: unit test for Modac Leicaputs client GTK panel 
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
from modacGUI import leicaPanel

class TestLeicaApp(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id="com.TestleicaPanel", flags=Gio.ApplicationFlags.FLAGS_NONE):
        # application_id needs to be in proper form com.modac.app1
        print("TestLeicaPanel: ", application_id)
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)
        self.connect("shutdown", self.shutdown)
        print("activated")
        # TODO: is there some Gtk.Application methods needed for shutdown and other mgmt?

    def new_window(self, *args):
        TestLeicaPanelWindow(self)

    def shutdown(self, *args):
        print("App Shutdown")
        modacExit()

class TestLeicaPanelWindow(object):
    dataCount = 0
    def __init__(self, application):
        self.Application = application
        builder = None
        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            print("load gui from file")
            builder = Gtk.Builder.new_from_file("modacGUI/testApp.glade")
            builder.connect_signals(self)
            print("signals connected")
        except GObject.GError:
            print("Error reading GUI file")
            raise
        # Fire up the main window
        self.MainWindow = builder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        
        self.viewport = builder.get_object("MainViewport")
        
        self.panel = leicaPanel.LeicaPanel()
        self.panel.box.show()
        self.viewport.add(self.panel.box)
        #release builder ?
        
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
        # update from network
        if not moClient.clientReceive():
            print("no client data received")
            return True # keep listening
        self.panel.update()
        return True 
        
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
        Application = TestLeicaApp("com.mioat.TestLeicaPanel", Gio.ApplicationFlags.FLAGS_NONE)
        Application.run()
    except Exception as e:
        print("Exception somewhere in dataWindow. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main of moGTKclient")
    modacExit()


