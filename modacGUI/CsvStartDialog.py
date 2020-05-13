#  CsvStartDialog
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
from modac import moCSV

_dialog = None
_filename = "modac.csv"
_lastDir = "logs"
_timing = 1
_response = Gtk.ResponseType.NONE

_maxRange = 240

def get_filename():
    return this._filename
def get_lastDir():
    return this._lastDir
def get_timing():
    return this._timing
def get_response():
    return this._response

def runDialog(mainWindow, csvFilename, lastDir, timing):
    print("Open CsvStartDialog this: ", this._filename, this._lastDir, this._timing, this._response)
    print("Open CsvStartDialog param: ", csvFilename, lastDir, timing)
    this._dialog = CSVDialog(mainWindow,csvFilename, lastDir, timing)
    response = this._dialog.run()
    #dialog should have updated this values if it was OK
    print("response from dialog: ", this._response, response)
    this._dialog = None
    print("End CsvStartDialog this: ", this._filename, this._lastDir, this._timing, this._response)

class CSVDialog():
    def __init__(self, mainWindow, filename, lastDir, timing):        
        print("init CsvStartDialog ", filename, lastDir, timing, this._filename)
        self.builder = Gtk.Builder.new_from_file("modacGUI/CSVDialog.glade")
        self.builder.connect_signals(self)
        # initialize filename and timing
        self.dialog = self.builder.get_object("CsvStartDialog")
        self.dialog.set_transient_for(mainWindow)
        self.filenameBox = self.builder.get_object("FilenameBox")
        self.filenameBox.set_text(filename)
        self.filechooser = self.builder.get_object("Filechooser")
        self.timeWidget = self.builder.get_object("SampleTiming")
        adj = Gtk.Adjustment(timing, 1, this._maxRange, 1, 10)
        self.timeWidget.set_adjustment(adj)
        #self.timeWidget.set_value(timing)
        #self.timeWidget.set_range(1,this._maxRange)
        t = self.timeWidget.get_value()
        if not t == timing :
            log.error("***did not set timeWidget")
        self.response = Gtk.ResponseType.NONE
        
    def run(self):
        self.response = self.dialog.run()
        
    def afterRun(self):
        self.dialog.destroy()
        self.dialog = None
        pass
      
    def on_CsvStartDialog_close(self):
       # close box clicked = cancel
       print("\n\n**** close csvStartDialog\n\n")
       pass
    
    def OKButton_clicked_cb(self, button):
        print("\n\n**** OKButton_clicked_cb csvStartDialog\n\n")
        timing = self.timeWidget.get_value()
        if timing < 1 or timing > this._maxRange:
            print("csvDialog timing out of range " + str(timing))
            log.error("csvDialog timing out of range " + str(timing))
            this._response = Gtk.ResponseType.CANCEL
            self.dialog.close()
            return
        print("timing is ok, so reponse should be OK", timing)
        this._filename = self.filenameBox.get_text()
        #this._lastDir = self.filechooser.get_text()
        this._timing = timing
        this._response = Gtk.ResponseType.OK
        self.dialog.close()
        pass
    
    def CancelButton_clicked_cb(self, button):
        print("\n\n**** CancelButton_clicked_cb csvStartDialog\n\n")
        this._response = Gtk.ResponseType.CANCEL
        self.dialog.close()
        pass
  
    