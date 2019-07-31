"""
moGTKclient: first experiment merging pyNNG network messaging with GTK for MODAC
"""

import math
from time import sleep
import time
import datetime
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


from modac import moData, moNetwork, moClient, moCommand, moLogger

class ModacApp(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id, flags):
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)

    def new_window(self, *args):
        ModacAppWindow(self)

class ModacAppWindow(object):
    def __init__(self, application):
        self.Application = application

        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            GtkBuilder = Gtk.Builder.new_from_file("modacGUI/modac1.glade")
            GtkBuilder.connect_signals(self)
        except GObject.GError:
            print("Error reading GUI file")
            raise
                
        # Fire up the main window
        self.MainWindow = GtkBuilder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        self.MainWindow.show()
            
    def close(self, *args):
        self.MainWindow.destroy()
        modacExit()
    
    def on_notebook1_switch_page(self,  notebook, page, page_num, data=None):
        assert not notebook == None
        assert not page == None
        assert page_num >= 0
        print("Ignore switch page ", notebook, page, page_num)
        return
        self.tab = notebook.get_nth_page(page_num)
        self.label = notebook.get_tab_label(self.tab).get_label()
        self.message_id = self.statusbar.push(0, self.label)
    
    def on_gtk_new_activate(self, menuitem, data=None):
        # debugging message
        print('File New selected')
        
    def getData(self):
        # update from network
        if not moClient.clientReceive():
            print("no client data received")
            return False
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        moData.logData()

def modacExit():
    logging.info("modacExit")
    moClient.shutdownClient()
    exit()
    
def modacInit():
    # setup MODAC data/networking
    moData.init()
    moClient.startClient()

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


