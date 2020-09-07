#!/bin/sh -v
#
sudo make altinstall
#
sudo ln -s /usr/local/bin/pydoc3.7 /usr/bin/pydoc3.7
sudo ln -s /usr/local/bin/python3.7 /usr/bin/python3.7
sudo ln -s /usr/local/bin/python3.7m /usr/bin/python3.7m
sudo ln -s /usr/local/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7
sudo ln -s /usr/local/bin/pip3.7 /usr/bin/pip3.7
alias python='/usr/bin/python3.7'
alias python3='/usr/bin/python3.7'
ls /usr/bin/python*
python -V
sudo update-alternatives --config python
#
sudo python3 -m pip install --upgrade pip setuptools wheel