#!/bin/sh -v
sudo python3 -m pip install --upgrade pip setuptools wheel
#
# need latest numpy, scipy etc
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
sudo pip3 install thermocouples_reference scipy
#
#sudo python3 -m pip install -U trio
sudo pip3 install --upgrade pexpect
sudo pip3 install --upgrade trio
sudo pip3 install --upgrade pylint
sudo pip3 install --upgrade pynng
sudo pip3 install --upgrade pytest
#
sudo pip3 install singleton_decorator
#
sudo apt autoremove

