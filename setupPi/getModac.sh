#!/bin/sh
# install required modac packages
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install build-essential checkinstall
sudo apt-get install python-dev python3-dev
#
sudo apt-get -y install i2c-tools
sudo apt-get -y install python3-gpiozero
sudo apt-get -y install rpi.gpio
#sudo apt-get -y install python3-pyqt5
sudo apt-get -y install libffi-dev
#
sudo cp /usr/bin/pip3 /usr/bin/pip3.5
sudo python3 -m pip install --upgrade pip setuptools wheel
#
# need latest numpy, scipy etc
sudo apt install libatlas3-base
sudo apt-get -y install python-numpy python-scipy python-matplotlib
# why? do we really need both installs for these 3?
sudo python3 -m pip install -U matplotlib scipy numpy
#
# hardware support
sudo pip3 install --upgrade spidev
sudo pip3 install --upgrade smbus2
sudo pip3 install --upgrade Rpi.bme280
#
#  ADAfruit for oled and other devices
#  not using them mid-july so leave off
#sudo pip3 install adafruit-blinka
#sudo pip3 install adafruit-circuitpython-bme280
#sudo pip3 install Adafruit-SSD1306
#sudo pip3 install adafruit-circuitpython-ads1x15
#
# getting GTK3 installed
sudo apt install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
sudo pip3 install --upgrade pycairo
sudo pip3 install --upgrade PyGObject
sudo apt-get -y install glade
#
# experiment with QT and pyQTGraph
#sudo apt-get -y install qt-5default
#sudo apt-get -y install qtcreator
#sudo pip3 install pyqtgraph
#
sudo pip3 install thermocouples_reference scipy
#
#sudo python3 -m pip install -U trio
sudo pip3 install --upgrade pexpect
sudo pip3 install --upgrade trio
sudo pip3 install --upgrade pylint
sudo pip3 install --upgrade pynng
sudo pip3 install --upgrade pytest
#
sudo apt-get install dosfstools
sudo apt-get install hfsutils hfsprogs hfsutils
#
sudo pip3 install --upgrade zeroconf

