"""
Modac testPanel: unit test for Modac GTK panels
if a panel module provides box, update() and class creation
then this shell can quickly show it in a GTK Window
put module in... from modacGUI import ...
and then around line 94 set the self.panel
TODO: make module/calls nameing consistent, perhaps use panel() instead of box?
"""

import logging, logging.handlers

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GObject, Gio, Gtk
from gi.repository import GObject as Gobj

from modac import moLogger
if __name__ == "__main__":
    moLogger.init("testPanel")
    
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

from modac.moKeys import *
from modac import moData, moClient

#from modacGUI import tempDistPanel
from modacGUI import kilnPanel
#from modacGUI import enviroPanel, ktypePanel, ad24Panel,
# ad16Panel,leicaPanel, binaryOutPanel

appId = "com.TestPanel"

class TestPanelApp(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id=appId, flags=Gio.ApplicationFlags.FLAGS_NONE):
        # application_id needs to be in proper form com.modac.app1
        log.debug("Test appid: "+application_id)
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.new_window)
        self.connect("shutdown", self.shutdown)
        print("activated")
        # TODO: is there some Gtk.Application methods needed for shutdown and other mgmt?

    def new_window(self, *args):
        TestPanelWindow(self)

    def shutdown(self, *args):
        log.debug("App Shutdown")
        modacExit()

class TestPanelWindow(object):
    dataCount = 0
    def __init__(self, application):
        self.Application = application
        builder = None
        # Read GUI from file and retrieve objects from Gtk.Builder
        try:
            log.debug("load gui from file")
            builder = Gtk.Builder.new_from_file("modacGUI/testApp.glade")
            builder.connect_signals(self)
            log.debug("signals connected")
        except GObject.GError:
            log.debug("Error reading GUI file")
            raise
        # Fire up the main window
        self.MainWindow = builder.get_object("MainWindow")
        self.MainWindow.set_application(application)
        
        self.viewport = builder.get_object("MainViewport")
        
        # to change panel under test, simply load it here
        self.panel = kilnPanel.kilnPanel() # Panel to be tested
        #self.panel = ad24Panel.ad24Panel()
        #self.panel = ktypePanel.ktypePanel()
        
        
        self.panel.box.show()
        self.viewport.add(self.panel.box)
        #release builder ?
        
        # Start timer
        timer_interval = 1
        GObject.timeout_add_seconds(timer_interval, self.on_handle_timer)      

        log.debug("and ShowTime!")
        self.MainWindow.show()
            
    def close(self, *args):
        self.MainWindow.destroy()
    
    def on_winMain_destroy(self, widget, data=None):
        log.debug("on_winMain_destory")
        #modacExit()
        #Gtk.main_quit()

    def on_file_new_activate(self, menuitem, data=None):
        # debugging message
        log.debug('File New selected')
        
    def on_file_open_activate(self, menuitem, data=None):
        # debugging message
        log.debug('File OPEN selected')
        
    def on_file_quit_activate(self, widget, data=None):
        log.debug("on_file_quit")
        self.winMain.destroy()      

    def on_handle_timer(self):
        # update from network
        if not moClient.clientReceive():
            log.debug("on_handle_timer: no client data received")
            return True # keep listening
        self.panel.update()
        return True 
        
##################################
        
def modacExit():
    log.info("modacExit")
    moClient.shutdownClient()
    #sys.exit(0)
    
def modacInit():
    # setup MODAC data/networking
    moData.init()
    log.debug("try startClient()")
    moClient.startClient()
    log.debug("client started")

if __name__ == "__main__":
    #modac_argparse() # capture cmd line args to modac_args dictionary for others
    moLogger.init("moGUI_1") # start logging (could use cmd line args config files)
    log.debug("moGUI_1: modac from glade files")
    try:
        modacInit()
        Application = TestPanelApp(appId, Gio.ApplicationFlags.FLAGS_NONE)
        Application.run()
    except Exception as e:
        print("Exception somewhere in dataWindow. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("huh?")
    finally:
        print("end main of moGTKclient")
    modacExit()


