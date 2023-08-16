#!/usr/bin/python3
'''
Example to ea power supply.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
sys.path.append(os.getcwd())

#######################         GENERIC IMPORTS          #######################
import time


#######################       THIRD PARTY IMPORTS        #######################


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiHandlerC
from serial import PARITY_ODD

#######################          MODULE IMPORTS          #######################
from src.wattrex_driver_ea.drv_ea import DrvEaDeviceC
# from wattrex_driver_ea import DrvEaDeviceC

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def main():
    "Main function"
    init = time.time()

    #Create driver
    scpi = DrvScpiHandlerC(port = '/dev/ttyACM0', separator = '\n', timeout = 0.8,
                           write_timeout = 0.8, parity = PARITY_ODD, baudrate = 9600)
    drv = DrvEaDeviceC(handler = scpi)

    #Set properties
    if '2384' in drv.get_properties().model :
        drv.set_cv_mode(volt_ref = 12000, current_limit = 500, channel = 2)
    drv.set_cv_mode(volt_ref = 1000, current_limit = 500, channel = 1)
    time.sleep(4)

    #Obtain data
    log.info(f"Actual voltage: {drv.get_data().voltage}")
    if '2384' in drv.get_properties().model :
        log.info(f"Actual voltage out2: {drv.get_data(2).voltage}")

    #Disable output
    drv.disable()
    if '2384' in drv.get_properties().model :
        drv.disable(2)
    #Obtain properties
    properties = drv.get_properties()
    log.info(f"Max curr: {properties.max_current_limit}\tMax volt: {properties.max_volt_limit}\t\
             Max pwr: {properties.max_power_limit}\n\
             Model: {properties.model}\tSerial number: {properties.serial_number}")

    #Close driver
    drv.close()

    log.info(f"Time elapsed: {time.time() - init - 4}")


if __name__ == '__main__':
    main()
