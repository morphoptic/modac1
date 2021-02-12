# from https://python-forum.io/Thread-Adding-timer-on-the-Messagebox

import tkinter as tk

APP_TITLE = "Count Down Box"
APP_XPOS = 100
APP_YPOS = 100
APP_WIDTH = 350
APP_HEIGHT = 200


class CountDownMessageBox(tk.Toplevel):
    TEXT_FONT = ('Helevtica', 12, 'bold')
    TEXT = "This process may take up to 2 min. Please try after 2min..!"
    TIMER_FONT = ('Helevtica', 16, 'bold')
    TIMER_COUNT = 10  # Seconds

    def __init__(self, app, msg_text=TEXT):
        self.app = app
        self.msg_text = msg_text

        tk.Toplevel.__init__(self, app.main_win)

        self.build()

    def build(self):
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, padx=20, pady=20)

        message_var = tk.StringVar(self.app.main_win, self.msg_text)
        tk.Label(main_frame, bitmap='hourglass', padx=10, font=self.TEXT_FONT,
                 compound='left', textvariable=message_var, wraplength=200,
                 fg='gray40').grid(row=0, column=0)

        self.timer_var = tk.StringVar()
        tk.Label(main_frame, textvariable=self.timer_var, font=self.TIMER_FONT,
                 fg='blue').grid(row=1, column=0, padx=20, pady=20)

        self.count_down()

    def count_down(self, time_count=TIMER_COUNT):
        self.timer_var.set("{} Seconds".format(time_count))
        if time_count == 0:
            self.destroy()
            self.app.count_down_callback()
        time_count -= 1
        self.after(1000, self.count_down, time_count)


class Application:

    def __init__(self, main_win):
        self.main_win = main_win

        self.count_down = False
        self.build()

    def build(self):
        self.main_frame = tk.Frame(self.main_win)
        self.main_frame.pack(fill='both', expand=True)

        wifiOnButton = tk.Button(self.main_win, text="WiFi-ON",
                                 command=self.wifiOnscript, height=1, width=22)
        wifiOnButton.pack(expand=True, padx=40, pady=10)

    def wifiOnscript(self):
        if not self.count_down:
            CountDownMessageBox(self)

    def count_down_callback(self):
        print("Count down finished!")


def main():
    main_win = tk.Tk()
    main_win.title(APP_TITLE)
    main_win.geometry("+{}+{}".format(APP_XPOS, APP_YPOS))
    # main_win.geometry("{}x{}".format(APP_WIDTH, APP_HEIGHT))

    app = Application(main_win)

    main_win.mainloop()


if __name__ == '__main__':
    main()