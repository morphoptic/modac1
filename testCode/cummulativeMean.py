# simple example of a fast cumulative mean that doesnt require numpy, scipi or other
# keeps the cumulative_sum around, removes and subtracts oldest
# adds new value, divides
# this keeps minimum traversals of the deque/list

from collections import deque

cache = deque() # keep track of seen values
n = 10          # window size
A = xrange(100) # some dummy iterable
cum_sum = 0     # initialize cumulative sum

for t, val in enumerate(A, 1):
    cache.append(val)
    cum_sum += val
    if t < n:
        avg = cum_sum / float(t)
    else:                           # if window is saturated,
        cum_sum -= cache.popleft()  # subtract oldest value
        avg = cum_sum / float(n)

# so for a Channel that gets new value every tick

class MeanLimitedChannel:
    def __init__(self, window= 5, meanDeviation= 0.1, meanLimited = True ):
        self.cache = deque()
        self.cumulativeSum = 0.0
        self._average = 0
        self.windowSize = window
        self.count =0
        self.meanDeviation = meanDeviation
        self.meanLimited = meanLimited
        self._curvalue = 0.0

    def __str__(self):
        s = f"MeanLimitedChannel v: {self._curvalue} limited: {self.meanLimited} avg: {self._average}  def: {self.meanDeviation}"
        return s

    def addValue(self, v):
        if self.meanLimited and self.count >= self.windowSize:
            # first test if it is within meanLimited Range
            dif = abs(v - avg)
            if dif > (self._average * self.meanDeviation):
                raise ValueError("Channel value exceeds limit "+str(self))
        self.cache.append(v)
        self.cumulativeSum += v

        self.count += 1
        if self.count < self.windowSize:
            self._average = self.cumulativeSum / float (self.count)
        else:
            self.cumulativeSum -= self.cache.popleft()
            self._average = self.cumulativeSum / float (self.windowSize)
            # cap count at windowSize?

    def avg(self):
        return self._average

    def setMeanLimited(self,tf):
        if tf:
            self.meanLimited = True
        else:
            self.meanLimited = False

    def curValue(self):
        return self._curvalue






