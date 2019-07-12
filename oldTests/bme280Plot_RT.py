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
plot_width = 100
# arrays to hold data 
times = [0]*plot_width
temps = [0]*plot_width
humid = [0]*plot_width
press = [0]*plot_width

#temperatureRange = list(range(0,100))
temperaturePlot = fig.add_subplot(3,1,1)
temperaturePlot.set_title('temperature')
temperaturePlot.set_ylim(10,40)
temperatureLine, = temperaturePlot.plot(times, temps)

#humidityRange = list(range(30,80))
humidityPlot = fig.add_subplot(3,1,2)
humidityPlot.set_title('humidity')
humidityPlot.set_ylim(30,80)

pressureRange = [950,1000]
pressurePlot = fig.add_subplot(3,1,3)
pressurePlot.set_title('pressure')
pressurePlot.set_ylim(pressureRange) #900,1000)

pyplot.subplots_adjust(hspace=0.6)

#############################
bme = moBME280()

def fillForSeconds(seconds=10):
    global times, temps, humid, press
    #sample for 30 sec
    for t in range (0,seconds):
        #grab the bme data and appped to data arrays
        bme.read()
        times.append(t) #bme.timestamp.strftime("%S%Z"))
        temps.append(bme.temperature)
        humid.append(bme.humidity)
        press.append(bme.pressure)
        #limit size of arrays
        times = times[-plot_width:]
        temps = temps[-plot_width:]
        humid = humid[-plot_width:]
        press = press[-plot_width:]

        print(t,bme.timestamp, bme)
        time.sleep(1)

print("Original arrays:")
print("Times ",times)
print("temps ",temps)
print("humid ",humid)
print("press ",press)

fillForSeconds()

print("Filled arrays:")
print("Times ",times)
print("temps ",temps)
print("humid ",humid)
print("press ",press)

temperaturePlot.plot(times, temps)
humidityPlot.plot(times, humid)
pressurePlot.plot(times, press)
print("ok loaded plots, now show")
pyplot.show()


