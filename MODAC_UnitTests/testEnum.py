from enum import Enum
class moDataStatus(Enum):
    Error = -2
    Shutdown = -1
    Startup = 0
    Initialized = 1
    Running = 2
    
stat1 = moDataStatus.Initialized
print(stat1)
stat1Name = stat1.name
print(stat1Name)
stat2 = moDataStatus[stat1.name]
print(stat2)

