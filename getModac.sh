#!/bin/sh
# install required modac packages
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install build-essential checkinstall
sudo apt-get install python-dev python3-dev
#sudo apt-get -y install qt-5default
#sudo apt-get -y install qtcreator
#
sudo apt-get -y install i2c-tools
sudo apt-get -y install python3-gpiozero
sudo apt-get -y install rpi.gpio
#sudo apt-get -y install python3-pyqt5
sudo apt-get -y install libffi-dev
#
sudo cp /usr/bin/pip3 /usr/bin/pip3.5
sudo python3 -m pip install --upgrade pip setuptools wheel
#sudo python3 -m pip install -U matplotlib
#sudo pip3 install pyqtgraph
sudo pip3 install spidev
sudo pip3 install smbus2
sudo pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-bme280
sudo pip3 install Rpi.bme280
#sudo pip3 install Adafruit-SSD1306
sudo pip3 install adafruit-circuitpython-ads1x15
#
# sudo pip3 install simple-crypt
#
# getting GTK3 installed
sudo apt install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
sudo pip3 install pycairo
sudo pip3 install PyGObject
sudo apt-get install glade

