# Baumer OM-70 UDP Packet Datum
# The data fields held in a UDP packet from the OM70
# uses struct to translate from/to binary array
# holds data in a namedTuple, also available as Dictionary and JSON string
# also includes functions to create some test records
# and a main() to run some unit tests
# per the manual UDP fields are:
# uint32 (4bytes) BlockID
# uint8 (1byte) FrameType 0= singleFrame 1= first 2 = later frames
# uint8 reserved
# uint16 (2b) frame counter; type1: total count type2: current count
# uint8 Quality 0=ok 1=low 2=nosignal
# bool 1b State Switching 0= active 1= inactive
# bool 1b State Alarm 0= active 1=inactive
# 1b padding (no python var equiv required)
# float32 (4b) distance in millimeters
# float32 measurement rate
# float32 exposure reserve
# uint32 response delay seconds
# uint32 response delay microsec
# timestamp seconds
# timestamp microsec

import sys
this = sys.modules[__name__]
import struct
import random
import json
import math
from collections import namedtuple
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Constants for addressing items in dictionary or tuple
# _NAME are string names for dictionary; match names in OM70 manual
BLOCKID_NAME = "blockId"
FRAMEID_NAME = "frameid"
RESERVEDBYTE_NAME = "reservedByte"
FRAMECOUNT_NAME = "frameCount"
QUALITY_NAME = "quality"
SWITCHINGSTATE_NAME = "switchingState"
ALARMSTATE_NAME = "alarmState"
DISTANCEMM_NAME = "distanceMM"
RATE_NAME = "rate"
EXPOSURERESERVE_NAME = "exposureReserve"
DELAYSECONDS_NAME = "delaySeconds"
DELAYMICROSEC_NAME = "delayMicroSec"
TIMESTAMPSEC_NAME = "timestampSec"
TIMESTAMPMICROSEC_NAME = "timestampMicroSec"

# _IDX are index into UDP packet and thus tuple
BLOCKID_IDX = 0
FRAMEID_IDX = 1
RESERVEDBYTE_IDX = 2
FRAMECOUNT_IDX = 3
QUALITY_IDX = 4
SWITCHINGSTATE_IDX = 5
ALARMSTATE_IDX = 6
DISTANCEMM_IDX = 7
RATE_IDX = 8
EXPOSURERESERVE_IDX = 9
DELAYSECONDS_IDX = 10
DELAYMICROSEC_IDX = 11
TIMESTAMPSEC_IDX = 12
TIMESTAMPMICROSEC_IDX = 13

# memberNames for namedTuple
_memberNames = ("blockId", "frameId", "reservedByte", "frameCount", "quality",
               "switchingState", "alarmState", "distanceMM", "rate", "exposureReserve",
               "delaySeconds", "delayMicroSec", "timestampSec", "timestampMicroSec")
_memberDefaults = (0, 0, 0, 0, 2, True, True, 0.0, 0.0, 0.0, 0, 0, 0, 0)
# format is used by struct in compiled format to (un)pack binary
# to get it right, slowly add characters and test, as error msgs are not helpful
# single byte values dont need bytearray
_structFormat = '<I B b h b ? ? x fff iiii'
# common struct for all class members to use
_om70struct = struct.Struct(_structFormat)

_OM70DatumT = namedtuple('OM70Datum', [*_memberNames], defaults=[*_memberDefaults])

def byteSize():
    return struct.calcsize(_structFormat)

class OM70Datum(_OM70DatumT):
    """ Baumer OM70 UDP Packet Datum - packing unpacking, test and JSON important bits  """

    def distancemm(self):
        return self[DISTANCEMM_IDX]

    def asJson(self):
        s = json.dumps(self.asDict())
        return s
    
    def asJsonIndent(self):
        s = json.dumps(self.asDict(), indent=4)
        return s

    def asDict(self):
        #d = datum.asDict()
        #TODO: integrate modoc timestamp into dict
        return self._asdict()

    def equals(self,other):
        if not self[BLOCKID_IDX] == other[BLOCKID_IDX]:
            print("blockId not equal ",self[BLOCKID_IDX],other[BLOCKID_IDX])
            return False
        if not self[FRAMEID_IDX] == other[FRAMEID_IDX]:
            print("frameId not equal")
            return False
        if not self[RESERVEDBYTE_IDX] == other[RESERVEDBYTE_IDX]:
            print("reservedByte not equal")
            return False
        if not self[FRAMECOUNT_IDX] == other[FRAMECOUNT_IDX]:
            print("frameCount not equal")
            return False
        if not self[QUALITY_IDX] == other[QUALITY_IDX]:
            print("quality not equal")
            return False
        if not self[SWITCHINGSTATE_IDX] == other[SWITCHINGSTATE_IDX]:
            print("switchingState not equal")
            return False
        if not self[ALARMSTATE_IDX] == other[ALARMSTATE_IDX]:
            print("alarmState not equal")
            return False
        if not self[DISTANCEMM_IDX] == other[DISTANCEMM_IDX]:
            if math.isclose(self[DISTANCEMM_IDX], other[DISTANCEMM_IDX], rel_tol=1e-5):
                print("distance close ",self[DISTANCEMM_IDX], other[DISTANCEMM_IDX])
            else:
                print("distance not equal")
                return False
        if not self[RATE_IDX] == other[RATE_IDX]:
            if math.isclose(self[RATE_IDX], other[RATE_IDX], rel_tol=1e-5):
                print("rate close ", self[RATE_IDX], other[RATE_IDX])
            else:
                print("rate not equal")
                return False
        if not self[EXPOSURERESERVE_IDX]== other[EXPOSURERESERVE_IDX]:
            if math.isclose(self[EXPOSURERESERVE_IDX], other[EXPOSURERESERVE_IDX], rel_tol=1e-5):
                print("exposureReserve close ", self[EXPOSURERESERVE_IDX], other[EXPOSURERESERVE_IDX])
            else:
                print("exposureReserve not close or equal")
                return False
        if not self[DELAYSECONDS_IDX] == other[DELAYSECONDS_IDX]:
            print("delaySeconds not equal")
            return False
        if not self[DELAYMICROSEC_IDX] == other[DELAYMICROSEC_IDX]:
            print("delayMicroSec not equal")
            return False
        if not self[TIMESTAMPSEC_IDX] == other[TIMESTAMPSEC_IDX]:
            print("timestampSec not equal")
            return False
        if not self[TIMESTAMPMICROSEC_IDX] == other[TIMESTAMPMICROSEC_IDX]:
            print("timestampMicroSec not equal")
            return False
        return True

    def toBuffer(self, buffer):
        """pack the OM70 namedTuple into a buffer for UDP send"""
        _om70struct.pack_into(buffer, 0, *self)

def fromBuffer(buffer):
    """Treat Buffer as a raw UDP packet from OM70, unpack and create OM70Datum namedTuple"""
    nt = OM70Datum._make(_om70struct.unpack(buffer))
    #print("fromBuffer tuple: ", nt)
    return nt

def makeRandomOm70():
    """test method to create random values in OM70 namedTuple"""
    t = (random.randrange(0,99), random.randrange(0,128), random.randrange(0,128),
         random.randrange(0,10), random.randrange(0,2), 0, 1, random.random() * 10.0,
         2.0, 0.0, 1, 5, random.randrange(0,100), random.randrange(0,1000))
    return OM70Datum._make(t)

if __name__ == "__main__":
    print("test OM70Datum PackUnpack  begin")
    b1 = OM70Datum()
    b2 = OM70Datum()
    print("b1:",b1)
    print("b2:",b2)
    if b1.equals(b2):
        print("B1=B2 defaults are equal")
    else:
        print("B1 not = B2 defaults not equal")
    b2 = makeRandomOm70()
    b1= makeRandomOm70()
    print("b1 Test:",b1)
    print("b2 Random:",b2)
    if b1.equals(b2):
        print("B1=B2 randoms are but should not be equal" )
    else:
        print("B1 not = B2 randoms not equal")
    print("b1 json:", b1.asJson())
    print("b2 json:", b2.asJson())
    buffer = bytearray(byteSize())
    print("Now try converting to/from buffer")
    b1.toBuffer(buffer)
    print("buffer:", buffer)
    b2 = fromBuffer(buffer)
    print("b1 to   buffer", b1)
    print("b2 from Buffer", b2)
    if b1.equals(b2):
        print("B1=B2 Conversion to/from buffer works")
    else:
        print("B1 not = B2 Conversion to/from buffer Fails")
    print("b2 from buffer as json", b2.asJsonIndent())
    print("testDatumPackUnpack  end")
