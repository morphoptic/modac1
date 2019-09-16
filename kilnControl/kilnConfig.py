# kilnConfig.py
# mapping from BinaryOut -> heaters and fans
# and ktypes used
#

# if displacement is within this of target, start cooling
distanceEpsilon = 0.001
tempertureEpsilon = 1.0

# 12v power to driver side of relays is on BO[0] (controlled power strip)
relayPower = 0  # gpio conrolled power strip

# heaters: idxs of BinaryOut pins
heater_lower = 1
heater_middle = 2
heater_upper = 3
# and an array to hold those to match ktemps/kcmds heaters
heaters = [0, heater_lower, heater_middle, heater_upper]

# fans are wired ?? as 12v? as gpio?
fan_support = 9  # jet to support glass
fan_exhaust = 10  # heat exhaust fan

#####################
# kType thermocouples: may or may not be wired separate or combined
# three ktypes are defined over there, and reported by the kType entry in moData
# these are indices into the moData( kTypeKey ) array
kType_lower = 0
kType_middle = 1
kType_upper = 2

#####################
emergency_shutoff_temp = 800  # if kiln ever gets this hot, shutdown and vent

#####################
default_holdTemp = 500
default_targetDisplacement = 10
default_maxTime = 1000 #minutes
default_stepTime = 10
