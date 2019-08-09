# modac Kiln Controller, built on generic modac data acq & control
#
#  this is based on Oven code found in several github projects.
#  not sure which is the originator but these all seem to share very similar code
#     https://github.com/apollo-ng/picoReflow
#     https://github.com/jbruce12000/kiln-controller
# crude hack converting Profile -> Schedule
# csv reader logs up nice dictionary, then we turn it back into array
print("loading kiln.schedule")

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def keyForKilnTime(): "time"
def keyForKilnTemperature(): "temperature"

class Schedule:
    # others called this the Profile
    # it holds the time/temperature target schedule for kiln control
    # basically an ordered collection (list) of deltaTime and target temperature 
    # picoReflow et al use a json file for storage
    # we may use that but also use CSV file for easier editing
    timeTargetTempArray = []
    data = []

    def __init__(self, csvFile=None):
        if  csvFile == None:
            log.info("No csvFile used to init kilnSchedule")
        else:
            self.loadFromCSV(csvFile)
        print("created Schedule: ",self.data)
            
    def loadFromCSV(self, filename="testSchedule.csv"):
        import csv
        log.debug("loadFromCSV: "+filename)
        self.name = filename
        dataArray = []
        try:
            csvReader = csv.DictReader(open(filename))
            for row in csvReader:
                dataArray.append(row)
        except:
            # handle exceptions and throw em up chain
            log.error("Exception happened reading csv", exc_info=True)
            log.exception("reading csv")
            pass
        # csv file was read, do data checks here
        # it should be array of dictionaries with at least two entries each
        # there should be two columns named "time" and "temperature"
        # which would come from first row header
        # but for now we trust it is correct
        if self.verifyArray(dataArray):
            self.timeTargetTempArray = dataArray
        else:
            log.error("CSV file is not proper format: "+filename)
        for e in self.timeTargetTempArray:
            a = [ float(e["time"]), float(e["temperature"])]
            self.data.append(a)
        log.debug("Schedule dict:"+ str(self.timeTargetTempArray))
        log.debug("Schedule data:"+str(self.data))

    def verifyArray(self, dataArray):
        # also convert time strings to decimal seconds
        return True
    
    def get_duration(self):
        return max([t for (t, x) in self.data])

    def get_surrounding_points(self, time):
        if time > self.get_duration():
            return (None, None)

        prev_point = None
        next_point = None

        for i in range(len(self.data)):
            if time < self.data[i][0]:
                prev_point = self.data[i-1]
                next_point = self.data[i]
                break

        return (prev_point, next_point)

    def is_rising(self, time):
        (prev_point, next_point) = self.get_surrounding_points(time)
        if prev_point and next_point:
            return prev_point[1] < next_point[1]
        else:
            return False

    def get_target_temperature(self, time):
        if time > self.get_duration():
            return 0
        temp = 0
        (prev_point, next_point) = self.get_surrounding_points(time)
        if prev_point == None or next_point == None:
            log.error("no points surrounding time "+str(time))
        else:
            incl = float(next_point[1] - prev_point[1]) / float(next_point[0] - prev_point[0])
            temp = prev_point[1] + (time - prev_point[0]) * incl
        return temp
  
# main for testing
if __name__ == "__main__":
    s = this.Schedule("testSchedule.csv")
    print("Duration: "+ str(s.get_duration()))
    print("is_rising" + str(s.is_rising(100)))
    print("temp at 100: " + str(s.get_target_temperature(100)))

