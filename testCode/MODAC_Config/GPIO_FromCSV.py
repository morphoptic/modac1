#“GPIO_Usage” to be a JSON Config file 
#as python object:
import csv
import json

class modacGPIO:
    pin = 0
    gpio = 'nc'
    modac = 'nc'
    waveShareUse = 'nc'
    def __init__(self, pin= 0):
        self.pin = pin
        print("Create GPIO for pin ", self.pin)

print
csvFilename = "MODAC_GPIO.csv"
mgpioList = []
gpioList = []
#read first from CSV
csvReader = csv.DictReader(open(csvFilename))
for row in csvReader:
    gpioList.append(row)
    print("CSV Row: ", row)
    mgpio = modacGPIO(row['Pin'])
    #mgpio.pin = row['Pin']
    mgpio.gpio = row['GPIO']
    mgpio.modac = row['MODAC']
    mgpio.waveShareUse = row['WaveShareUse']
    mgpioList.append(mgpio)
    print("Row as JSON: ",json.dumps(row))
    #print("Row as Modad_GPIO: ", mgpio)

print("------------ gpioList--------")
print("gpioList: ", gpioList)
print("------------ JSON gpioLIST --------")
print(json.dumps(gpioList))
#print("JSON of mgpioList: ", json.dumps(mgpioList))
modacGPIOConfig = {"modacGPIOConfig": json.dumps(gpioList)}
print("------------ modacGPIOConfig --------")
print (modacGPIOConfig)
print("------------ JSON of modacGPIOConfig --------")
print(json.dumps(modacGPIOConfig))

print("------------ write JSON File gpioList --------")
with open("modacGPIOList.config.json",'w') as configFile:
    json.dump(gpioList, configFile, indent=4)

print("------------ write JSON File modacGPIOConfig --------")
with open("modacGPIO.config.json",'w') as configFile:
    json.dump(modacGPIOConfig, configFile, indent=4)
    
print("------------ read JSON File gpioList --------")
with open("modacGPIOList.config.json",'r') as configFile:
    gpioList2 = json.load(configFile)
    print("Read: ", gpioList2)
    print("asJson: ", json.dumps(gpioList2, indent=4))

print("done")
# the GPIO List looks simplest approach
# the class requires work to (de)serialize
