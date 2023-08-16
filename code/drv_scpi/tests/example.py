#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
Example of use of the driver for SCPI devices.
"""

#######################        MANDATORY IMPORTS         #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import sys
sys.path.append("..")

from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################
#######################          MODULE IMPORTS          #######################
from src.scpi_sniffer.drv_scpi_iface import DrvScpiHandlerC

#######################          PROJECT IMPORTS         #######################


#######################              ENUMS               #######################

#######################              CLASSES             #######################

def example():
    '''Example of the remote SCPI.
    '''
    multimeter = DrvScpiHandlerC(port='/dev/ttyUSB0', separator='\n',
                                baudrate= 38400)
    log.info("multimeter")
    # multimeter.send_msg('VOLT:DC:NPLC 1')
    # multimeter.send_msg('FETCH?')
    # multimeter.receive_msg()
    # multimeter.send_and_read('FETCH?')
    log.info(f"{multimeter.read_device_info()}")

    source = DrvScpiHandlerC(port = '/dev/ttyACM0', separator = '\n',
                            baudrate = 9600)
    log.info("source")
    # source.send_msg('SYSTem:LOCK: ON')
    # source.send_msg('SYSTem:LOCK: OFF')
    # source.send_and_read('MEASure:VOLTage?')
    log.info(f"{source.read_device_info()}")


if __name__ == '__main__':
    example()