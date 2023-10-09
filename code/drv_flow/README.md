#### DRIVER FOR FLOWMETER
1. Introduction

    The purpose of this package is to communicate with the flowmeter, read the measurements and save them to a csv file.
    To do this, you need one or two flowmeters and an Arduino Uno.


2. Flowmeter features

    Flow range: 0.05 l/min - 10 l/min.\
    Supply voltage: 4.5V -24V.\
    Rated current: 8mA.\
    Output: NPN/PNP pulse current\
    Pipe diameter range: 8mm.\
    Connections:

        - Blue: Output.
        - Red: +4,5 - 24V.
        - Screen 0 V.


3. Arduino connection diagram
    
    Power of the arduino through the usb to usb port of the controller.

    Flow main:

        - Blue: Pin 2
        - Red: 5V
        - Screen: GND

    Flow aux:

        - Blue: Pin 8
        - Red: 5V
        - Screen: GND


4. SCPI Commands

    - Message: 'IDN*?' Response: ':IDN:FLOWmeter:DEVice: Device_number :VERsion: firmware_version \n'
    - Message: ':MEASure:FLOW?' Response: ':MEASure:FLOW:DATA flow_main flow_aux \n'


5. References
- Flowmeter: https://es.rs-online.com/web/p/caudalimetros/5082704
- Arduino uno: https://store.arduino.cc/products/arduino-uno-rev3
