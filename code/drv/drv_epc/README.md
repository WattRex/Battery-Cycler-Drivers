### EXAMPLE INSTRUCTIONS
This readme explain how to use the example and the different ways you can try the driver.

## Hardware requirements
This example has been tested using a Raspberry PI Zero with the <[RS485 CAN HAT]>.
Also the hat has a manual that can be found <[here]>
However the most important commands and instructions to follow are the next:
`sudo nano /boot/config.tx`

Write the following configuration:
```console
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=10000
```

Apply with:
`sudo reboot`

And test with:
`dmesg | grep -i '\(can\|spi\)'`

## Test for 1 device without commands
Just connect the device and write the can id when ask, the file can be ignored pressing enter
The device will go from WAIT for 3s mode to CC 1A for 3s and back to WAIT again for ever.

## Test for n devices with commands
Connect the dessire devices and write the device id of each one, when the file is ask,
write the command file each file will follow.
It must follow the same order written in the device id.

## Example of command file
The command file can have the next instructions.
It must be located in a folder called example in drv_epc:
WAIT, CC, CV, and CP.
The WAIT mode is followed by the time in seconds wanted in WAIT MODE
The CC, CV and CP are followed by the ref in A/V/W the type of limit and the reference of the limit.
Here is an example of code:

```
WAIT, 5
CC, 0.5, TIME, 5
WAIT, 5
CV, 3, CURRENT, -1
WAIT, 6
CP, 2, VOLTAGE, 5
WAIT, 7.5
CC, 2, POWER, 3
WAIT, 7.5
```

[RS485 CAN HAT]: ttps://www.waveshare.com/rs485-can-hat.ht
[here]: ttps://www.waveshare.com/w/upload/2/29/RS485-CAN-HAT-user-manuakl-en.pd