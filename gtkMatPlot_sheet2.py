"""
===============
GTK Spreadsheet Derived from gtk_spreadsheet_sgskip.py
===============

Example of embedding Matplotlib in an application and interacting with a
treeview to store data.  Double click on an entry to update plot data.
"""

import math
from time import sleep
import time
import datetime
import numpy as np

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository import GObject as Gobj

#from matplotlib.backends.backend_gtk3agg import FigureCanvas  # or gtk3cairo.
from matplotlib.backends.backend_gtk3cairo import FigureCanvas  # or gtk3cairo.

from matplotlib.figure import Figure

# our MorphOptics wrapper on the BME280 device, wraps Adafruit library, smbus2, etc
from moBME280 import moBME280

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
 
        #self.createData()
        self.bme = moBME280()
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
            column = Gtk.TreeViewColumn(columnNames[i], Gtk.CellRendererText(),text=1)
            column.set_min_width(80)
            column.set_alignment(0.5)
            self.treeview.append_column(column)
            
        self.getBMEData() # put one item in data
        
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        sw.add(self.treeview)
        self.treeview.connect('row-activated', self.clickRow)
        self.vbox.pack_start(sw, True, True, 0)

        # Matplotlib stuff
        self.fig = Figure(figsize=(6, 4))

        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea
        self.vbox.pack_start(self.canvas, True, True, 0)
        self.ax = self.fig.add_subplot(1,1,1)
        self.line, = self.ax.plot(self.times, self.temps)  # plot the first row

        #self.add_columns()
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.KEY_PRESS_MASK |
                        Gdk.EventMask.KEY_RELEASE_MASK)
        self.dataUpdateId = Gobj.timeout_add(1000, self.getNextData)
    
    def getBMEData(self):
        self.count = self.count+1
        self.bme.read()
        self.times.append(self.count) #bme.timestamp.strftime("%S%Z"))
        self.temps.append(self.bme.temperature)
        self.humid.append(self.bme.humidity)
        self.press.append(self.bme.pressure)
        #limit size of arrays
        self.times = self.times[-self.plot_width:]
        self.temps = self.temps[-self.plot_width:]
        self.humid = self.humid[-self.plot_width:]
        self.press = self.press[-self.plot_width:]
        # create strings for listStore
        timeStr = self.bme.timestamp.strftime("%H:%M:%S%Z")
        hStr = '%0.3f%%rH'% self.bme.humidity
        tStr = '%0.3f°C'%self.bme.temperature
        pStr = '%0.3fhPa'% self.bme.pressure
        #
        it = self.listStore.append([timeStr,tStr,hStr,pStr])
        #it = self.listStore.append([timeStr,self.bme.temperature, self.bme.humidity, self.bme.pressure])
        #
        self.printBMEData()
        print("Row: ",self.listStore[it][0],self.listStore[it][1],self.listStore[it][2],self.listStore[it][3])
        
    def printBMEData(self):
        #dateStr = self.bme.timestamp.strftime("Date  %Y-%m-%d") 
        timeStr = self.bme.timestamp.strftime("Time: %H:%M:%S%Z") 
        hStr = 'Humidity:  %0.3f %%rH'% self.bme.humidity
        tStr = 'Temp:      %0.3f° C'%self.bme.temperature
        pStr = 'Pressure:  %0.3f hPa'% self.bme.pressure
        print("BME: ",self.count, timeStr,tStr,hStr,pStr)
        
    def plotTemp(self): #, treeview, path, view_column):
        #self.line.set_ydata(self.dataModel.temps)
        self.line, = self.ax.plot(self.times, self.temps)  # plot the first row
        #_min = np.amin(self.dataModel.temps)
        _max = np.amax(self.temps)
        if _max < 35:
            _max = 35
        self.ax.set_title('temperature')
        self.ax.set_ylim(25,_max+_max*0.1)
        self.canvas.draw()
        
    def plotHumid(self): #, treeview, path, view_column):
        self.line.set_ydata(self.humid)
        self.canvas.draw()
        
    def plotPressure(self): #, treeview, path, view_column):
        self.line.set_ydata(self.press)
        self.canvas.draw()
        
    def getNextData(self):
        self.getBMEData()
        self.plotTemp()
        return True

    def printList(self,widget):
        for row in self.listStore :
            print(row[:])
    def clickRow(self, treeview, path, view_column):
        ind, = path  # get the index into data

#    def add_columns(self):
#        for i in self.model.columnNames:
#            column = Gtk.TreeViewColumn(str(i), Gtk.CellRendererText(), text=i)
#            self.treeview.append_column(column)



manager = DataWindow()
manager.show_all()
Gtk.main()
