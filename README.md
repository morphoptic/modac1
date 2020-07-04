#Morph Optics Data Acquistion (MODAC) Proof Of Concept#

MODAC is a generic Data Acquisition and Control tool built on Raspberry Pi as a Client/Server tool.
It uses the pyNNG brokerless messaging system for IP based communications. The server uses the Trio async library. Gui tools rely on GTK for pseudo-async

Thop folder holds the MODAC Proof of Concept Code & some other assets. 
Documentation is currently on GoogleDrive and *may* migrate here.

testCode and MODAC_UnitTests contain the python scripts used to test components of MODAC
Due to nature of Packages, some subfolders are used to create support libraries that are imported into tools while others hold operational tests. Some migrated to this top level for quick tests.

Postprocessing holds python code to process various CSV files for comparisons with original controller.

scripts holds various shell scripts to start the tools from command line (or autostart on boot).

setupPi holds the scripts to pull various libraries.

waveshareADAC is package for the 24bit AD Waveshare board.

thermocouple is the package for converting between degC and mV for various thermocouples. Most other imports are installed system wide.

MODAC_Config were experiements in config files. We currently use variables in python files (see docs)

modac is the package holding most of the MODAC generic DA code

kilnControl is package holding the kiln specific parts

modacServer.py is main server script

moGui_all.py is GTK GUI app with all panels

moGui_Kiln.py is GTK Gui stripped down for just kiln control.

------
(older info, see documentation for *more* up to date stuff)

Current system is a server/client setup where the server runs
the hardware and publishes data on a PyNNG pub/sub channel, while listening for commands on a Pair1 link
Clients subscribe to the data channel and send commands to server on the Pair1 link 
multiple clients are allowed. they dont know about each other.
Current PyNNG uses fixed ip addresses, and only works with the rPi
Phase 3 will add clients on a PC and perhaps use some zeroConfig ip address resolution

Both client and server architectures share common code but add their own specifics
modac folder contains the internals of modac for both server and client
modacGUI folder holds python code and Glade layout definitions for gtk clients

Basic action is for leica to run on its own, measuring every second or so (see code for delay),
while cmd receiving loop runs async reads (await sock.aread())
and the main loop periodically takes the full moData dictionary and publishes it

modac/moHardware is the common hardware abstraction module. Server interacts with this and it deals
with lower level hardware stuff... mostly by invoking hardware specific modules
ad24 - 24bit AD board with 8 chan via spi  (board also has 2 DA channels we dont use yet)
ad16 - 16bit AD on at least one i2c board 4 channels each
binaryOutputs - relay board and the relay controlled power outlet.
ktype - uses defined channels from ad24 as K-Type thermocouples, giving DegC readings vs 0-5v of AD
enviro - i2c board giving temp, humidity and pressure

moData is a data dictionary that gets populated by either hardware or network data
moKeys provides functions for keys to the moData dictionary, and key names for network commands
moCommand  provides command senders

moServer - encapuslates server methods
moClient - basics for client tools

moNetwork - low level stuff for network, creating/unpacking packets, encrypting, etc
moCSV - module to export moData into a CSV file

