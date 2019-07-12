#BME280 MatPlotLib test
import math
from time import sleep
import time
import datetime
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

from moBME280 import moBME280

# create a figure with 3 subplots
fig = pyplot.figure()

temperaturePlot = fig.add_subplot(3,1,1)
humidityPlot = fig.add_subplot(3,1,2)
pressurePlot = fig.add_subplot(3,1,3)
temperaturePlot.set_title('temperature')
humidityPlot.set_title('humidity')
pressurePlot.set_title('pressure')

pyplot.subplots_adjust(hspace=0.6)

#simple routine to test the plots
def plotSinCos():
    x_sine = [i/5.0 for i in range (0,50)]
    y1s = [math.sin(x) for x in x_sine]
    y2s = [math.cos(x) for x in x_sine]
    y3s = [math.fabs(x) for x in x_sine]

    temperaturePlot.plot(x_sine, y1s)
    humidityPlot.plot(x_sine, y2s)
    pressurePlot.plot(x_sine, y3s)
    pyplot.show()

print("Setup done read 30sec data")
#plotSinCos()

bme = moBME280()

times = []
temps = []
humid = []
press = []

#sample for 30 sec
for t in range (0,30):
    bme.read()
    times.append(bme.timestamp.strftime("%S%Z"))
    temps.append(bme.temperature)
    humid.append(bme.humidity)
    press.append(bme.pressure)
    print(t,bme.timestamp, bme)
    time.sleep(1)

print("Loaded arrays:")
print(times)
print(temps)
print(humid)
print(press)

temperaturePlot.plot(times, temps)
humidityPlot.plot(times, humid)
pressurePlot.plot(times, press)
print("ok loaded plots, now show")
pyplot.show()


