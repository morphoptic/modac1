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
#####################
# internal very specific heater states - one each plus array
lowerHeaterState = False
middleHeaterState = False
upperHeaterState = False
#heaterStateStr = ""
reportedHeaterStates = [False, False, False, False]

# fans are wired via 
fan_support = 11  # jet to support glass
fan_exhaust = 10  # heat exhaust fan

#####################
# kType thermocouples: may or may not be wired separate or combined
# three ktypes are defined over there, and reported by the kType entry in moData
# these are indices into the moData( kTypeKey ) array
# note the indices to kiln.kilnTemps is this +1 (as kilnTemps[0] is average)
kType_lower = 0
kType_middle = 1
kType_upper = 2

# for some circumstance (testing) only one kType is used for control
# this boolean controls whether kTypeLower is used or average is used
kType_avgAll = False

#####################
emergency_shutoff_temp = 800  # if kiln ever gets this hot, shutdown and vent

#####################
default_holdTemp = 500
default_targetDisplacement = 10
default_maxTime = 1000 #minutes
default_stepTime = 2 # 10

###
# this lets any watchers note end of run and reset gui, etc
endRunHoldTime = 60 # sec to wait after cool down before idle
