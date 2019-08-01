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
from modacGUI import enviroPanel, ktypePanel, ad24Panel, ad16Panel

class ModacApp(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id="com.modacApp", flags=Gio.ApplicationFlags.FLAGS_NONE):
        # application_id needs to be in proper form com.modac.app1
        print("ModacApp: ", application_id)
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)
        self.connect("shutdown", self.shutdown)
        print("activated")
        # TODO: is there some Gtk.Application methods needed for shutdown and other mgmt?

    def new_window(self, *args):
        ModacAppWindow(self)

    def shutdown(self, *args):
        print("App Shutdown")
        modacExit()

class ModacAppWindow(object):
    dataCount = 0
    def __init__(self, application):
        self.Application = application
        builder = None
        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            print("load gui from file")
            builder = Gtk.Builder.new_from_file("modacGUI/modac1.glade")
            builder.connect_signals(self)
            print("signals connected")
        except GObject.GError:
            print("Error reading GUI file")
            raise
        # Fire up the main window
        self.MainWindow = builder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        
        self.statusbar = builder.get_object("MainStatusBar")
        self.context_id = self.statusbar.get_context_id("status")
        self.status_count = 0
        status_text = "Welcome to MODAC"
        self.statusbar.push(self.context_id, status_text)   

        self.aboutdialog = builder.get_object("AboutMODAC_Dialog")
        if self.aboutdialog == None:
            print("no aboutdialog")

        self.notebook = builder.get_object("notebook")
        if self.notebook == None:
            print("ERROR no notebook")

        # populate sub panels
        self.notebook.remove_page(0)
        
        #####
        self.enviroPanel = enviroPanel.enviroPanel()
        print("loaded enviroPanel", self.enviroPanel, self.enviroPanel.box)
        self.notebook.append_page(self.enviroPanel.box, self.enviroPanel.label)

        self.ktypePanel = ktypePanel.ktypePanel()
        self.notebook.append_page(self.ktypePanel.box, self.ktypePanel.label)
        
        self.ad24Panel = ad24Panel.ad24Panel()
        self.notebook.append_page(self.ad24Panel.box, self.ad24Panel.label)
        
        self.ad16Panel = ad16Panel.ad16Panel()
        self.notebook.append_page(self.ad16Panel.box, self.ad16Panel.label)
        
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

    def on_notebook1_switch_page(self,  notebook, page, page_num, data=None):
        assert not notebook == None
        assert not page == None
        assert page_num >= 0
        print("Switch page ", page_num, notebook, page)
        #return
        self.tab = notebook.get_nth_page(page_num)
        self.label = notebook.get_tab_label(self.tab).get_label()
        #self.message_id = self.statusbar.push(0, self.label)
    
    def on_file_new_activate(self, menuitem, data=None):
        # debugging message
        print('File New selected')
        
    def on_file_open_activate(self, menuitem, data=None):
        # debugging message
        print('File OPEN selected')
        
    def on_activate_AboutMenuItem(self, menuitem, data=None):
        print("Help-About selected")
        self.response = self.aboutdialog.run()
        self.aboutdialog.hide()
        
    def on_file_quit_activate(self, widget, data=None):
        print("on_file_quit")
        self.winMain.destroy()      

    def on_handle_timer(self):
        # Update status bar
        if not self.getData():
            # no data received
            return True
        timestamp = moData.getValue(keyForTimeStamp())
        if timestamp == None:
            timestamp = "no data yet"
        #text = "Random number = " + str(random.randint(1,101))
        self.setStatus("Data Updated: #%d at "%self.dataCount +timestamp)
        self.updatePanels()
        return True 

    def setStatus(self, status):
        self.statusbar.pop(self.context_id)
        self.statusbar.push(self.context_id, status)           
    
    def getData(self):
        # update from network
        if not moClient.clientReceive():
            print("no client data received")
            return False
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.dataCount += 1
        moData.logData()
        return True
    
    def updatePanels(self):
        self.enviroPanel.update()
        self.ktypePanel.update()
        self.ad24Panel.update()
        self.ad16Panel.update()

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
        Application = ModacApp("com.mioat.modacGUI1", Gio.ApplicationFlags.FLAGS_NONE)
        Application.run()
    except Exception as e:
        print("Exception somewhere in dataWindow. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main of moGTKclient")
    modacExit()


