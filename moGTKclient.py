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
from gi.repository import Gtk, Gdk
from gi.repository import GObject as Gobj

#from matplotlib.backends.backend_gtk3agg import FigureCanvas  # or gtk3cairo.
from matplotlib.backends.backend_gtk3cairo import FigureCanvas  # or gtk3cairo.
from matplotlib.figure import Figure

# modac
from modac.moKeys import *
from modac import moData, moNetwork

columnNames = ['time','degC', '%rH', 'hPa']

class DataWindow(Gtk.Window):
    def __init__(self):
        global columnNames
        
        super().__init__()
        self.set_default_size(600, 600)
        self.connect('destroy', lambda win: Gtk.main_quit())

        self.set_title('GtkMatPlotBME Sheet demo')
        self.set_border_width(8)

        self.vbox = Gtk.VBox(homogeneous=False, spacing=8)
        self.add(self.vbox)

        self.toolbar = Gtk.Toolbar()
        self.context = self.toolbar.get_style_context()
        self.context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.vbox.pack_start(self.toolbar, False, False, 0)
       
       #Then we have to create buttons and add them to the toolbar on position 0 and 1. Then add the toolbar to our layout. The two buttons are also connected to their respective function when they are clicked.

        self.tempButton = Gtk.ToolButton(label="Plot degC")
        self.humidButton = Gtk.ToolButton(label="Plot rH")
        self.pressureButton = Gtk.ToolButton(label="Plot hPa")
        self.printButton = Gtk.ToolButton(label="Print")

        self.toolbar.insert(self.tempButton, 0)
        self.toolbar.insert(self.humidButton, -1)
        self.toolbar.insert(self.pressureButton, -1)
        self.toolbar.insert(self.printButton, -1)

        self.tempButton.connect("clicked", self.plotTemp)
        self.humidButton.connect("clicked", self.plotHumid)
        self.pressureButton.connect("clicked", self.plotPressure)
        self.printButton.connect("clicked", self.printList)
 
        # setup MODAC data/networking
        moData.init()
        moNetwork.startSubscriber()
        
        plot_width = self.plot_width = 100
        self.count=0
        self.times = [0]*plot_width
        self.temps = [0]*plot_width
        self.humid = [0]*plot_width
        self.press = [0]*plot_width
        
        self.listStore = Gtk.ListStore(str,str,str,str)
        #self.listStore = Gtk.ListStore(str,float, float, float)
        self.treeview = Gtk.TreeView(model=self.listStore)
        for i in range( len(columnNames)) :
            column = Gtk.TreeViewColumn(columnNames[i], Gtk.CellRendererText(),text=i)
            column.set_min_width(100)
            column.set_alignment(0.5)
            column.set_clickable(True)
            column.connect("clicked", self.clickedColumn, i)
            self.treeview.append_column(column)
            
        
        self.getData() # put one item in data
        
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        sw.add(self.treeview)
        #self.treeview.connect('row-activated', self.clickRow)
        self.vbox.pack_start(sw, True, True, 0)

        # Matplotlib stuff
        self.fig = Figure(figsize=(6, 4))

        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea
        self.vbox.pack_start(self.canvas, True, True, 0)
        self.ax = self.fig.add_subplot(1,1,1)
        
        self.plotColumn = 1
        self.line, = self.ax.plot(self.times, self.temps)  # plot the first row

        #self.add_columns()
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK |
                        Gdk.EventMask.KEY_RELEASE_MASK)
        self.dataUpdateId = Gobj.timeout_add(1000, self.getNextData)
    
    def getData(self):
        # update from network
        if not moNetwork.clientReceive():
            return False
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.timestamp = moData.getValue(keyForTimeStamp())
        enviro = moData.getValue(keyForEnviro())
        temperature = enviro[keyForTemperature()]
        humidity = enviro[keyForHumidity()]
        pressure = enviro[keyForPressure()]
        
        self.count = self.count+1

        self.hStr = '%0.3f%%rH'% humidity
        self.tStr = '%0.3f°C'%temperature
        self.pStr = '%0.3fhPa'%pressure
       
        #update local data arrays
        self.times.append(self.count) #bme.timestamp.strftime("%S%Z"))
        self.temps.append(temperature)
        self.humid.append(humidity)
        self.press.append(pressure)
        
        #limit size of arrays
        self.times = self.times[-self.plot_width:]
        self.temps = self.temps[-self.plot_width:]
        self.humid = self.humid[-self.plot_width:]
        self.press = self.press[-self.plot_width:]
        # create strings for listStore
        # which is the table view
        it = self.listStore.append([self.timestamp,self.tStr,self.hStr,self.pStr])
        #it = self.listStore.append([timeStr,self.bme.temperature, self.bme.humidity, self.bme.pressure])
        #
        #self.printBMEData()
        #print("Row: ",self.listStore[it][0],self.listStore[it][1],self.listStore[it][2],self.listStore[it][3])
        return True
    
    def printBMEData(self):
        #dateStr = self.bme.timestamp.strftime("Date  %Y-%m-%d") 
        print("BME: ",self.count, self.timestamp,self.tStr,self.hStr,self.pStr)
        
    def plotTemp(self,widget): #, treeview, path, view_column):
        self.plotColumn = 1
        #self.line.set_ydata(self.temps)
        #self.line.set_xdata(self.times)
        self.ax.clear()
        self.line, = self.ax.plot(self.times, self.temps)  # plot the first row
        #_min = np.amin(self.dataModel.temps)
        _max = np.amax(self.temps)
        if _max < 35:
            _max = 35
        self.ax.set_title('Ambient Temperature')
        self.ax.set_ylim(25,_max+_max*0.1)
        self.canvas.draw()
        
    def plotHumid(self,widget): #, treeview, path, view_column):
        #self.line.set_ydata(self.humid)
        self.plotColumn=2
        self.ax.clear()
        self.line, = self.ax.plot(self.times, self.humid)  # plot the first row
        self.ax.set_title('Humidity')
        self.ax.set_ylim(30,100)
        self.canvas.draw()
        
    def plotPressure(self,widget): #, treeview, path, view_column):
        #self.line.set_ydata(self.press)
        self.plotColumn=3
        self.ax.clear()
        self.line, = self.ax.plot(self.times, self.press)  # plot the first row
        self.ax.set_title('Pressure')
        self.ax.set_ylim(960,1000)
        self.canvas.draw()
        
    def updatePlot(self):
        if self.plotColumn == 1:
            self.plotTemp(self.tempButton)
        elif self.plotColumn == 2:
            self.plotHumid(None)
        else :
            self.plotPressure(None)
        
    def getNextData(self):
        # should only update plot if data changed
        self.getData()
        self.updatePlot()
        return True

    def printList(self,widget):
        for row in self.listStore :
            print(row[:])
    
    def clickedColumn(self, treeCol, idx):
        print("clicked column ", idx, columnNames[idx])
        self.plotColumn = idx
        self.updatePlot()

loggerInit = False
def setupLogging():
    global loggerInit
    print("setupLogging")
    if loggerInit :
        logging.warn("Duplicate call to setupLogging()")
        return
    maxLogSize = (1024 *1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = "moGTKClient"+nowStr+".log"
    logFormatStr = "%(asctime)s [%(threadName)-12.12s] [%(name)s] [%(levelname)-5.5s] %(message)s"
    # setup base level logging to stderr (console?)
    # consider using logging.config.fileConfig()
    # consider using log directory ./log
    logDirName = os.path.join(os.getcwd(),"logs")
    if os.path.exists(logDirName) == False:
        os.mkdir(logDirName)
        
    logName = os.path.join(logDirName, logName)
    print("print Logging to stderr and " + logName)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    rootLogger = logging.getLogger()
    
    logFormatter = logging.Formatter(logFormatStr)
    #consoleHandler = logging.StreamHandler()
    #consoleHandler.setFormatter(logFormatter)
    #rootLogger.addHandler(consoleHandler);
    # chain rotating file handler so logs go to stderr as well as logName file
    fileHandler = logging.handlers.RotatingFileHandler(logName, maxBytes=maxLogSize, backupCount=10)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    
    logging.captureWarnings(True)
    logging.info("Logging Initialized")
    print("Logging Initialized? should have echo'd on line above")
    loggerInit = True
    
def modac_exit():
    logging.info("modac_exit")
    moNetwork.shutdownNet()
    exit()

if __name__ == "__main__":
    #modac_argparse() # capture cmd line args to modac_args dictionary for others
    setupLogging() # start logging (could use cmd line args config files)
    print("moGTKclient testing nng publish-subscribe")
    try:
        manager = DataWindow()
        manager.show_all()
        Gtk.main()
    except Exception as e:
        print("Exception somewhere in dataWindow. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main of moGTKclient")
    modac_exit()

