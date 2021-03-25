# filters values against rapid change in moving average (derivative of)
# uses fast moving average (by retaining window values and adjusting sum)
# if addValue exceeds deltaLimit, value is rejected (throws ValueError?)
#
# caveat collections.deque is deprecated and removed soon
# simple example of a fast cumulative mean that doesnt require numpy, scipi or other
# keeps the cumulative_sum around, removes and subtracts oldest
# adds new value, divides
# this keeps minimum traversals of the deque/list
###########
import logging, logging.handlers, traceback
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

########
from collections import deque

class FilteredChannel:
    def __init__(self, window=5, slopelimit=5001.0, filtered=True):
        """
        @type window: int
        @type slopelimit: float
        @type filtered: bool
        """
        self.cache = deque()
        #TODO: movAvg and movSlope dont need queue?
        self._curvalue = 0.0
        self.cumulativeSum = 0.0
        self._average = 0
        self.windowSize = window
        self.count = 0
        self.slope = 0
        self.slopeLimit = slopelimit
        self.filtered = filtered
        print("Created Filtered Channel ", self)

    def __str__(self):
        s = f"FilteredChannel v:{self._curvalue} filtered:{self.filtered} maxSlope:{self.slopeLimit} avg:{self._average} {self.cache} slope:{self.slope}"
        return s

    def addValue(self, v):
        val = float(v)

        # test to reject value if > mov_avg by Deviations
        if self.filtered and self.count >= self.windowSize:
            # first test if it is within meanLimited Range
            dv = abs(val - self._average)
            if dv > self.slopeLimit:
                msg = f"Channel value:{val} dv:{dv} exceeds limit {self}"
                raise ValueError(msg)

        # passed test, add to cache and update average
        self.cache.append(val)
        self.cumulativeSum += val
        self._curvalue = val

        self.count += 1
        prevAvg = self._average
        if self.count <= self.windowSize:
            self._average = self.cumulativeSum / float (self.count)
        else:
            self.cumulativeSum -= self.cache.popleft()
            self._average = self.cumulativeSum / float (self.windowSize)
            #cap count at windowSize?
            self.count = self.windowSize

        self.slope = self._average - prevAvg

    def avg(self):
        return self._average

    def setMeanLimited(self,tf):
        if tf:
            self.filtered = True
        else:
            self.filtered = False

    def setSlopeLimit(self, deviation):
        self.slopeLimit = float(deviation)

    def curValue(self):
        return self._curvalue

    def reset(self):
        self._curvalue = 0.0
        self.cumulativeSum = 0.0
        self._average = 0
        self.count = 0
        self.slope = 0
        self.cache.clear()

if __name__ == '__main__':
    # initialize 4 channels, first 3 are limited
    chans = []
    numChan = 3
    print("Setup Channels")
    for i in range(numChan):
        print("Create channel ",i)
        if i < numChan-1:
            chan = FilteredChannel()
        else:
            print("unlimited Channel")
            chan = FilteredChannel(filtered=False)
        chans.append(chan)
        print("Channel Created: ", chan)
        # setup some initial values
        #print("Add some values")
        for v in range(6):
            try:
                chans[i].addValue(float(v))
            except ValueError as e:
                log.error("Error on chan "+str(chan),exc_info=True)
                #raise e

    for c in chans:
        c.setSlopeLimit(2.0)
        print(c)
    print("Initialization complete, run tests")
    ## Now run some tests
    for step in range(6,100):
        for c in chans:
            try:
                c.addValue(float(step))
                print(c)
            except ValueError as ve:
                log.error("Error on chan " + str(c), exc_info=True)
                raise(ve)


# cache = deque() # keep track of seen values
# n = 10          # window size
# A = xrange(100) # some dummy iterable
# cum_sum = 0     # initialize cumulative sum
#
# for t, val in enumerate(A, 1):
#     cache.append(val)
#     cum_sum += val
#     if t < n:
#         avg = cum_sum / float(t)
#     else:                           # if window is saturated,
#         cum_sum -= cache.popleft()  # subtract oldest value
#         avg = cum_sum / float(n)





