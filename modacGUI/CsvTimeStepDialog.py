# CsvGetTimeStepDialog
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

_maxRange = 240

class CsvTimeStepDialog(Gtk.Dialog):

    def __init__(self, parent, initialValue= 1.0):
        Gtk.Dialog.__init__(self, "Set CSV Time Step", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        box = self.get_content_area()
        
        label = Gtk.Label("Seconds between CSV row recording:")
        box.add(label)
       
        # adj = Gtk.Adjustment(timing, 1, this._maxRange, 1, 10)
        adj = Gtk.Adjustment (initialValue, 1.0, 240.0, 1.0, 10.0);
        #creates the spinbutton, with no decimal places
        #  button = gtk_spin_button_new (adjustment, 1.0, 0);
        self.spinbutton = Gtk.SpinButton (adjustment=adj, climb_rate=1, digits=0);
        #button.set_adjustment(adjustment)
        self.spinbutton.set_numeric(True)

        box.add(self.spinbutton)
        self.show_all()
        
    def get_value(self):
        return self.spinbutton.get_value()
