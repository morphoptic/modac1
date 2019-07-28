# moCommand
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers
import json

#import rest of modac
from .moKeys import *
from . import moData, moNetwork

def sendBinaryOut(binOutIdx, onOff):
    assert isinstance(binOutIdx, int)
    assert isinstance(onOff, bool)
    moNetwork.cmdBinary(binOutIdx, onOff)