# modacGUI leica Panel 1

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
from modac import moCommand

### kinda messy having global
# TODO: replace columnNames and plotWidth with Config values

class leicaPanel():
    plotWidth = 100 #__plotWidth # for some reason it is not accepting __plotWidth
    columnNames = ['time','dist']

    def __init__(self):
        self.key = keyForLeicaDisto()
        self.box = Gtk.VBox(homogeneous=False, spacing=8)
        self.label = Gtk.Label("Leica Dist")
        
        self.resetBtn = Gtk.Button("Reset Leica")
        self.resetBtn.set_property("width-request",200)
        self.resetBtn.set_property("height-request",25)
        self.resetBtn.show()
        self.resetBtn.connect("clicked", self.on_clicked_resetBtn)
        # add 
        self.box.pack_start(self.resetBtn, False,False,0)
    
        ### setup Plot Data 
        self.count=0
        self.times = [0]*self.plotWidth
        self.distance = [0]*self.plotWidth
        
        ### setup Table (aka listStore) in a ScrollWindow
        colTypes = [str]*2

        # so how do we get it to be types ?
        self.listStore = Gtk.ListStore()
        self.listStore.set_column_types(colTypes)#str,str,str,str)
        #self.listStore = Gtk.ListStore(str,float, float, float)
        self.treeview = Gtk.TreeView(model=self.listStore)
        for i in range( len(self.columnNames)) :
            column = Gtk.TreeViewColumn(self.columnNames[i], Gtk.CellRendererText(),text=i)
            column.set_min_width(100)
            column.set_alignment(0.5)
            column.set_clickable(True)
            #column.connect("clicked", self.clickedColumn, i)
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
        self.line, = self.ax.plot(self.times, self.distance)  # plot the first row
        #self.lowerScroll.add_with_viewport(self.canvas)
        #print("canvas: ", self.canvas)
        self.upperScroll.show()
        self.canvas.show()
        self.box.show()
        
    def getData(self):
        # network got something - hopefully dispatched  already so moData is updated
        # ToDo: check timestamp ? if it is same as last, then nothing changed (so what was received?)
        lData = moData.getValue(keyForLeicaDisto())
        #print("leicaPanel.getData = ", lData)
        self.timestamp = lData[keyForTimeStamp()]
        data = lData[keyForDistance()]
        #print(self.key+" Update = ", data)
        
        self.count = self.count+1

        #update local data arrays
        self.times.append(self.count)
        self.distance.append(data)
        
        #limit size of arrays
        self.times = self.times[-self.plotWidth:]
        self.distance = self.distance[-self.plotWidth:]

        # create strings for listStore and add them at top
        it = self.listStore.prepend([self.timestamp,str(data)])
        # and limit the listStore
        try:
            if len(self.listStore) > self.plotWidth:
                it = self.listStore.iter_nth_child(None,self.plotWidth)
                self.listStore.remove(it)
        except :
            #print(self.key+"got an exception removing from listStore")
            log.error(self.key+" Exception happened", exc_info=True)
            pass
        
        return True
    
        
    def plotOne(self): #, treeview, path, view_column):
        if self.plotColumn == 0:
            log.error("cant plot time vs time")
            return
        #print(self.key+" Plot column ", self.plotColumn)
        colData = self.distance
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
        #Wprint("updatePlot column", self.plotColumn, self.colNames[self.plotColumn])
        self.plotOne()
            
    def clickedColumn(self, treeCol, idx):
        #print("clicked column ", idx, self.columnNames[idx])
        self.plotColumn = idx
        self.updatePlot()

    def update(self):
        self.getData()
        self.updatePlot()

    def on_clicked_resetBtn(self, button):
        moCommand.cmdResetLeica()
        pass
    
