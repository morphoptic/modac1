# modac_ktype
import logging, logging.handlers

from thermocouples_reference import thermocouples

__typeK = thermocouples['K']

def mVToC(mV,tempRef=0):
    return __typeK.inverse_CmV(mV, Tref=tempRef)
 