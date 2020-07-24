#BME280 MatPlotLib test
# opens a window with 3 line graphs for temp, humidity and pressure
# no fancy decorators

import math
from time import sleep
import time
import datetime
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

# our MorphOptics wrapper on the BME280 device, wraps Adafruit library, smbus2, etc
from moBME280 import moBME280


# create a figure with 3 subplots
fig = pyplot.figure()
plot_width = 100
# arrays to hold data 
times = [0]*plot_width
temps = [0]*plot_width
humid = [0]*plot_width
press = [0]*plot_width

tempPlot = fig.add_subplot(3,1,1)
tempPlot.set_title('temperature')
tempPlot.set_ylim(25,35)

humidPlot = fig.add_subplot(3,1,2)
humidPlot.set_title('humidity')
humidPlot.set_ylim(30,100)

pressPlot = fig.add_subplot(3,1,3)
pressPlot.set_title('pressure')
pressPlot.set_ylim(900,1000)

pyplot.subplots_adjust(hspace=0.6)

times = list(range(0,plot_width))
tempsLine, = tempPlot.plot(times, temps)
humidLine, = humidPlot.plot(times, humid)
pressLine, = pressPlot.plot(times, press)

#############################
bme = moBME280()
readCount = 0
def readRecordOne(count):
    global times, temps, humid, press
    bme.read()
    times.append(count) #bme.timestamp.strftime("%S%Z"))
    temps.append(bme.temperature)
    humid.append(bme.humidity)
    press.append(bme.pressure)
    #limit size of arrays
    times = times[-plot_width:]
    temps = temps[-plot_width:]
    humid = humid[-plot_width:]
    press = press[-plot_width:]
    print(count, bme)
    
def fillForSeconds(seconds=10):
    #sample for 30 sec
    for t in range (0,seconds):
        #grab the bme data and appped to data arrays
        readRecordOne(t)
        time.sleep(1)

def animate(i):
    global times, temps, humid, press
    global tempsLine, humidLine, pressLine
    readRecordOne(i)
    tempsLine.set_ydata(temps)
    humidLine.set_ydata(humid)
    pressLine.set_ydata(press)
    return tempsLine, humidLine, pressLine

print("Start main")
ani = animation.FuncAnimation(fig, animate, interval=500, blit=True)
pyplot.show()


