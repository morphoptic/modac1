#recalibrateKType

from thermocouples_reference import thermocouples
import numpy as np

__typeK = thermocouples['K']

def mVToC(mV,tempRef=0):
    return __typeK.inverse_CmV(mV, Tref=tempRef)

def CtomV(c, tempRef=0):
    return __typeK.emf_mVC(c, Tref=tempRef)

# ran some tests and get ice water temp at 0.134V avg
# which is 134mV so working that back
ice134 = mVToC(0.134,tempRef=0)#25.4)
print ("ice134 =",ice134)
# warm water measured w thermometer = 0.298
warm38 =mVToC(0.298,tempRef=0)
print ("warm38 =",warm38)
# room temp measured w enviro (25.4)  = 0.2327
room254 =mVToC(0.2327,tempRef=0)
print ("room254 =",room254)

# really crude T=(Vout-1.25)/0.005
def crude(v):
    return (v)/0.005
iceCrude = crude(0.134)
warmCrude = crude(0.298)
roomCrude = crude(0.2327)
print ("iceCrude =",iceCrude)
print ("warmCrude =",warmCrude)
print ("roomCrude =",roomCrude)











