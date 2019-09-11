# kilnConfig.py
# mapping from BinaryOut -> heaters and fans
# and ktypes used
#
# 12v power to driver side of relays is on BO[0] (controlled power strip)
relayPower = 0  # gpio conrolled power strip

# heaters: may or may not be wired separate or combined
heater_combined = 4
heater_lower = 1
heater_middle = 2
heater_upper = 3
heaters = (heater_lower, heater_middle, heater_upper)

# fans are wired ?? as 12v? as gpio?
fan_support = 5  # jet to support glass
fan_exhaust = 6  # heat exhaust fan

#####################
# kType thermocouples: may or may not be wired separate or combined
# kType_combined = 4 # all wired to single
# note these are NOT the ad24 connections; see ktypes.py for that
# moData.numKTypes = 4 
# kType kTypeIdx[] gives ad24 indices, len is used to create values in this
# as of Sept11 2019, [4 5 6 7] = NC, lower, middle, upper
# so lower = 1 here
kType_lower = 1
kType_middle = 2
kType_upper = 3
kiln_ktypes = [kType_lower, kType_middle, kType_upper] #indices of moData.ktype thermocouples to monitor
