# moPanelTempPlot a tab for moTkShell to display temperature table and matplot
# skips the middle, unconnected thermocouple, and the external (near Baumer)
from datetime import datetime
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
# import colorlog
# handler = colorlog.StreamHandler()
# handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
# log = colorlog.getLogger(__name__)
# log.addHandler(handler)

log = logging.getLogger(__name__)

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from modac.moKeys import *
from modac import moData

log.setLevel(logging.DEBUG)

class moPanelTempPlot():
    def getTitle(self):
        return self.tabTitle

    def __init__(self,frame):
        # Upper panel contains an table of max 100 (plotwidth) entrys
        # lower panel is graph of same data
        self.frame = frame
        self.tabTitle = "K-type+Dist"
        self.maxRows = 100  # __plotWidth # for some reason it is not accepting __plotWidth

        now = datetime.now()
        self.count = 0
        self.columnNames = ("time", "AvgT", "Lower", "Middle", "Upper")
        self.n_col = len(self.columnNames)
        print("self.columnNames", self.columnNames,self.n_col)
        self.times = [now]*self.maxRows
        #self.data = [[0] * self.maxRows] * self.n_col
        # we know what we got, and can skip the 2d array
        self.avgT = [0]*self.maxRows
        self.lowerT = [0]*self.maxRows
        self.middleT = [0]*self.maxRows
        self.upperT = [0]*self.maxRows
        self.distance = [0]*self.maxRows
        self.minData = 1000 # instead of using numpy min/max just keep em on the fly
        self.maxData = 0 # although this may be an issue when overall min/max scroll off
        self.stateName = None

        self.upperPanel = None
        self.lowerPanel = None
        self.treeView = None
        self.fig = None
        self.canvas = None
        self.subplot = None

        self.buildTablePanel()
        self.buildGraphPanel()
        self.updateFromMoData()  # fill in from whatever is in the data

    def buildTablePanel(self):
        self.upperPanel = tk.Frame(self.frame, bg="blue")
        self.treeView = ttk.Treeview(self.upperPanel, columns=self.columnNames, height=5)
        self.treeView['show'] = 'headings'
        for colName in self.columnNames:
            self.treeView.column(colName, width=10, anchor='c')
            self.treeView.heading(colName, text=colName, command=lambda c=colName: self.selectColumn(c))

        vScroll = ttk.Scrollbar(self.upperPanel,
                                   orient=tk.VERTICAL,
                                   command=self.treeView.yview)

        # Calling pack method w.r.to verical
        # scrollbar
        vScroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Configuring treeview
        self.treeView.configure(yscrollcommand=vScroll.set)
        self.treeView.pack(side=tk.TOP, fill=tk.X)

        # placeholder = tk.Label(self.upperPanel, text="Table will go here")
        # placeholder.pack()
        self.upperPanel.pack(side=tk.TOP, fill=tk.X)

    def selectColumn(self, colName):
        print("In Select Column ", colName)
        print("column is",self.treeView.columns[colName])

    def buildGraphPanel(self):
        self.lowerPanel = tk.Frame(self.frame, bg="green", height=360)
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.lowerPanel)  # a Gtk.DrawingArea

        # put something in the graph. it will replave on frist updateFromMoData()/plotAll()
        self.subplot = self.fig.add_subplot(1, 1, 1)
        self.subplot.set_title("avg, bottom & top kType Thermocouples")
        self.subplot.legend(loc=2)

        line, = self.subplot.plot(self.times, self.avgT)  # plot the first column
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.lowerPanel.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

    def updateFromMoData(self):
        kilnStatus = moData.getValue(keyForKilnStatus())
        print("Kilnstatus:", kilnStatus)
        self.timestamp = moData.getValue(keyForTimeStamp())
        try:
            dtime = datetime.strptime(self.timestamp, moData.getTimeFormat() )
        except ValueError:
            # probably first one with NoDataYet
            dtime = datetime.now()
        ktypes = kilnStatus[keyForKilnTemperatures()]
        distance = kilnStatus[keyForCurrentDisplacement()]

        self.count = self.count+1
        #self.times.append(self.count)
        self.times.append(dtime)
        self.times.pop(0)

        if self.count % (self.maxRows/2) == 0:
            log.debug("hit count mod maxRows, so recalc max/min")
            self.recalcDataMaxMin()

        a = ktypes[0]
        b = ktypes[1]
        m = ktypes[2]
        t = ktypes[3]
        self.minMax(a)
        self.minMax(b)
        #self.minMax(m)
        self.minMax(t)
        self.avgT.append(a)
        self.avgT.pop(0)
        self.lowerT.append(b)
        self.lowerT.pop(0)
        self.middleT.append(m)
        self.middleT.pop(0)
        self.upperT.append(t)
        self.upperT.pop(0)

        row = [self.timestamp, str(a), str(b), str(m), str(t)]
        self.treeView.insert("", 0, values=row)
        # now remove last/oldest row
        children = self.treeView.get_children()
        if len(children) > self.maxRows:
            lastIID = children[-1]
            self.treeView.delete(lastIID)

        self.plotTemps()

    def plotTemps(self):
        mi = self.minData - (self.minData * 0.1)
        ma = self.maxData + (self.maxData*0.1)
        if ma < 100:
            ma = 100 # min size is 0-100
        print("plotAll mi ",mi, "ma", ma)
        if mi < 0:
            mi = self.minData

        self.subplot.clear()
        self.subplot.set_ylim(mi, ma)

        # xfmt = matplotlib.dates.DateFormatter('%a %H:%M:%S')
        # self.subplot.xaxis.set_major_formatter(xfmt)
        # formatting could be done in creation, not each rebuild
        self.subplot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%a %H:%M:%S'))
        # self.subplot.xaxis.set_major_locator(matplotlib.dates.HourLocator())
        self.subplot.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(10))
        # self.subplot.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(byminute=range(60,5)))
        # self.subplot.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%M:%S"))
        self.subplot.xaxis.set_minor_locator(matplotlib.dates.MinuteLocator())


        #self.subplot.set_xticks(self.times)
        self.subplot.plot(self.times, self.avgT, label="averageT")
        self.subplot.plot(self.times, self.lowerT, label="lowerT")
        #self.subplot.plot(self.times, self.middleT, label="middleT")
        self.subplot.plot(self.times, self.upperT, label="upperT")

        self.fig.autofmt_xdate()
        self.canvas.draw()
        log.debug("plot frame height "+ str(self.lowerPanel.winfo_height()))

        pass

    def recalcDataMaxMin(self):
        log.debug("recalcDataMaxMin count:", str(self.count), "was min", str(self.minData) , " max ",str(self.maxData))
        self.minData = 1000 # instead of using numpy min/max just keep em on the fly
        self.maxData = 0 # although this may be an issue when overall min/max scroll off
        for i in range(self.maxRows):
            self.minMax(self.avgT[i])
            self.minMax(self.lowerT[i])
            #self.minMax(self.middleT[i])
            self.minMax(self.upperT[i])
        log.debug("recalcDataMaxMin new min/max "+str(self.minData) + ":" + str(self.maxData))

    def minMax(self,datum):
        if datum < self.minData:
            self.minData = datum
        if datum > self.maxRows:
            self.maxData = datum


