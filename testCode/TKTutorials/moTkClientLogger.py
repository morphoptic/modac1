# moTkClientLogger - modac client msg/data logger with TK GUI
#

import datetime
from time import sleep
import sys
this = sys.modules[__name__]
import os
import argparse
import json

import tkinter as tk

window = tk.Tk()
window.geometry('600x400')
window.title("MODAC Data Logger")

### some stand in gui elements
l1 = tk.Label(window, text="edureka!", font=("Arial Bold", 20) )
l1.grid(column=0, row=0)

txt = tk.Entry(window, width=10)
txt.grid(column=0, row=1)

def clicked():
    res = "Welcome to " + txt.get()
    l1.configure(text=res)

bt = tk.Button(window, text="Copy To Label",bg="orange", fg="green", command = clicked)
bt.grid(column=1, row=1)

from tkinter.ttk import *
combo = Combobox(window)
combo['values']= (1, 2, 3, 4, 5, "Text")
combo.current(5)
combo.grid(column=0, row=2)

from tkinter import scrolledtext
stxt = scrolledtext.ScrolledText(window, width=20,height=10)
stxt.grid(column=0, row=5)
stxt.insert(tk.END,"This is\n the first\n text")

from tkinter import messagebox
def clicked2():
    messagebox.showinfo('Message title', l1.cget("text"))
btn2 = Button(window, text="Show MessageBox", command=clicked2)
btn2.grid(column=2, row=6)

# simple version would stop here, using one or other technique here to show UI
#window.mainloop()
#while 1:
#    window.update()

##############################
# now the trio stuff for logging
# cp/pastes from modac_netLogger.py


##############################
# now the main loop stuff

while 1:
    window.update()

