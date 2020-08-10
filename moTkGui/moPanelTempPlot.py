#moPanelTempPlot a tab for moTkShell to display temperature table and matplot
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from modac.moKeys import *
from modac import moData


class moPanelTempPlot():
    def getTitle(self):
        return self.tabTitle

    def __init__(self,frame):
        # Upper panel contains an table of max 100 (plotwidth) entrys
        # lower panel is graph of same data
        self.frame = frame
        self.tabTitle = "K-type+Dist"
        self.maxRows = 100  # __plotWidth # for some reason it is not accepting __plotWidth

        self.count = 0
        self.columnNames = ("time", "AvgT", "Lower", "Middle", "Upper", "Distance")
        self.n_col = len(self.columnNames)
        print("self.columnNames", self.columnNames,self.n_col)
        self.times = [0]*self.maxRows
        self.data = [[0] * self.maxRows] * self.n_col
        self.stateName = None

        self.upperPanel = None
        self.lowerPanel = None
        self.treeView = None

        self.buildTablePanel()
        self.buildGraphPanel()
        self.updateFromMoData()

    def buildTablePanel(self):
        self.upperPanel = tk.Frame(self.frame, bg="blue")
        self.treeView = ttk.Treeview(self.upperPanel, columns=self.columnNames)
        self.treeView['show'] = 'headings'
        for colName in self.columnNames:
            self.treeView.column(colName, width=10, anchor='c')
            self.treeView.heading(colName, text=colName, command=lambda c=colName: self.selectColumn(c))

        vScroll = ttk.Scrollbar(self.upperPanel,
                                   orient=tk.VERTICAL,
                                   command=self.treeView)

        # Calling pack method w.r.to verical
        # scrollbar
        vScroll.pack(side=tk.LEFT, fill=tk.X)

        # Configuring treeview
        self.treeView.configure(yscrollcommand=vScroll.set)
        self.treeView.pack(side=tk.TOP, fill=tk.X)

        # placeholder = tk.Label(self.upperPanel, text="Table will go here")
        # placeholder.pack()
        self.upperPanel.pack(side=tk.TOP, pady=2, fill=tk.X)

    def selectColumn(self, colName):
        print("In Select Column ", colName)
        print("column is",self.treeView.columns[colName])

    def buildGraphPanel(self):
        self.lowerPanel = tk.Frame(self.frame, bg="green")
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.lowerPanel)  # a Gtk.DrawingArea

        self.ax = self.fig.add_subplot(1, 1, 1)
        line, = self.ax.plot(self.times, self.data[1])  # plot the first row

        #placeholder = tk.Label(self.lowerPanel, text="Graph will go here")
        #placeholder.pack()
        self.lowerPanel.pack(side=tk.BOTTOM, pady=2, fill=tk.X)

    def updateFromMoData(self):
        # TODO: remember scroll position and reset to there
        kilnStatus = moData.getValue(keyForKilnStatus())
        print("Kilnstatus:", kilnStatus)
        self.timestamp = moData.getValue(keyForTimeStamp())

        ktypes = kilnStatus[keyForKilnTemperatures()]
        distance = kilnStatus[keyForCurrentDisplacement()]

        self.count = self.count+1
        self.times.append(self.count)
        self.times = self.times[-self.maxRows:]

        row = [self.timestamp]
        for i in range(len(ktypes)):
            v = ktypes[i]
            self.data[i].append(v)
            self.data[i] = self.data[i][-self.maxRows:]
            row.append(str(v))
        row.append(str(distance))
        self.treeView.insert("", 0, values=row)
        children = self.treeView.get_children()
        if len(children) > self.maxRows:
            lastIID = children[-1]
            print("Childre ", children,"LastIID", lastIID)
            self.treeView.delete(lastIID)
        self.plotTemps()

    def plotTemps(self):
        mi = np.min(self.data)
        ma = np.max(self.data)
        print("data has:", len(self.data), self.data)
        print("min has:", len(mi), mi)
        print("max has:", len(ma), ma)
        r = (ma-mi) * 0.01
        if r < ma*0.5:
            r+=ma*0.5
        mi -= r
        ma += r
        print("plotAll min",mi, "max", ma)
        self.ax.clear()
        self.ax.set_title("All kType Thermocouples")
        self.ax.set_ylim(mi,ma) # 10% under and over
        for colIdx in range(self.n_col):
            self.ax.plot(self.times, self.data[colIdx], label= self.columnNames[colIdx+1])
        self.ax.legend(loc=2)
        self.canvas.draw()
        pass

