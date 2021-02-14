#!/bin/bash
# turn off Modac relays via shell script
BASE_GPIO_PATH=/sys/class/gpio

ACTIVE_LOW_ON="0"
ACTIVE_LOW_OFF="1"
ACTIVE_HI_ON="1"
ACTIVE_HI_OFF="0"

#activeHI - some relays are active HI, other active Low
relay0=5
relay9=26
relay10=19
relay11=13
#ActiveLow (relays
relay1=21
relay2=20
relay3=16
relay4=12
relay5=7
relay6=8
relay7=25
relay8=24

# util functoins
# export as output
exportPin()
{
    if [ ! -e $BASE_GPIO_PATH/gpio$1 ]; then
      echo "export " $1
      echo $1 > $BASE_GPIO_PATH/export
    fi
}
setOutput()
{
  echo "out" > $BASE_GPIO_PATH/gpio$1/direction
}

setRelayState()
{
  echo "set gpio" $1 $2
  echo $2 > $BASE_GPIO_PATH/gpio$1/value
}

exportPin $relay0
exportPin $relay1
exportPin $relay2
exportPin $relay3
exportPin $relay4
#exportPin $relay5
#exportPin $relay6
exportPin $relay7
exportPin $relay8
exportPin $relay9
exportPin $relay10
exportPin $relay11

setOutput $relay0
setOutput $relay1
setOutput $relay2
setOutput $relay3
setOutput $relay4
#exportPin $relay5
#exportPin $relay6
setOutput $relay7
setOutput $relay8
setOutput $relay9
setOutput $relay10
setOutput $relay11

activeHI_On()
{
  echo "Active Hi ON"
  setRelayState $relay0 $ACTIVE_HI_ONsetOutput
  setRelayState $relay9 $ACTIVE_HI_ON
  setRelayState $relay10 $ACTIVE_HI_ON
  setRelayState $relay11 $ACTIVE_HI_ON
}

activeLow_On()
{
  echo "Active Low ON"
  setRelayState $relay1 $ACTIVE_LOW_ON
  setRelayState $relay2 $ACTIVE_LOW_ON
  setRelayState $relay3 $ACTIVE_LOW_ON
  setRelayState $relay4 $ACTIVE_LOW_ON
  #setRelayState $relay5 $ACTIVE_LOW_ON
  #setRelayState $relay6 $ACTIVE_LOW_ON
  setRelayState $relay7 $ACTIVE_LOW_ON
  setRelayState $relay8 $ACTIVE_LOW_ON
  setRelayState $relay9 $ACTIVE_LOW_ON
}

activeHI_On

activeLow_On



