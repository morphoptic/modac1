MODAC - MorphOptic Data Acquisition and Control

proof of concept system - Summer 2020

Documentation Overview

(DRAFT)

June 2020 

MorpOptic Data Acquisition and Control (MODAC)

Documentation Overview

[[TOC]]

    1. 1 System Description

The MorpOptic Data Acquisition and Control (MODAC) project is a proof of concept general purpose Data Acquisition and Control (DAC) system written in Python on a Raspberry Pi (rPi).  Its preliminary use is to control a glass slumping kiln with a few extras, eg non-contact (laser) distance sensor, fans, etc.  For its generic DAC functionality, it supports binary outputs, 16 & 24 bit resolutions of Analog/Digital (AD) inputs, K-Type thermocouple support,  and expandable via I2C devices.  A separate Graphical User Interface (GUI) provides monitoring and control through an IP messaging protocol.

    2. 1.1 Basic Overview

The MODAC system was conceived as a modular system for collecting and controlling laboratory equipment.  The Proof of Concept (PoC) project was undertaken to build a basic framework around a Raspberry Pi (or equiv) system, with remote control access.  

*Web connection is not desired. System should be air gapped from internet, as overall system security of the PoC was not addressed.*

One half of the software (MODAC_Server) controls the hardware directly on a Raspberry Pi. It communicates over an IP Message Passing Protocol (i.e. NNG) with a Monitor/Control application that provides the human interface.  That User Interface (UI Client) application could run on the same rPi, or it could run on a different machine.  The message protocol is (very simply) encrypted and uses uncommon ports, providing a modicum of security with hooks to implement more robust protections if later required.

Modules supporting a variety of input/output devices are implemented, as are simple user interfaces for monitoring and controlling those devices.  All devices post their data to a common ‘blackboard’ (in memory data) which is shared with the UI Client.  Specific application (i.e. Kiln Control) can add their own data, processing and UI.

## 1.2 Online Archive:

*  [https://github.com/morphoptic](https://github.com/morphoptic)

*  [https://github.com/morphoptic/modac1](https://github.com/morphoptic/modac1)

## 1.3 Suggestions for next gen MODAC

* different/complete touch screen w/mount

    * Purchased touch screen requires careful mounting to avoid breakage

    * Alternate pre-mounted screens are available

* rPi + USB 5vdc power

    * the rPi gets power from a USB-B type cable providing 5vdc, 3A

    * provides only small Amp (0.5?) on USB ports

    * tried using a USB-B cable to connect to power bus but fails

        * Desktop UI has blinking lightning bolt in corner on low power

    * powered USB hub does not have power

* Utilize AC power distribution in cabinet

    * cabinet has 6 AC outlets and 1 breakered input that are unused

* External antenna for BLE/WiFi

    * unknown: the case may block RF sufficiently to make wireless comms unreliable.

# 2 User Documentation

* User Documentation will provide instruction on basic hardware setup and GUI use for Kiln Control.

The documentation is in a [google drive subFolder](https://drive.google.com/drive/folders/1_CS7XPMKPJ14HiZDGGAnZuaY4YvucM4z?usp=sharing), with [starting document](https://docs.google.com/document/d/131gk2v6jvdlfa9OxDu13b9-0aTxPXDuq0zz-3A7oEMg/edit?usp=sharing)

# 3 Design Documentation

Design documentation is intended for support engineers.  It gives an overview of the architecture, design constraints, and details of the hardware and software included in MODAC PoC, circa June/July 2020.

The [MODAC Design Documentation](https://docs.google.com/document/d/1IHdJdUaz1vRYGcZqRdQVnzF7wiIQA6-rH-l5l5adt78/edit?usp=sharing) is in a [google drive subfolder](https://docs.google.com/document/d/1IHdJdUaz1vRYGcZqRdQVnzF7wiIQA6-rH-l5l5adt78/edit?usp=sharing)

# 4 Overview Capabilities

## 4.1 MODAC is Two Programs: 

* Server – hardware control

* User Client – user interface

* IP communications (internal or over network)

* modular and adaptable design

## 4.2 Log, Data and Config Files

MODAC has several File artifacts. Kiln Scripts are used to step the system through a series of actions. Log files collect messages useful for debugging. CSV data files record sensor values.  Configuration files can change how MODAC operates.

### 4.2.1 Kiln Script 

Kiln Script files are JSON syntax file holding a series of Script Segments/Steps

* name, description fields (auto filled in gui) 

* Simulation Flag (allows testing MODAC logic)

* Series of Script Segments:

    * segment sequence number (index)

    * Target Temperature (degC)

    * Target Displacement (slump, mm)

    * Hold Time (after reach temperature)

    * Exhaust on/off

    * Pump on/off

    * 12v Heater Power on/off

[Here is an example Kiln Script](https://drive.google.com/file/d/1Qv0_Vp6CDvFj2TIiNejmkts55iJPkkxW/view?usp=sharing), used for a test run in early June 2020

### 4.2.2 Log Files

Log messages are written to files by both server and client into folder "logs"

Messages are produced using the Python Logging framework, with various levels (Info, Debug, Warning, Error). They are used liberally in the code base to provide some level of execution tracing.

* file name has the form: prefixYYYMMDD_HHMMSS.log 

* rolls over and renames older files to log.1, log.2 … etc

* each file has max size of 1Mb,

* highest numbered log file is oldest.

* rate of messages and verbosity can be changed by editing code

* server: modac20200207_160720.log.1

* client: modacGUI20200207_160757.log.5

### 4.2.3 CSV Data 

CSV Data files are written by server and optionally gui 

* server always on (saved in folder "logs")

* gui only on User start (user selected location/name)

* modacServerData_20200207_1607.csv

* columns determined by code in moCSV.py and moData.py

* moData defines the column names and collects row contents as an array

* moCSV controls file access and rate of row addition (1/min is default)

### 4.2.4 JSON Message Log

JSON messages written by server when compiled to use (off generally)

* each record is contents of moData dictionary

* by default this is turned off. 

* a Logger Client was built but not maintained during development

* File name format: modacServer_20200207_1607.json

### Configuration Files

There are a lot of configuration variables for the Proof of Concept system. These are kept in python source files.  A number of common ones are grouped into the

moKeys.py holds inline functions that return string constants for use as dictionary keys

configuration inline in hardware module support code

kiln control has a [kilnConfig.py](https://github.com/morphoptic/modac1/blob/master/kilnControl/kilnConfig.py) to hold variables shared with other code modules

## 4.3 Hardware: 

(see hardware [spreadsheet ](https://docs.google.com/spreadsheets/d/14ZYECJ_tfQRatfjn2zahfT1W3wfto0_kKzY8I5mpQlw/edit?usp=sharing)for details)

The MODAC server consists of:

* Raspberry Pi 3B+

* HAT (Daughter) boards

    * Pi-EZ Connect Terminal Breakout HAT (screw terminal daughter board)

    * Waveshare 24 bit AD/DA Converter HAT (8 AD, 2 DA) w screw terminals

        * note: the 24 bit Digital/Analog output is not supported in software

        * note: 24bit A/D is not used in latest version as a) its overkill and b) it was noisy, given long wires between kiln and MODAC

        * a previous 24Bit A/D converter board failed and had to be replaced

* I2C Connected:

    * i2c-RJ45 driver pair (run i2c signals over Cat5 cable)

    * 16 bit AD Converter (4 AD, i2c connect)

    * 4 channel k-type thermocouple amplifier

    * i2c Environment Sensor (Temp, Humidity, Pressure)

* Binary Outputs

    * 8 Channel Relay Module

    * 3 Power strips w/relay control (always on, normally on, normally off)

* Leica Disto Blue Tooth laser distance sensor

* Power Supplies:

    * 5v 10A dc power supply + screw connector bus

    * 5v 3A dc -usb for rPi

    * 12vdc power supply (output side of Relay Module)

* UI components

    * powered USB hub (low quality, missing power supply)

    * USB keyboard

    * USB mouse

    * Desktop HDMI Monitor (ok DVI with dvi-hdmi cable)

* Case: upcycled rack mount from old UPS system

* Unused Components

    * 7" touch screen

    * 1.3" OLED screen (i2c)

    * USB-Serial for Pi

    * 4 port ethernet switch)

