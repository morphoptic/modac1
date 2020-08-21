#!/bin/sh
# 19Aug on raspianBuster OS
#sudo
# install required modac packages
sudo apt-get update
sudo apt-get upgrade
#sudo apt-get -y install build-essential checkinstall
sudo apt-get install build-essential checkinstall libpq-dev libssl-dev openssl libffi-dev zlib1g-dev
#
#
sudo apt-get install python-dev python3-dev
#
sudo apt-get install i2c-tools
sudo apt-get install python3-gpiozero
sudo apt-get install rpi.gpio
sudo apt-get install libffi-dev
sudo apt-get install exfat-fuse
#
#sudo python3 -m pip3 install --upgrade pip setuptools wheel
sudo pip3 install --upgrade pip setuptools wheel
#
sudo ln -s /usr/include/python3.7m /usr/local/include/python3.7m
#
#

## up to here new 14Aug Raspberry Pi OS has not needed much if anything
#
# need latest numpy, scipy etc
sudo apt install gfortran
sudo apt install libatlas3-base
#sudo apt install --upgrade libatlas3-base-dev
sudo apt-get -y install python-numpy python-scipy python-matplotlib

# why? do we really need both installs for these 3?
# maybe not- 14Aug this blows up with mkl_rt not found
#sudo python3 -m pip install -U matplotlib scipy numpy
sudo pip3 install --upgrade matplotlib
sudo pip3 install --upgrade numpy
#sudo pip3 install --upgrade scipy # blows up on mkl_rt not found

#
# hardware support
sudo pip3 install --upgrade spidev # error- 3.4 installed w distutils
sudo pip3 install --upgrade smbus2
sudo pip3 install --upgrade Rpi.bme280
#
#  ADAfruit for oled and other devices
#  not using them mid-july so leave off
#sudo pip3 install adafruit-blinka
#sudo pip3 install adafruit-circuitpython-bme280
#sudo pip3 install Adafruit-SSD1306
sudo pip3 install adafruit-circuitpython-ads1x15
#
# getting GTK3 installed
sudo apt install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
sudo pip3 install --upgrade pycairo
sudo pip3 install --upgrade PyGObject
sudo apt-get -y install glade
#
sudo pip3 install thermocouples_reference 
#
#sudo python3 -m pip install -U trio
sudo pip3 install --upgrade pexpect
sudo pip3 install --upgrade trio
#sudo pip3 install --upgrade pylint # fails on Buster
###
# 18Aug testing
sudo pip3 install ifaddr
# pynng requires cmake
sudo pip3 install cmake
sudo pip3 install --upgrade pynng
sudo pip3 install --upgrade pytest
#
sudo apt-get install dosfstools
sudo apt-get install hfsutils hfsprogs hfsutils
#cd /s
sudo pip3 install singleton_decorator
#
sudo apt autoremove
# need JDK to run pyCharm
sudo apt-get install -y openjdk-11-jdk
