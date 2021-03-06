# modacGUI Enviro Panel 1

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

import numpy as np

#from matplotlib.backends.backend_gtk3agg import FigureCanvas  # or gtk3cairo.
from matplotlib.backends.backend_gtk3cairo import FigureCanvas  # or gtk3cairo.
from matplotlib.figure import Figure

from modac.moKeys import *
from modac import moData, moLogger

### kinda messy having global
# TODO: replace columnNames and plotWidth with Config values
columnNames = ['time','degC', '%rH', 'hPa']
__plotWidth = 100 

class enviroPanel():
    plotWidth = 100 #__plotWidth # for some reason it is not accepting __plotWidth


    def __init__(self):
        self.box = Gtk.VBox(homogeneous=False, spacing=8)
        self.label = Gtk.Label("Enviro Sensors")
    
        ### setup Plot Data 
        self.count=0
        self.times = [0]*self.plotWidth
        self.temps = [0]*self.plotWidth
        self.humid = [0]*self.plotWidth
        self.press = [0]*self.plotWidth
        
        ### setup Table (aka listStore) in a ScrollWindow
        colTypes = [str]*4

        # so how do we get it to be types ?
        self.listStore = Gtk.ListStore()
        self.listStore.set_column_types(colTypes)#str,str,str,str)
        #self.listStore = Gtk.ListStore(str,float, float, float)
        self.treeview = Gtk.TreeView(model=self.listStore)
        for i in range( len(columnNames)) :
            column = Gtk.TreeViewColumn(columnNames[i], Gtk.CellRendererText(),text=i)
            column.set_min_width(100)
            column.set_alignment(0.5)
            column.set_clickable(True)
            column.connect("clicked", self.clickedColumn, i)
            self.treeview.append_column(column)
        self.treeview.show()
        
        # get at least some data
        self.getData() # put one item in local data
        
        sw = self.upperScroll = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_vexpand(True)
        viewport = Gtk.Viewport()
        viewport.add(self.treeview)
        viewport.show()
        sw.add(viewport)
        #sw.add_with_viewport(self.treeview)
        self.box.pack_start(sw, True, True, 0)
        
        ### Matplotlib stuff
        self.fig = Figure(figsize=(6, 4))

        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea
        self.box.pack_end(self.canvas, True, True, 0)

        self.ax = self.fig.add_subplot(1,1,1)
        
        self.plotColumn = 1
        self.line, = self.ax.plot(self.times, self.temps)  # plot the first row
        #self.lowerScroll.add_with_viewport(self.canvas)
        #print("canvas: ", self.canvas)
        self.upperScroll.show()
        self.canvas.show()
        self.box.show()
        
    def getData(self):
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.timestamp = moData.getValue(keyForTimeStamp())
        enviro = moData.getValue(keyForEnviro())
        #log.debug("enviro Update = "+str( enviro))
        temperature = enviro[keyForTemperature()]
        humidity = enviro[keyForHumidity()]
        pressure = enviro[keyForPressure()]
        
        self.count = self.count+1

        self.hStr = '%0.3f%%rH'% humidity
        self.tStr = '%0.3f°C'%temperature
        self.pStr = '%0.3fhPa'%pressure
       
        #update local data arrays
        self.times.append(self.count)
        self.temps.append(temperature)
        self.humid.append(humidity)
        self.press.append(pressure)
        
        #limit size of arrays
        self.times = self.times[-self.plotWidth:]
        self.temps = self.temps[-self.plotWidth:]
        self.humid = self.humid[-self.plotWidth:]
        self.press = self.press[-self.plotWidth:]
        # create strings for listStore and add them at top
        it = self.listStore.prepend([self.timestamp,self.tStr,self.hStr,self.pStr])
        # and limit the listStore
        try:
            if len(self.listStore) > self.plotWidth:
                it = self.listStore.iter_nth_child(None,self.plotWidth)
                self.listStore.remove(it)
        except :
            print("got an exception removing from listStore")
            log.error("Exception happened", exc_info=True)
            pass
        
        #it = self.listStore.append([timeStr,self.bme.temperature, self.bme.humidity, self.bme.pressure])
        #
        #self.printBMEData()
        #print("Row: ",self.listStore[it][0],self.listStore[it][1],self.listStore[it][2],self.listStore[it][3])
        return True
    
    def printBMEData(self):
        print("BME: ",self.count, self.timestamp,self.tStr,self.hStr,self.pStr)
        
    def plotTemp(self): #, treeview, path, view_column):
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
        
    def plotHumid(self): #, treeview, path, view_column):
        #self.line.set_ydata(self.humid)
        self.plotColumn=2
        self.ax.clear()
        self.line, = self.ax.plot(self.times, self.humid)  # plot the first row
        self.ax.set_title('Humidity')
        self.ax.set_ylim(30,100)
        self.canvas.draw()
        
    def plotPressure(self): #, treeview, path, view_column):
        #self.line.set_ydata(self.press)
        self.plotColumn=3
        self.ax.clear()
        self.line, = self.ax.plot(self.times, self.press)  # plot the first row
        self.ax.set_title('Pressure')
        self.ax.set_ylim(960,1000)
        self.canvas.draw()
        
    def updatePlot(self):
        #print("updatePlot column", self.plotColumn)
        if self.plotColumn == 1:
            self.plotTemp()
        elif self.plotColumn == 2:
            self.plotHumid()
        else :
            self.plotPressure()
        
    def printList(self,widget):
        for row in self.listStore :
            print(row[:])
    
    def clickedColumn(self, treeCol, idx):
        print("clicked column ", idx, columnNames[idx])
        self.plotColumn = idx
        self.updatePlot()

    def update(self):
        self.getData()
        self.updatePlot()
