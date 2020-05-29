# read and decimate modac csv
import sys
this = sys.modules[__name__]
import os
import csv
from datetime import datetime, timedelta

infilename ='temps_server.csv'
outfilename = 'temps_server_out.csv'
count = 0
outCount = 0
outfile = None
writer = None
inColumnNames = None
outColumnNames = None

timestampKey = 'timestamp'
dateKey = 'date'
timeKey = 'time'
lastTimeMin = 0
lastDateTime = None

def processLine (row):
    #print("processing line ",count, row)
    dtStr = row[timestampKey]
    dt = datetime.strptime(dtStr,"%Y-%m-%d %H:%M:%S")
    if this.lastDateTime== None :
        this.lastDateTime = dt
    elif dt.time().minute == this.lastDateTime.time().minute:
        # skip same minute
        #print("Same Minute", dt,dt.time().minute, this.lastDateTime,this.lastDateTime.time().minute)
        return
    this.lastDateTime = dt
    dateStr = datetime.strftime(dt,"%Y-%m-%d")
    timeStr = datetime.strftime(dt,"%I:%M:%S%p")
    row[dateKey]= dateStr
    row[timeKey]=timeStr
    #print("outRow:", row)
    this.writer.writerow(row)
    this.outfile.flush()
    this.outCount += 1
    pass

def doFile(filename):
    base, ext = os.path.splitext(filename)
    outfilename = base+"_out.csv"
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if this.count == 0:
                inColumnNames = reader.fieldnames
                print("Columns are ",inColumnNames)
                outColumnNames = [dateKey,timeKey] + inColumnNames
                print("out Columns are ",inColumnNames)
                this.outfile = open(outfilename, 'w', newline='')
                this.writer = csv.DictWriter(this.outfile, outColumnNames)
                this.writer.writeheader()
            #print (count, row)
            processLine(row)
            this.count = this.count+1
            #if count > 500:
            #    break
    this.outfile.close()
    this.outfile = None
    print("Read %d lines wrote %d lines"%(this.count,this.outCount))
    this.count = 0
    this.outCount = 0

doFile('modacServer_0225.csv')
