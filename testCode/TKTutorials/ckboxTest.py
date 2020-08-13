import tkinter as tk

class aTest():
    def __init__(self,frame):
        print("init aTest ", self)
        self.bVar = tk.BooleanVar()
        print("bVar is ",self.bVar)
        self.bVar.set(True)
        print("bVar value is ",self.bVar.get())
        self.ckbox = tk.Checkbutton(frame, text="myCkBox", variable=self.bVar, command=self.doCkBox)
        print("ckbox is ",self.ckbox)
        self.ckbox.pack()
        self.doCkBox()
    def doCkBox(self):
        print("in doCkBox: self ", self)
        print("bVar is ",self.bVar)
        print("bVar value is ",self.bVar.get())
        if self.bVar.get():
            self.ckbox.config(bg="cyan")
        else:
            self.ckbox.config(bg="red")

if __name__ == "__main__":
    print("Hello from main ")
    window = tk.Tk()
    myTest = aTest(window)
    print("window is ", window)
    print("myTest is ", myTest)

    window.mainloop()
