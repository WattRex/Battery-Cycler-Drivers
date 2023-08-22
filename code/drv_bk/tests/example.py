#!/usr/bin/python3

'''
Example to bk precision.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import time

#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiHandlerC

#######################          MODULE IMPORTS          #######################
from src.wattrex_driver_bk.drv_bk import DrvBkModeE, DrvBkDeviceC

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def main():
    "Main function"
    init = time.time()

    #Create driver
    scpi = DrvScpiHandlerC(port = '/dev/ttyUSB1', separator='\n', baudrate=38400, \
                                               timeout=1, write_timeout=1)
    drv = DrvBkDeviceC(handler = scpi)

    #Set properties
    drv.set_mode(DrvBkModeE.CURR_AUTO)

    #Obtain data
    data = drv.get_data()
    log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
              Mode: {data.mode}\tStatus: {data.status}")

    #Obtain properties
    properties = drv.get_properties()
    log.info(f"Voltage: {properties.max_volt_limit}\tCurrent: {properties.max_current_limit}\t\
             Power: {properties.max_power_limit}\n\
             Model: {properties.model}\tSerial number: {properties.serial_number}")
    log.info(f"Time elapsed: {time.time() - init}")


if __name__ == '__main__':
    main()
