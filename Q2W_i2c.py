#!/usr/bin/python3

import quick2wire.i2c as i2c
#isdale june2019 trying to get it working

# ===========================================================================
# Quick2Wire_I2C functions
# ===========================================================================


def Q2WreverseByteOrder(data):
    "Reverses the byte order of an int (16-bit) or long (32-bit) value"
    # Courtesy Vishal Sapre
    byteCount = len(hex(data)[2:].replace('L','')[::2])
    val       = 0
    for i in range(byteCount):
        val    = (val << 8) | (data & 0xff)
        data >>= 8
    return val

def Q2WerrMsg(address,message = "Check your I2C address"):
    print ("Error accessing 0x%02X: %s" % (address,message))
    return -1

def Q2Wwrite8(address, reg, value, debug = False):
    "Writes an 8-bit value to the specified register/address"
    try:
        with i2c.I2CMaster() as bus:
            bus.transaction(
                i2c.writing_bytes(address, reg, value))
        if debug:
            print ("Q2W_I2C: Device 0x%02x wrote 0x%02X to register 0x%02X" % (address,value, reg))
    except IOError as err:
        message = "Check your I2C address"
        return Q2WerrMsg(address,message)

def Q2Wwrite16(address, reg, value, debug = False):
    "Writes a 16-bit value to the specified register/address pair"
    if (value > 0xffff):
        return Q2WerrMsg(address,"Value exceeds 16 bits")
    lsb = (value & 0x00ff)  # strip off the upper byte
    msb = value >> 8 
    try:
        with i2c.I2CMaster() as bus:
            bus.transaction(
                i2c.writing_bytes(address,bytes([reg,msb,lsb])))
        if debug:
            print ("Q2W_I2C: Device 0x%02x wrote 0x%02X to register pair 0x%02X,0x%02X" %
            (address,value, reg, reg+1))
    except IOError as err:
        return Q2WerrMsg(address)

def Q2WwriteList(address, reg, byte_seq,debug = False):
    '''Writes an sequence of bytes (a list of bytes) using I2C format.
       byte_seq = bytes(byte_seq) '''    
    try:
        if debug:
            print ("Q2W_I2C: Device 0x%02x writing list to register 0x%02X:" % (address,reg))
            print (byte_seq)
        byte_seq.prepend(reg)
        with i2c.I2CMaster() as bus:
            bus.transaction(
                i2c.writing_bytes(address, byte_seq))
    except IOError as err:
        return Q2WerrMsg(address)

def Q2WreadList(address, reg, length,debug = False):
    "Read a list of bytes from the I2C device"
    # results=[]
    try:
        with i2c.I2CMaster() as bus:
            results = bus.transaction(
                i2c.writing_bytes(address,reg),
                i2c.reading(address,length))[0]
        if debug:
            print ("Q2W_I2C: Device 0x%02X returned the following from reg 0x%02X" %
             (address, reg))
            print (results)
        return results
    except IOError as err:
      return Q2WerrMsg(address)

def Q2WreadListNoReg(address, length, debug = False):
    '''Read a list of bytes from the I2C device without designating a register'''
    # results=[]
    try:
        with i2c.I2CMaster() as bus:
            results = bus.transaction(
                i2c.reading(address,length))[0]
        if debug:
            print ("Q2W_I2C: Device 0x%02X returned the following:" % (address))
            print (results)
        return results
    except IOError as err:
      return Q2WerrMsg(address)

def Q2WreadU8(address, reg, debug = False):
    "Read an unsigned byte from the I2C device"
    try:
        with i2c.I2CMaster() as bus:
            result = bus.transaction(
                i2c.writing_bytes(address, reg),
                i2c.reading(address, 1))[0][0]
        if debug:
            print ("Q2W_I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" %
                (address, result & 0xFF, reg))
        return result
    except IOError as err:
      return Q2WerrMsg(address)

def Q2WreadS8(address, reg, debug = False):
    "Reads a signed byte from the I2C device"
    try:
        with i2c.I2CMaster() as bus:
            result = bus.transaction(
                i2c.writing_bytes(address, reg),
                i2c.reading(address, 1))[0][0]
        if result > 127: result -= 256
        if debug:
            print ("Q2W_I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" %
            (address, result & 0xFF, reg))
        return result
    except IOError as err:
      return Q2WerrMsg(address)

def Q2WreadU16(address, reg, debug = False):
    "Reads an unsigned 16-bit value from the I2C device"
    try:
        with i2c.I2CMaster() as bus:
            msb,lsb = bus.transaction(
                i2c.writing_bytes(address, reg),
                i2c.reading(address, 2))[0]
            result =  (msb << 8) + lsb
        if debug:
            print ("Q2W_I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" %
             (address, result & 0xFFFF, reg))
        return result
    except IOError as err:
      return Q2WerrMsg(address)

def Q2WreadS16(address, reg,debug = False):
    "Reads a signed 16-bit value from the I2C device"
    try:
        with i2c.I2CMaster() as bus:
            msb,lsb = bus.transaction(
                i2c.writing_bytes(address, reg),
                i2c.reading(address, 2))[0]
            result =  (msb << 8) + lsb
        if result > 32767: result -= 65536
        if debug:
            print ("Q2W_I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" %
             (address, result & 0xFFFF, reg))
        return result
    except IOError as err:
      return Q2WerrMsg(address)


if __name__ == '__main__':
    try:
        Q2WreadU8(address=0x76,reg=0, debug = True)
        print ("Default I2C bus is accessible")
    except:
        print ("Error accessing default I2C bus")
    print ("after try")
    Q2WreadU8(address=0x76,reg=0, debug = True)
    print("done read")
    