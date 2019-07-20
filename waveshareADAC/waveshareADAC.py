# their header:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

import spidev
import RPi.GPIO as GPIO
import time
import logging

# waveshare AD DA converter config support
# from https://github.com/waveshare/High-Precision-AD-DA-Board
#

class Config:
    # Pin definition
    RST_PIN         = 18
    CS_PIN          = 22
    CS_DAC_PIN      = 23
    DRDY_PIN        = 17

    # SPI device, bus = 0, device = 0
    SPI = spidev.SpiDev(0, 0)

    def __init__(self):
        logging.debug("config waveshareADAC")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.CS_DAC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        #GPIO.setup(DRDY_PIN, GPIO.IN)
        GPIO.setup(self.DRDY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.SPI.max_speed_hz = 20000
        self.SPI.mode = 0b01
        #return 0;
    
    def digital_write(self,pin, value):
        GPIO.output(pin, value)

    def digital_read(self,pin):
        return GPIO.input(self.DRDY_PIN)

    def delay_ms(self,delaytime):
        time.sleep(delaytime // 1000.0)

    def spi_writebyte(self,data):
        self.SPI.writebytes(data)
        
    def spi_readbytes(self,reg):
        return self.SPI.readbytes(reg)
    
config = Config()

### END OF config ###
#################################
#begin ADS1256

class ADS1256:
    ScanMode = 0

    # gain channel
    ADS1256_GAIN_E = {'ADS1256_GAIN_1' : 0, # GAIN   1
                      'ADS1256_GAIN_2' : 1, # GAIN   2
                      'ADS1256_GAIN_4' : 2, # GAIN   4
                      'ADS1256_GAIN_8' : 3, # GAIN   8
                      'ADS1256_GAIN_16' : 4,# GAIN  16
                      'ADS1256_GAIN_32' : 5,# GAIN  32
                      'ADS1256_GAIN_64' : 6,# GAIN  64
                     }

    # data rate
    ADS1256_DRATE_E = {'ADS1256_30000SPS' : 0xF0, # reset the default values
                       'ADS1256_15000SPS' : 0xE0,
                       'ADS1256_7500SPS' : 0xD0,
                       'ADS1256_3750SPS' : 0xC0,
                       'ADS1256_2000SPS' : 0xB0,
                       'ADS1256_1000SPS' : 0xA1,
                       'ADS1256_500SPS' : 0x92,
                       'ADS1256_100SPS' : 0x82,
                       'ADS1256_60SPS' : 0x72,
                       'ADS1256_50SPS' : 0x63,
                       'ADS1256_30SPS' : 0x53,
                       'ADS1256_25SPS' : 0x43,
                       'ADS1256_15SPS' : 0x33,
                       'ADS1256_10SPS' : 0x20,
                       'ADS1256_5SPS' : 0x13,
                       'ADS1256_2d5SPS' : 0x03
                      }

    # registration definition
    REG_E = {'REG_STATUS' : 0,  # x1H
             'REG_MUX' : 1,     # 01H
             'REG_ADCON' : 2,   # 20H
             'REG_DRATE' : 3,   # F0H
             'REG_IO' : 4,      # E0H
             'REG_OFC0' : 5,    # xxH
             'REG_OFC1' : 6,    # xxH
             'REG_OFC2' : 7,    # xxH
             'REG_FSC0' : 8,    # xxH
             'REG_FSC1' : 9,    # xxH
             'REG_FSC2' : 10,   # xxH
            }

    # command definition
    CMD = {'CMD_WAKEUP' : 0x00,     # Completes SYNC and Exits Standby Mode 0000  0000 (00h)
           'CMD_RDATA' : 0x01,      # Read Data 0000  0001 (01h)
           'CMD_RDATAC' : 0x03,     # Read Data Continuously 0000   0011 (03h)
           'CMD_SDATAC' : 0x0F,     # Stop Read Data Continuously 0000   1111 (0Fh)
           'CMD_RREG' : 0x10,       # Read from REG rrr 0001 rrrr (1xh)
           'CMD_WREG' : 0x50,       # Write to REG rrr 0101 rrrr (5xh)
           'CMD_SELFCAL' : 0xF0,    # Offset and Gain Self-Calibration 1111    0000 (F0h)
           'CMD_SELFOCAL' : 0xF1,   # Offset Self-Calibration 1111    0001 (F1h)
           'CMD_SELFGCAL' : 0xF2,   # Gain Self-Calibration 1111    0010 (F2h)
           'CMD_SYSOCAL' : 0xF3,    # System Offset Calibration 1111   0011 (F3h)
           'CMD_SYSGCAL' : 0xF4,    # System Gain Calibration 1111    0100 (F4h)
           'CMD_SYNC' : 0xFC,       # Synchronize the A/D Conversion 1111   1100 (FCh)
           'CMD_STANDBY' : 0xFD,    # Begin Standby Mode 1111   1101 (FDh)
           'CMD_RESET' : 0xFE,      # Reset to Power-Up Values 1111   1110 (FEh)
          }

    dataRate = ADS1256_DRATE_E['ADS1256_50SPS'] # hold onto data rate
    currGain = ADS1256_GAIN_E['ADS1256_GAIN_1']
    
    def __init__(self):
        logging.debug("Create ADS1256")
        self.rst_pin = this.this.config.RST_PIN
        self.cs_pin = this.this.config.CS_PIN
        self.drdy_pin = this.this.config.DRDY_PIN

    # Hardware reset
    def ADS1256_reset(self):
        logging.debug("Reset ADS1256")
        this.this.config.digital_write(self.rst_pin, GPIO.HIGH)
        this.this.config.delay_ms(200)
        this.this.config.digital_write(self.rst_pin, GPIO.LOW)
        this.this.config.delay_ms(200)
        this.this.config.digital_write(self.rst_pin, GPIO.HIGH)
    
    def ADS1256_WriteCmd(self, reg):
        this.config.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        this.config.spi_writebyte([reg])
        this.config.digital_write(self.cs_pin, GPIO.HIGH)#cs 1
    
    def ADS1256_WriteReg(self, reg, data):
        this.config.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        this.config.spi_writebyte([CMD['CMD_WREG'] | reg, 0x00, data])
        this.config.digital_write(self.cs_pin, GPIO.HIGH)#cs 1
        
    def ADS1256_Read_data(self, reg):
        this.config.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        this.config.spi_writebyte([CMD['CMD_RREG'] | reg, 0x00])
        data = this.config.spi_readbytes(1)
        this.config.digital_write(self.cs_pin, GPIO.HIGH)#cs 1

        return data
        
    def ADS1256_WaitDRDY(self):
        for i in range(0,400000,1):
            if(this.config.digital_read(self.drdy_pin) == 0):
                
                break
        if(i >= 400000):
            print ("Time Out ...\r\n")
        
        
    def ADS1256_ReadChipID(self):
        self.ADS1256_WaitDRDY()
        id = self.ADS1256_Read_data(REG_E['REG_STATUS'])
        id = id[0] >> 4

        return id
        
    #The configuration parameters of ADC, gain and data rate
    def ADS1256_ConfigADC(self, gain, drate=0x63):
        print("ConfigADC G: ",gain, " dr 0x%x"%drate)
        self.ADS1256_WaitDRDY()
        buf = [0,0,0,0,0,0,0,0]
        buf[0] = (0<<3) | (1<<2) | (0<<1)
        buf[1] = 0x08
        buf[2] = (0<<5) | (0<<3) | (gain<<0)
        buf[3] = drate
        self.dataRate = drate
        self.currGain = gain
        this.this.config.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        this.this.config.spi_writebyte([CMD['CMD_WREG'] | 0, 0x03])
        this.this.config.spi_writebyte(buf)
        
        this.this.config.digital_write(self.cs_pin, GPIO.HIGH)#cs 1
        this.this.config.delay_ms(1)

    def ADS1256_SetChannal(self, Channal):
        if Channal > 7:
            return 0
        self.ADS1256_WriteReg(REG_E['REG_MUX'], (Channal<<4) | (1<<3))

    def ADS1256_SetDiffChannal(self, Channal):
        if Channal == 0:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (0 << 4) | 1)   #DiffChannal  AIN0-AIN1
        elif Channal == 1:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (2 << 4) | 3)   #DiffChannal   AIN2-AIN3
        elif Channal == 2:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (4 << 4) | 5)   #DiffChannal    AIN4-AIN5
        elif Channal == 3:
            self.ADS1256_WriteReg(REG_E['REG_MUX'], (6 << 4) | 7)   #DiffChannal   AIN6-AIN7

    def ADS1256_SetMode(self, Mode):
        ScanMode = Mode

    def ADS1256_init(self):
        #if (this.this.config.module_init() != 0):
        #    return -1
        self.ADS1256_reset()
        id = self.ADS1256_ReadChipID()
        if id == 3 :
            print("ID Read success  ")
        else:
            print("ID Read failed   ")
            return -1
        self.ADS1256_ConfigADC(ADS1256_GAIN_E['ADS1256_GAIN_1'], ADS1256_DRATE_E['ADS1256_50SPS'])
        return 0
        
    def ADS1256_Read_ADC_Data(self):
        this.config.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        this.this.config.spi_writebyte([CMD['CMD_RDATA']])
        this.this.config.delay_ms(10)
        buf = this.this.config.spi_readbytes(3)
        this.this.config.digital_write(self.cs_pin, GPIO.HIGH)#cs 1
        read = (buf[0]<<16) & 0xff0000
        read |= (buf[1]<<8) & 0xff00
        read |= (buf[2]) & 0xff
        if (read & 0x800000):
            read |= 0xFF000000
        return read
 
    def ADS1256_GetChannalValue(self, Channel):
        while(this.this.config.digital_read(self.drdy_pin) == 1):
            pass
        if(ScanMode == 0):# 0  Single-ended input  8 channel1 Differential input  4 channe 
            if(Channel>=8):
                return 0
            elif(Channel == 7):
                Channel = 0
            else :
                Channel = Channel + 1
            self.ADS1256_SetChannal(Channel)
            self.ADS1256_WriteCmd(CMD['CMD_SYNC'])
            this.this.config.delay_ms(10)
            self.ADS1256_WriteCmd(CMD['CMD_WAKEUP'])
            this.this.config.delay_ms(10)
            Value = self.ADS1256_Read_ADC_Data()
        else:
            if(Channel>=4):
                return 0
            self.ADS1256_SetDiffChannal(Channel)
            self.ADS1256_WriteCmd(CMD['CMD_SYNC'])
            this.this.config.delay_ms(10) 
            self.ADS1256_WriteCmd(CMD['CMD_WAKEUP'])
            this.this.config.delay_ms(10) 
            Value = self.ADS1256_Read_ADC_Data()
        return Value
        
    def ADS1256_GetAll(self):
        ADC_Value = [0,0,0,0,0,0,0,0]
        for i in range(0,8,1):
            ADC_Value[i] = self.ADS1256_GetChannalValue(i)
        return ADC_Value
    

    def ADS1256_gainLookup(self, gain):
        #print("gainLookup ",gain)
        if gain <= 1:
            return 0  #ADS1256_GAIN_E['ADS1256_GAIN_1']
        
        if gain <= 2:
            return 1 #ADS1256_GAIN_E['ADS1256_GAIN_2']
        
        if gain <= 4:
            return 2 #ADS1256_GAIN_E['ADS1256_GAIN_4']
        
        if gain <= 8:
            return 3 #ADS1256_GAIN_E['ADS1256_GAIN_8']
        if gain <= 16:
            return 4 #ADS1256_GAIN_E['ADS1256_GAIN_16']
        if gain <= 32:
            return 5 #ADS1256_GAIN_E['ADS1256_GAIN_32']
        return 6 #ADS1256_GAIN_E['ADS1256_GAIN_64']
        
    def ADS1256_GetLower(self, gain=0):
        ADC_Value = [0,0,0,0]
        if gain != self.currGain:
            self.ADS1256_ConfigADC(gain, self.dataRate)
        for i in range(4):
            ADC_Value[i] = self.ADS1256_GetChannalValue(i)
        return ADC_Value

    def ADS1256_GetUpper(self, gain=0):
        ADC_Value = [0,0,0,0]
        if gain != self.currGain:
            self.ADS1256_ConfigADC(gain, self.dataRate)
        for i in range(4,8,1):
            ADC_Value[i-4] = self.ADS1256_GetChannalValue(i)
        return ADC_Value
    
    def ADS1256_SyncWakeup(self):
        self.ADS1256_WriteCmd(CMD['CMD_SYNC'])
        this.this.config.delay_ms(10)
        self.ADS1256_WriteCmd(CMD['CMD_WAKEUP'])
        this.this.config.delay_ms(10)
###################################
#begin DAC8532

class DAC8532:
    channel_A   = 0x30
    channel_B   = 0x34

    DAC_Value_MAX = 65535

    DAC_VREF = 5 # 3.3
    def __init__(self):
        self.cs_pin = this.this.config.CS_DAC_PIN
        # this.this.config.module_init()
    
    def DAC8532_Write_Data(self, Channel, Data):
        this.config.digital_write(self.cs_pin, GPIO.LOW)#cs  0
        this.config.spi_writebyte([Channel, Data >> 8, Data & 0xff])
        this.config.digital_write(self.cs_pin, GPIO.HIGH)#cs  0
        
    def DAC8532_Out_Voltage(self, Channel, Voltage):
        if((Voltage <= DAC_VREF) and (Voltage >= 0)):
            temp = int(Voltage * DAC_Value_MAX / DAC_VREF)
            self.DAC8532_Write_Data(Channel, temp)        

if __name__ == "__main__":
    print("WaveshareADAC unitTest")
    try:
        ADC = ADS1256.ADS1256()
        DAC = DAC8532.DAC8532()
        ADC.ADS1256_init()

        DAC.DAC8532_Out_Voltage(0x30, 3)
        DAC.DAC8532_Out_Voltage(0x34, 3)
        while(1):
            ADC_Value = ADC.ADS1256_GetAll()
            print ("0 ADC = %lf"%(ADC_Value[0]*5.0/0x7fffff))
            print ("1 ADC = %lf"%(ADC_Value[1]*5.0/0x7fffff))
            print ("2 ADC = %lf"%(ADC_Value[2]*5.0/0x7fffff))
            print ("3 ADC = %lf"%(ADC_Value[3]*5.0/0x7fffff))
            print ("4 ADC = %lf"%(ADC_Value[4]*5.0/0x7fffff))
            print ("5 ADC = %lf"%(ADC_Value[5]*5.0/0x7fffff))
            print ("6 ADC = %lf"%(ADC_Value[6]*5.0/0x7fffff))
            print ("7 ADC = %lf"%(ADC_Value[7]*5.0/0x7fffff))

            temp = (ADC_Value[0]>>7)*5.0/0xffff
            print ("DAC :",temp)
            print ("\33[10A")
            DAC.DAC8532_Out_Voltage(DAC8532.channel_A, temp)
            DAC.DAC8532_Out_Voltage(DAC8532.channel_B, 3.3 - temp)

    except :
        GPIO.cleanup()
        print ("\r\nProgram end     ")
        exit()
