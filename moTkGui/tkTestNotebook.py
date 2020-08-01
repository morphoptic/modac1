import tkinter as tk
import tkinter.ttk as ttk

main = tk.Tk()
main.title("Notebook test")
main.geometry('800x600')

rows =0
while rows < 50:
    main.rowconfigure(rows, weight=1)
    main.columnconfigure(rows, weight=1)
    rows += 1

nb = ttk.Notebook(main)
nb.grid(row=1,column=0, columnspan=50, rowspan=49, sticky='NSEW')

tab1 = ttk.Frame(nb)
nb.add(tab1, text='Tab1')

tab2 = ttk.Frame(nb)
nb.add(tab2, text='Tab2')

main.mainloop()