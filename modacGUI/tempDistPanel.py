# modacGUI panel showing K types and Leica Distance

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

numKTypeInKiln = 4

class tempDistPanel():
    plotWidth = 100 #__plotWidth # for some reason it is not accepting __plotWidth
    def __init__(self):
        
        self.box = Gtk.VBox(homogeneous=True, spacing=8)
        self.label = Gtk.Label("Temp/Distance")

        #n_col = moData.numKType() + 1 # + one for dist
        n_col = numKTypeInKiln + 1 # + one for dist
        #print("NumCol: ", n_col)
        # initialized array of data of plotWidth
        self.count=0
        self.times = [0]*self.plotWidth
        self.col = [ [0]*self.plotWidth ]*(n_col)
        #print("len self.col ", len(self.col))
        
        self.columnNames = ["time"]+["AvgT"]+["Lower"]+["Middle"]+["Upper"] +["Dist"]
        #print("Columns:", self.columnNames)
        ### setup Plot Data 
        
        ### setup Table (aka listStore) in a ScrollWindow
        colTypes = [str]*(n_col+1) # plus one for time
        self.listStore = Gtk.ListStore()
        self.listStore.set_column_types(colTypes)#str,str,str,str)

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
        self.kilnStatus = moData.getValue(keyForKilnStatus())
        if self.kilnStatus == keyForNotStarted():
            self.stateName = keyForNotStarted()
            return False
        self.timestamp = moData.getValue(keyForTimeStamp())
        kilnStatus = moData.getValue(keyForKilnStatus())
        
        ktypes = kilnStatus[keyForKilnTemperatures()]
        #print("kTypes Update = ", ktypes)
        #lData = moData.getValue(keyForLeicaDisto())
        #distance = lData[keyForDistance()]
        distance = kilnStatus[keyForCurrentDisplacement()]
        #print("leicaPanel.getData = ", lData)
        #self.timestamp = lData[keyForTimeStamp()]

        self.count = self.count+1
       
        #update local data arrays
        self.times.append(self.count)
        self.times = self.times[-self.plotWidth:]
        
        #start a row for table
        row = [moData.getValue(keyForTimeStamp())]
        #add values to data columns and row
        for i in range(len(ktypes)):
            v = ktypes[i]
            self.col[i].append(v)
            self.col[i] = self.col[i][-self.plotWidth:]
            row.append(str(v))
        
        distCol = len(ktypes)
        #print("distCol = ", distCol)
        self.col[distCol].append(distance)
        self.col[distCol] = self.col[distCol][-self.plotWidth:]
        row.append(str(distance))
        
       # create strings for listStore and add them at top
        it = self.listStore.prepend(row)
        # and limit the listStore
        try:
            if len(self.listStore) > self.plotWidth:
                it = self.listStore.iter_nth_child(None,self.plotWidth)
                self.listStore.remove(it)
        except :
            log.error("got an exception removing from listStore")
            log.error("Exception happened", exc_info=True)
            pass
        
        return True
    
    def plotOne(self): #, treeview, path, view_column):
        #self.line.set_ydata(self.press)
        if self.plotColumn == 0:
            log.error("cant plot time vs time")
            return
        #print("Plot column ", self.plotColumn, len(self.col))
        colData = self.col[self.plotColumn-1]
        #print("ColData:", colData)
        mi = np.min(colData)
        ma = np.max(colData)
        self.ax.clear()
        #print("min max", mi, ma)
        r = (ma-mi) *0.1
#        if r < 5:
#            r+=5
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
        #print("updatePlot column", self.plotColumn, self.columnNames[self.plotColumn])
        self.plotOne()
        
    def printList(self,widget):
        for row in self.listStore :
            print(row[:])
    
    def clickedColumn(self, treeCol, idx):
        #print("clicked column ", idx, self.columnNames[idx])
        if idx == 0:
            log.error("Cant plot time")
            return
        self.plotColumn = idx
        self.updatePlot()

    def update(self):
        #log.debug("KilnTemp-Dist panel update")
        if self.getData() == True:
            self.updatePlot()
