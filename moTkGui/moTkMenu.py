# moTKMenu - Top level Menu for modac TK GUI apps
# add to a window
from tkinter import *
from tkinter.filedialog import askopenfilename


def NewFile():
    print("New File!")

def OpenFile():
    name = askopenfilename()
    print(name)

def About():
    print("This is a simple example of a menu")

class moMenu():
    def __init__(self, moWin):
        moRoot = moWin.root()
        self.menu = Menu(moRoot)
        moRoot.config(menu=menu)

        self.filemenu = Menu(menu)
        self.menu.add_cascade(label="File", menu=filemenu)
        self.filemenu.add_command(label="Set CSV RecordRate", command=setCSVTiming)
        self.filemenu.add_command(label="Set CSV File", command=setCSVFile)
        self.filemenu.add_command(label="Start CSV File", command=startCSVRecording)
        self.filemenu.add_command(label="Stop CSV Recording", command=stopCSVRecording)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Terminate Server", command=terminateServer) # too simple?
        self.filemenu.add_command(label="Exit", command=doExit) # too simple?

        self.helpmenu = Menu(menu)
        #self.menu.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="About...", command=About)