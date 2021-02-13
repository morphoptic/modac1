# generic common Status enum

from enum import Enum

class moStatus(Enum):
    Error = -100
    Default = 0
    Initialized = 1
    OK = 2
    Simulated = 3

class moClientStatus(Enum):
    Error = -100
    Shutdown = -1
    Default = 0
    Running = 1
    Paused = 2


