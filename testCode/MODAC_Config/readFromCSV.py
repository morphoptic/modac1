#“GPIO_Usage” to be a JSON Config file 
#as python object:

import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import csv
import json

#csvFilename = "modac.csv"
csvFilename = "kilnSchedule.csv"

dataArray = []
#read first from CSV
csvReader = csv.DictReader(open(csvFilename))
for row in csvReader:
    dataArray.append(row)
    print("CSV Row: ", row)
    print("Row as JSON: ",json.dumps(row))
    #print("Row as Modad_GPIO: ", mgpio)

print("------------ dataArray--------")
print("dataArray: ", dataArray)
print("------------ JSON dataArray --------")
print(json.dumps(dataArray, indent=4))

print("------------ write JSON File dataArray --------")
with open("modacdataArray.config.json",'w') as configFile:
    json.dump(dataArray, configFile, indent=4)
   
print("------------ read JSON File dataArray --------")
with open("modacdataArray.config.json",'r') as configFile:
    dataArray2 = json.load(configFile)
    print("Read: ", dataArray2)
    print("asJson: ", json.dumps(dataArray2, indent=4))

print("done")
