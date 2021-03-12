import tkinter as tk

top = tk.Tk()
Texts = ["12V Power", "Lower Heater", "Middle Heater","Upper Heater","NC 4","NC 5","NC 6","NC 7","NC 8","SupportFan","ExhaustFan"]
CmdBVar =[]
RptBVar = []
Commanded = []
Reported = []

def callback(idx):
    print(idx, Texts[idx], CmdBVar[idx].get())

header0 = tk.Label(text="Relay Command")
header0.grid(row=0, column=0)
header1 = tk.Label(text="Relay Reported")
header1.grid(row=0, column=1)

for i, z in enumerate(Texts):
    CmdBVar.append(tk.BooleanVar(top, False))
    RptBVar.append(tk.BooleanVar(top, False))
    Commanded.append(tk.Checkbutton(top, text=z, onvalue=True, offvalue=False,
                                    variable=CmdBVar[i], command=lambda itemp=i: callback(itemp)))
    Commanded[i].grid(row=i+1, column=0)
    Reported.append(tk.Checkbutton(top, text=z, onvalue=True, offvalue=False, state = tk.DISABLED, variable=RptBVar[i]))
    Reported[i].grid(row=i+1, column=1)

top.mainloop()
