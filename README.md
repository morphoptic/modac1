#Morph Optics Data Acquistion (MODAC) Unit Tests
This folder holds python tools for testing MODAC components. 
Contents may vary over time with older versions moving to sub folder oldTests.

Due to nature of Packages, some subfolders are used to create support libraries that are imported into tools
while others hold operational tests

MODAC_UnitTests contains the python scripts used for the Phase 1 development
MODAC_Phase1Code is the code used at Demo.
ian-BlueToothDistance is code from Ian's git repo to support the BlueTooth Laser distance sensor
oldTests is experimental scaffolding code to test out stuff. this may vanish in later builds as git works
github user morphoptic  repo modac1

------

Current Phase 2 system has evolved to a server/client setup where the server (modac_io_server.py) runs
the hardware and publishes data on a PyNNG pub/sub channel, while listening for commands on a Pair1 link
Clients subscribe to the data channel and send commands to server on the Pair1 link 
multiple clients are allowed. they dont know about each other.
Current PyNNG uses fixed ip addresses, and only works with the rPi
Phase 3 will add clients on a PC and perhaps use some zeroConfig ip address resolution

Both client and server architectures share common code but add their own specifics
modac folder contains the internals of modac for both server and client
modacGUI folder holds python code and Glade layout definitions for gtk clients

testPanel is used to test UI panels. a couple edits and it can test different panels
moGui_1 is the combined gui - it uses a tabbed Notebook style to support multiple panels

modac_io_server is the only real server code
It uses the Trio system for async threading.  It has threads (or whatever they are) for:
  * main publishing loop
  * cmd receiving loop
  * leica Disto BLE device management

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

