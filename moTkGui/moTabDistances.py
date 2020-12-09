#moPanelTempPlot a tab for moTkShell to display temperature table and matplot
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

class moTabDistances():
    def getTitle(self):
        return self.tabTitle

    def __init__(self,frame):
        # Upper panel contains an table of max 100 (plotwidth) entrys
        # lower panel is graph of same data
        self.frame = frame
        self.tabTitle = "Distances"
        self.maxRows = 100  # __plotWidth # for some reason it is not accepting __plotWidth


        # data for table and graphs
        now = datetime.now()
        self.count = 0
        self.columnNames = ("time", "RawMM", "SlumpMM")
        self.n_col = len(self.columnNames)
        print("self.columnNames", self.columnNames,self.n_col)
        self.times = [now]*self.maxRows

        # we know what we got, and can skip the 2d array
        #self.rawMM = [0]*self.maxRows
        self.slumpMM = [0]*self.maxRows
        self.minData = 1000 # instead of using numpy min/max just keep em on the fly
        self.maxData = 0 # although this may be an issue when overall min/max scroll off
        self.stateName = None

        self.upperPanel = None
        self.lowerPanel = None
        self.treeView = None
        self.fig = None
        self.canvas = None
        self.subplot = None

        self.buildUpperPanel()
        self.buildGraphPanel()
        self.updateFromMoData()  # fill in from whatever is in the data

    def buildUpperPanel(self):
        self.upperPanel = tk.Frame(self.frame, bg="blue")
        self.valuePanel = tk.Frame(self.upperPanel, bg = "linen")
        # TODO this time we should add a row for Orig and Target Distances

        self.distanceLabel = tk.Label(self.valuePanel, text="RawDistance: ----")
        self.distanceLabel.grid(row=0, column=0, sticky=tk.NW)

        # these from KilnStatus; current dist here may not == distance
        self.currentDistanceLabel = tk.Label(self.valuePanel, text="CurrDist: ----")
        self.currentDistanceLabel.grid(row=0, column=1, sticky=tk.N)

        self.startDistanceLabel = tk.Label(self.valuePanel, text="StartDist: ----")
        self.startDistanceLabel.grid(row=0, column=2, sticky=tk.NE)

        self.targetDisplacementLabel = tk.Label(self.valuePanel, text="target Slump: ----")
        self.targetDisplacementLabel.grid(row=1, column=0, sticky=tk.SW)

        self.currentDisplacementLabel = tk.Label(self.valuePanel, text="current Slump: ----")
        self.currentDisplacementLabel.grid(row=1, column=1, sticky=tk.SE)

        self.valuePanel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

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
        self.subplot.set_title("Distances")
        self.subplot.legend(loc=2)

        line, = self.subplot.plot(self.times, self.slumpMM)  # plot the slump only
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.lowerPanel.pack(side=tk.BOTTOM, fill=tk.X, expand=1)

    def updateFromMoData(self):
        self.timestamp = moData.getValue(keyForTimeStamp())
        try:
            dtime = datetime.strptime(self.timestamp, moData.getTimeFormat())
        except ValueError:
            # probably first one with NoDataYet
            dtime = datetime.now()
        self.count = self.count+1
        #self.times.append(self.count)
        self.times.append(dtime)
        self.times.pop(0)

        # rawDist is top level keyForDistance() while currentDistance should be same in KilnStatus but may not ==
        rawDistance = moData.getValue(keyForDistance())
        kilnStatus = moData.getValue(keyForKilnStatus())
        # print("Kilnstatus:", kilnStatus)

        targetDisplacement = kilnStatus[keyForTargetDisplacement()]
        startDistance = kilnStatus[keyForStartDistance()]
        currentDistance = kilnStatus[keyForCurrentDistance()]
        currentDisplacement = kilnStatus[keyForCurrentDisplacement()]

        # Update the sorta static values
        self.distanceLabel.config(text="RawDistance: " + str(rawDistance))
        # these from KilnStatus; current dist here may not == distance
        self.currentDistanceLabel.config(text="CurrDist: " + str(currentDistance))

        self.startDistanceLabel.config(text="StartDist: " + str(startDistance))
        self.targetDisplacementLabel.config(text="target Slump: : " + str(targetDisplacement))
        self.currentDisplacementLabel.config(text="current Slump:: " + str(currentDisplacement))

        # add currents to arrays
        #self.rawMM.append(rawDistance)
        #self.rawMM.pop(0)

        self.slumpMM.append(currentDisplacement)
        self.slumpMM.pop(0)
        self.minMax(currentDisplacement)

        if self.count % (self.maxRows/10) == 0:
            log.debug("hit count mod maxRows, so recalc max/min")
            self.recalcDataMaxMin()

        #insure min max for chart
        #self.minMax(rawDistance)
        #self.minMax(currentDisplacement)

        #update the table
        row = [self.timestamp, str(rawDistance), str(currentDisplacement)]
        self.treeView.insert("", 0, values=row)
        # now remove last/oldest row
        children = self.treeView.get_children()
        if len(children) > self.maxRows:
            lastIID = children[-1]
            self.treeView.delete(lastIID)

        self.plot()

    def plot(self):
        mi = self.minData - (self.minData * 0.1)
        ma = self.maxData + (self.maxData*0.1)
        if ma < 10:
            ma = 10 # min size is 0-100
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
        #self.subplot.plot(self.times, self.rawMM, label="rawMM")
        self.subplot.plot(self.times, self.slumpMM, label="slumpMM")

        self.fig.autofmt_xdate()
        self.canvas.draw()
        log.debug("plot frame height "+ str(self.lowerPanel.winfo_height()))

        pass

    def recalcDataMaxMin(self):
        log.debug("recalcDataMaxMin count:", str(self.count), "was min", str(self.minData) , " max ",str(self.maxData))
        self.minData = 2000 # instead of using numpy min/max just keep em on the fly
        self.maxData = 0 # although this may be an issue when overall min/max scroll off
        for i in range(self.maxRows):
            #self.minMax(self.rawMM[i])
            self.minMax(self.slumpMM[i])
        log.debug("recalcDataMaxMin new min/max "+str(self.minData) + ":" + str(self.maxData))

    def minMax(self,datum):
        if datum < self.minData:
            self.minData = datum
        if datum > self.maxData:
            self.maxData = datum


