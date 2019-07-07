#!/usr/bin/python
# -*- coding:utf-8 -*-

import math
from time import sleep
import time
import datetime
import numpy as np
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository import GObject as Gobj

#from matplotlib.backends.backend_gtk3agg import FigureCanvas  # or gtk3cairo.
from matplotlib.backends.backend_gtk3cairo import FigureCanvas  # or gtk3cairo.
from matplotlib.figure import Figure

from waveshareADAC import ADS1256
import RPi.GPIO as GPIO

boardPot = 0 # board potentiometer is on AD0
boardPhotoR = 1 # board photo resistor is on AD1
myPot = 2 # test pot is on AD2
  
print("MODAC Graphing ADS1256 waveshare board")

columnNames = ['time','degC', '%rH', 'hPa']

class DataWindow(Gtk.Window):
    def init_Data(self):
        plot_width = self.plot_width = 100
        self.count=0
        self.data = np.zeros((plot_width,9))
        self.columnNames = ["Count"]
        self.colTypes = [str]
        with np.nditer(self.data) as it:
            it.iternext() # skip first column
            while not it.finished:
                name = 'A%0d'% it.index-1
                self.columnNames.append(name)
                self.colTypes.append(str)
                it.iternext()
        print(colNames)
        
    def __init__(self,ADC):
        
        super().__init__()
        self.adc = ADC
        self.init_Data()
        
        self.set_default_size(600, 600)
        self.connect('destroy', lambda win: Gtk.main_quit())

        self.set_title('GtkMatPlot Waveshield Sheet demo')
        self.set_border_width(8)

        self.vbox = Gtk.VBox(homogeneous=False, spacing=8)
        self.add(self.vbox)

        
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
            
        self.getBMEData() # put one item in data
        
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
    
    def readOneData(self):
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
        #self.printBMEData()
        #print("Row: ",self.listStore[it][0],self.listStore[it][1],self.listStore[it][2],self.listStore[it][3])
        
    def printBMEData(self):
        #dateStr = self.bme.timestamp.strftime("Date  %Y-%m-%d") 
        timeStr = self.bme.timestamp.strftime("Time: %H:%M:%S%Z") 
        hStr = 'Humidity:  %0.3f %%rH'% self.bme.humidity
        tStr = 'Temp:      %0.3f° C'%self.bme.temperature
        pStr = 'Pressure:  %0.3f hPa'% self.bme.pressure
        print("BME: ",self.count, timeStr,tStr,hStr,pStr)
        
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
        self.readOneData()
        self.updatePlot()
        return True

    def printList(self,widget):
        for row in self.listStore :
            print(row[:])
    
    def clickedColumn(self, treeCol, idx):
        print("clicked column ", idx, columnNames[idx])
        self.plotColumn = idx
        self.updatePlot()

#try:
print("start loop")
ADC = ADS1256.ADS1256()
ADC.ADS1256_init()

manager = DataWindow(ADC)
manager.show_all()
Gtk.main()
    
#except :
#    print("****Exception!!")
#    print(sys.exc_info()[0])
#    for err in sys.exc_info():
#        print(err)
GPIO.cleanup()
print ("\r\nProgram end     ")
exit()
