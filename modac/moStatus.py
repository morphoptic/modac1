# generic common Status enum

from enum import Enum

class moStatus(Enum):
    Error = -100
    Default = 0
    Initialized = 1
    OK = 2
    Simulated = 3


