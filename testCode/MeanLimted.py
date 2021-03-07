# simple example of a fast cumulative mean that doesnt require numpy, scipi or other
# keeps the cumulative_sum around, removes and subtracts oldest
# adds new value, divides
# this keeps minimum traversals of the deque/list
# use of Mean is optional, size of window and deviation allowed can be set
# meanDeviation is a float
# window is an integer
###########
import logging, logging.handlers, traceback
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

########
from collections import deque

class MeanLimitedChannel:
    def __init__(self, window= 5, deviation= 3.0, limited = True):
        """
        @type window: int
        @type deviation: float
        @type limited: bool
        """
        self.cache = deque()
        self.movAvg = deque()
        self.movSlope = deque()
        self.cumulativeSum = 0.0
        self._average = 0
        self.windowSize = window
        self.count =0
        self.meanDeviation = deviation
        self.meanLimited = limited
        self._curvalue = 0.0

    def __str__(self):
        s = f"MeanLimitedChannel v:{self._curvalue} limited:{self.meanLimited} dev:{self.meanDeviation} avg:{self._average} {self.cache} ma:{self.movAvg} ms:{self.movSlope}"
        return s

    def addValue(self, v):
        val= float(v)
        # test to reject value if > mov_avg by Deviations
        if self.meanLimited and self.count >= self.windowSize:
            # first test if it is within meanLimited Range
            dif = abs(val - self._average)
            if dif > (self._average * self.meanDeviation):
                raise ValueError(f"Channel value {val} exceeds limit {self}")

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

        self.movAvg.append(self._average)
        self.movSlope.append(self._average - prevAvg)
        if len(self.movAvg) > self.windowSize:
            self.movAvg.popleft()
            self.movSlope.popleft()

    def avg(self):
        return self._average

    def setMeanLimited(self,tf):
        if tf:
            self.meanLimited = True
        else:
            self.meanLimited = False
    def setMeanDeviation(self, deviation):
        self.meanDeviation = float(deviation)

    def curValue(self):
        return self._curvalue

if __name__ == '__main__':
    # initialize 4 channels, first 3 are limited
    chans = []
    numChan = 3
    print("Setup Channels")
    for i in range(numChan):
        print("Create channel ",i)
        if i < numChan-1:
            chan = MeanLimitedChannel()
        else:
            print("unlimited Channel")
            chan = MeanLimitedChannel(limited=False)
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
        c.setMeanDeviation(2.0)
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





