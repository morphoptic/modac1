# moTkShared - data and methods shared w others in moTk
import os
from singleton_decorator import singleton
import datetime

@singleton
class moTkShared():
    def __init__(self):
        now = datetime.datetime.now()
        self.root = None
        self.startTimeStr = now.strftime("%Y%m%d_%H%M")
        cwd = os.getcwd()
        self.last_open_dir = cwd+"/logs/"
        self.csvFilename = self.last_open_dir+"moTkShell_" + self.startTimeStr + ".csv"
        self.csvStep = 60 # once per minute is default
        self.lastCsvStep = None
        self.csvActive = False


