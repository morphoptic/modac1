# ADS1115 adafruit test
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

# create a figure with 3 subplots
fig = pyplot.figure()
plot_width = 100
# arrays to hold data 
times = [0]*plot_width
raw = [0]*plot_width
volts = [0]*plot_width

rawPlot = fig.add_subplot(2,1,1)
rawPlot.set_title('raw ads1115 chan 1')
rawPlot.set_ylim(-18,32752)

voltPlot = fig.add_subplot(2,1,2)
voltPlot.set_title('volts ads1115 chan 1')
voltPlot.set_ylim(0,5)

pyplot.subplots_adjust(hspace=0.6)
times = list(range(0,plot_width))
rawLine, = rawPlot.plot(times,raw)
voltLine, = voltPlot.plot(times,volts)

readCount = 0
def readRecordOne(count):
    global times, raw, volts
    times.append(count) 
    raw.append(chan.value)
    volts.append( chan.voltage)
    #limit size of arrays
    times = times[-plot_width:]
    raw = raw[-plot_width:]
    volts = volts[-plot_width:]
    print(count, chan.value, chan.voltage)
    
def animate(i):
    global times, raw, volts
    global rawLine, voltLine
    readRecordOne(i)
    rawLine.set_ydata(raw)
    voltLine.set_ydata(volts)
    return rawLine, voltLine

print("Start main")
ani = animation.FuncAnimation(fig, animate, interval=500, blit=True)
pyplot.show()

