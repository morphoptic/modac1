#“readSteps” a json file containing steps to run
#    [
#    {"idle"},
#    {"heatTo" :{ 500}},
#    {"holdTemp": {"temp":500, "deflect": 100}},
#    {"RampDown": {"support": 1, "exhaust": 1}}
#    ]
#

import json

with open("modacSteps.json",'r') as stepFile:
    steps = json.load(stepFile)
    print("Read file: ", steps)
    print("formatted json:", json.dumps(steps, indent=4))
    with  open("out.json",'w') as outfile:
        json.dump(steps, outfile, indent=4)
