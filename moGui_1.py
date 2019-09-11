"""
moGui_1: 2nd experiment with GTK for MODAC
"""
timer_interval = 1

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

from modac import moLogger
if __name__ == "__main__":
    moLogger.init("modacGUI")
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from modac.moKeys import *
from modac import moData, moNetwork, moClient, moCommand, moCSV
from modacGUI import enviroPanel, ktypePanel, ad24Panel, ad16Panel, leicaPanel, binaryOutPanel
from modacGUI import leicaPanel, binaryOutPanel, tempDistPanel
from modacGUI import kilnPanel

class ModacApp(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id="com.modacApp", flags=Gio.ApplicationFlags.FLAGS_NONE):
        # application_id needs to be in proper form com.modac.app1
        log.debug("ModacApp: "+ application_id)
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)
        self.connect("shutdown", self.shutdown)
        log.debug("activated")
        # TODO: is there some Gtk.Application methods needed for shutdown and other mgmt?

    def new_window(self, *args):
        ModacAppWindow(self)

    def shutdown(self, *args):
        log.debug("App Shutdown")
        modacExit()

class ModacAppWindow(object):
    dataCount = 0
    last_open_dir = "~"
    def __init__(self, application):
        self.Application = application
        builder = None
        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            log.debug("load gui from file")
            builder = Gtk.Builder.new_from_file("modacGUI/modac1.glade")
            builder.connect_signals(self)
            log.debug("signals connected")
        except GObject.GError:
            log.debug("Error reading GUI file")
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
            log.debug("no aboutdialog")

        self.notebook = builder.get_object("notebook")
        if self.notebook == None:
            log.debug("ERROR no notebook")

        # populate sub panels
        self.notebook.remove_page(0)
        
        #####
        self.enviroPanel = enviroPanel.enviroPanel()
        self.notebook.append_page(self.enviroPanel.box, self.enviroPanel.label)

        self.ktypePanel = ktypePanel.ktypePanel()
        self.notebook.append_page(self.ktypePanel.box, self.ktypePanel.label)
        
        self.ad24Panel = ad24Panel.ad24Panel()
        self.notebook.append_page(self.ad24Panel.box, self.ad24Panel.label)
        
        self.ad16Panel = ad16Panel.ad16Panel()
        self.notebook.append_page(self.ad16Panel.box, self.ad16Panel.label)
        
        self.leicaPanel = leicaPanel.leicaPanel()
        self.notebook.append_page(self.leicaPanel.box, self.leicaPanel.label)
        
        self.binaryOutPanel = binaryOutPanel.binaryOutPanel()
        self.notebook.append_page(self.binaryOutPanel.box, self.binaryOutPanel.label)
        
        self.tempDistPanel= tempDistPanel.tempDistPanel()
        self.notebook.append_page(self.tempDistPanel.box, self.tempDistPanel.label)
        
        self.kilnPanel = kilnPanel.kilnPanel() # Panel to be tested
        self.notebook.append_page(self.kilnPanel.box, self.kilnPanel.label)

        #  add here and then in updatePanels
        
        # Start timer
        GObject.timeout_add_seconds(timer_interval, self.on_handle_timer)      

        log.debug("and ShowTime!")
        self.MainWindow.show()
            
    def close(self, *args):
        self.MainWindow.destroy()
    
    def on_winMain_destroy(self, widget, data=None):
        log.debug("on_winMain_destory")
        self.shutdown()
        #modacExit()
        #Gtk.main_quit()

    def on_notebook1_switch_page(self,  notebook, page, page_num, data=None):
        assert not notebook == None
        assert not page == None
        assert page_num >= 0
        log.debug("Switch page "+str(page_num)+" "+str(notebook)+" "+str( page))
        #return
        self.tab = notebook.get_nth_page(page_num)
        self.label = notebook.get_tab_label(self.tab).get_label()
        log.debug("should be panel "+ self.label)
        #self.message_id = self.statusbar.push(0, self.label)
    
    def on_startCSV_activate(self, menuitem, data=None):
        if moCSV.isOpen():
            moCSV.close()
            # TODO maybe we should ask to close
            
        # debugging message
        log.debug('on_startCSV_activate')
        dialog=Gtk.FileChooserDialog(
            title="Select CSV File",
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_current_name("modac.csv")
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_current_folder(self.last_open_dir)
        filter_csv = Gtk.FileFilter()
        filter_csv.set_name("CSV Files")
        filter_csv.add_pattern("*.csv")
        dialog.add_filter(filter_csv)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.last_open_dir = dialog.get_current_folder()
            log.debug("*********Selected CSV file: "+filename)
            moCSV.init(filename)
        # enable stop?
        dialog.destroy()      
    
    def on_stopCSV_activate(self, menuitem, data=None):
        # debugging message
        log.debug('on_stopCSV_activate')
        moCSV.close()
        # disable stop, enable start
        
    def on_quit_activate(self, menuitem, data=None):
        # debugging message
        log.debug('File Quit selected')
        self.winMain.destroy()      
        
    def on_activate_AboutMenuItem(self, menuitem, data=None):
        log.debug("Help-About selected")
        self.response = self.aboutdialog.run()
        self.aboutdialog.hide()
        
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
            #log.debug("no client data received")
            return False
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.dataCount += 1
        #moData.logData()
        return True
    
    def updatePanels(self):
        moCSV.addRow()
        self.enviroPanel.update()
        self.ktypePanel.update()
        self.ad24Panel.update()
        self.ad16Panel.update()
        self.leicaPanel.update()
        self.binaryOutPanel.update()
        self.tempDistPanel.update()
        self.kilnPanel.update()

def modacExit():
    log.info("modacExit")
    if moCSV.isOpen():
        moCSV.close()
    moClient.shutdownClient()
    #sys.exit(0)
    
if __name__ == "__main__":
    #modac_argparse() # capture cmd line args to modac_args dictionary for others
    #moLogger.init("moGUI_1") # start logging (could use cmd line args config files)
    # logging initialized at top to avoid start by libraries
    log.debug("moGUI_1: modac from glade files")
    try:
        moData.init(client=True)
        # setup MODAC data/networking
        log.debug("try startClient networking")
        moClient.startClient()
        log.debug("start client gui")
        Application = ModacApp("com.mioat.modacGUI1", Gio.ApplicationFlags.FLAGS_NONE)
        Application.run()
    except Exception as e:
        log.debug("Exception somewhere in dataWindow. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("huh?")
    finally:
        log.debug("end main of moGTKclient")
    modacExit()


