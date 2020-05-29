# modacGUI ad24Panel Panel 1

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

class ad24Panel():
    plotWidth = 100 #__plotWidth # for some reason it is not accepting __plotWidth
    def __init__(self):        
        self.box = Gtk.VBox(homogeneous=False, spacing=8)
        self.label = Gtk.Label("AD24 5v")

        self.n_col = moData.numAD24()
        # initialized array of data of plotWidth
        self.count=0
        self.times = [0]*self.plotWidth
        self.col = [ [0]*self.plotWidth ]*(self.n_col) 
        
        self.columnNames = ["time"]+["AD24-"+str(i) for i in range(self.n_col) ]
        ### setup Plot Data 
        
        ### setup Table (aka listStore) in a ScrollWindow
        colTypes = [str]*(self.n_col+1)
        self.listStore = Gtk.ListStore()
        self.listStore.set_column_types(colTypes)#str,str,str,str)
        #self.listStore = Gtk.ListStore(str,float, float, float)
        self.treeview = Gtk.TreeView(model=self.listStore)
        # so why do we need to do this if listStore has types of columns already?
        # doesnt this add a column to the store as well?
        for i in range( len(self.columnNames)) :
            column = Gtk.TreeViewColumn(self.columnNames[i], Gtk.CellRendererText(),text=i)
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
        
        self.plotColumn = 1 # use first column, 
        self.line, = self.ax.plot(self.times, self.col[self.plotColumn-1])  # plot the first row
        #self.lowerScroll.add_with_viewport(self.canvas)
        #print("canvas: ", self.canvas)
        self.upperScroll.show()
        self.canvas.show()
        self.box.show()
        
    def getData(self):
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        self.timestamp = moData.getValue(keyForTimeStamp())
        data = moData.getValue(keyForAD24())
        #print("AD24 Update = ", data)
 
        self.count = self.count+1
       
        #update local data arrays
        self.times.append(self.count)
        self.times = self.times[-self.plotWidth:]
        row = [moData.getValue(keyForTimeStamp())]
        for i in range(len(data)):
            v = data[i]
            self.col[i].append(v)
            self.col[i] = self.col[i][-self.plotWidth:]
            row.append(str(v))

        # create strings for listStore and add them at top
        it = self.listStore.prepend(row)
        # and limit the listStore
        try:
            if len(self.listStore) > self.plotWidth:
                it = self.listStore.iter_nth_child(None,self.plotWidth)
                self.listStore.remove(it)
        except :
            print("got an exception removing from listStore")
            log.error("Exception happened", exc_info=True)
            pass
        
        return True
    
    def plotAll(self):
        mi = np.min(self.col)
        ma = np.max(self.col)
        r = (ma-mi) *0.01
        if r < ma*0.5:
            r+=ma*0.5
        mi -= r
        ma += r
        print("plotAll min",mi, "max", ma)
        self.ax.clear()
        self.ax.set_title("All 24Bit AD")
        self.ax.set_ylim(mi,ma) # 10% under and over
        for colIdx in range(self.n_col):
            self.ax.plot(self.times, self.col[colIdx], label= self.columnNames[colIdx+1])
        self.ax.legend(loc=2)
        self.canvas.draw()
        pass

    def plotOne(self): #, treeview, path, view_column):
        #self.line.set_ydata(self.press)
        if self.plotColumn == 0:
            print("cant plot time vs time")
            return
        #print("Plot column ", self.plotColumn, len(self.col))
        colData = self.col[self.plotColumn-1]
        #print("ColData:", colData)
        mi = np.min(colData)
        ma = np.max(colData)
        self.ax.clear()
        #print("min max", mi, ma)
        r = (ma-mi) *0.1
        if r < ma*0.5:
            r+=ma*0.5
        mi -= r
        ma += r
        #print("revised min max", mi, ma)
        self.line, = self.ax.plot(self.times, colData )  # plot the first row
        self.ax.set_title(self.columnNames[self.plotColumn])
        self.ax.set_ylim(mi,ma) # 10% under and over
        self.canvas.draw()
        
    def updatePlot(self):
        if self.plotColumn > 0 :
            self.plotOne()
        else:
            self.plotAll()
                
    def printList(self,widget):
        for row in self.listStore :
            print(row[:])
    
    def clickedColumn(self, treeCol, idx):
        #print("clicked column ", idx, self.columnNames[idx])
#        if idx == 0:
#            print("Cant plot time")
#            return
        self.plotColumn = idx
        self.updatePlot()

    def update(self):
        self.getData()
        self.updatePlot()
