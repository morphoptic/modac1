import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class DialogExample(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        box = self.get_content_area()
        
        label = Gtk.Label("This is a dialog to display additional information")
        box.add(label)
       
        # adj = Gtk.Adjustment(timing, 1, this._maxRange, 1, 10)
        adj = Gtk.Adjustment (1.0, 1.0, 240.0, 1.0, 10.0);
        #creates the spinbutton, with no decimal places
        #  button = gtk_spin_button_new (adjustment, 1.0, 0);
        self.spinbutton = Gtk.SpinButton (adjustment=adj, climb_rate=1, digits=0);
        #button.set_adjustment(adjustment)
        self.spinbutton.set_numeric(True)

        box.add(self.spinbutton)
        
        self.show_all()
    def get_value(self):
        return self.spinbutton.get_value()
    
class DialogWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Dialog Example")

        self.set_border_width(6)
        box = Gtk.Box(spacing=6)
        self.add(box)

        button1 = Gtk.Button("Open SpinTest")
        button1.connect("clicked", self.on_spinbutton_clicked)
        box.add(button1)

        button2 = Gtk.Button("Open dialog")
        button2.connect("clicked", self.on_warn_clicked)
        box.add(button2)

    def on_spinbutton_clicked(self, widget):
        # dialog = CsvTimeStepDialog(self, self.csvStep)
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK_CANCEL, "Set CSV Time Step")
        box = dialog.get_content_area()
        label = Gtk.Label("Seconds between CSV row recording:")
        box.add(label)
        # adj = Gtk.Adjustment(timing, 1, this._maxRange, 1, 10)
        self.csvStep = 1
        self.maxCsvRange = 240
        adj = Gtk.Adjustment (self.csvStep, 1.0, self.maxCsvRange, 1.0, 10.0);
        #creates the spinbutton, with no decimal places
        #  button = gtk_spin_button_new (adjustment, 1.0, 0);
        spinbutton = Gtk.SpinButton (adjustment=adj, climb_rate=1, digits=0);
        #button.set_adjustment(adjustment)
        spinbutton.set_numeric(True)

        box.add(spinbutton)
        box.show_all()

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            result = spinbutton.get_value()
            print("spin dialog result: ", result)
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()
        
    def on_warn_clicked(self, widget):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK_CANCEL, "This is an WARNING MessageDialog")
        dialog.format_secondary_text(
            "And this is the secondary text that explains things.")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("WARN dialog closed by clicking OK button")
        elif response == Gtk.ResponseType.CANCEL:
            print("WARN dialog closed by clicking CANCEL button")
        dialog.destroy()

win = DialogWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
