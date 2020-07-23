# Tkinker tutorial tktutorial1.py
# written following https://www.edureka.co/blog/tkinter-tutorial/

import tkinter as tk

window = tk.Tk()
window.geometry('600x400')

# to rename the title of the window window.title("GUI")
 
# pack is used to show the object in the window
#label = tk.Label(window, text = "Hello World!").pack()

l1 = tk.Label(window, text="edureka!", font=("Arial Bold", 20) )
l1.grid(column=0, row=0)

txt = tk.Entry(window, width=10)
txt.grid(column=0, row=1)

def clicked():
    res = "Welcome to " + txt.get()
    l1.configure(text=res)

def clicked1():
    l1.configure(text="Button was clicked !!")

bt = tk.Button(window, text="Copy To Label",bg="orange", fg="green", command = clicked)
bt.grid(column=1, row=1)

from tkinter.ttk import *
combo = Combobox(window)
combo['values']= (1, 2, 3, 4, 5, "Text")
combo.current(5)
combo.grid(column=0, row=2)

chk_state = tk.BooleanVar()
chk_state.set (True)
chk = tk.Checkbutton(window, text="Select", var=chk_state)
chk.grid(column=0, row=3)

rad1 = Radiobutton(window, text="Python", value=1)
rad2 = Radiobutton(window, text="Java", value=2)
rad3 = Radiobutton(window, text="Scala", value=3)
rad1.grid(column=0, row=4)
rad2.grid(column=1, row=4)
rad3.grid(column=2, row=4)

from tkinter import scrolledtext
stxt = scrolledtext.ScrolledText(window, width=20,height=10)
stxt.grid(column=0, row=5)
stxt.insert(tk.END,"This is\n the first\n text")

from tkinter import messagebox
def clicked2():
    messagebox.showinfo('Message title', l1.cget("text"))
btn2 = Button(window, text="Show MessageBox", command=clicked2)
btn2.grid(column=2, row=6)

spin = Spinbox(window, from_=0, to=100, width=10)
spin.grid(row=7)

#window.mainloop()
while 1:
    window.update()
