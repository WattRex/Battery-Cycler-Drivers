#!/usr/bin/python3
'''
Example to RS.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import time
#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiHandlerC
from serial import PARITY_ODD

#######################          MODULE IMPORTS          #######################
from src.wattrex_driver_rs.drv_rs import DrvRsDeviceC

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def main():
    "Main function"
    init = time.time()
    #Create driver
    scpi = DrvScpiHandlerC(port = 'COM6', separator = '\n', timeout = 0.5,
                           write_timeout = 0.5, parity = PARITY_ODD, baudrate = 115200)
    drv = DrvRsDeviceC(handler = scpi)

    #Obtain properties
    properties = drv.get_properties()
    log.info(f"Max curr: {properties.max_current_limit}\tMax volt: {properties.max_volt_limit}\t\
             Max pwr: {properties.max_power_limit}\n\
            Model: {properties.model}\tSerial number: {properties.serial_number}")

    #Set properties
    drv.set_cv_mode(volt_ref = 8100)
    # drv.set_cc_mode(curr_ref = 1000)
    time.sleep(3)

    #Obtain data
    data = drv.get_data()
    log.info(f"Mode: {data.mode}\tStatus: {data.status}\n\
             Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}")

    #Close driver
    drv.close()

    log.info(f"Time elapsed: {time.time() - init - 3}")


if __name__ == '__main__':
    main()
