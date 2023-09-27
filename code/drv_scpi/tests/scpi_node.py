#!/usr/bin/python3
'''
This is an example of use of the SCPI module.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path, exit
import os

#######################         GENERIC IMPORTS          #######################
from time import sleep
from threading import Event
#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################
from drv_scpi.src.scpi_sniffer import *

#######################            FUNCTIONS             #######################
if __name__ == '__main__':
    # Flag to know if the SCPI is working
    _working_scpi = Event()
    _working_scpi.set()
    #Create the thread for SCPI
    scpi_node = DrvScpiNodeC(working_flag = _working_scpi, tx_scpi_long = 200)
    try:
        scpi_node.process_iteration()
        while 1:
            sleep(300)
            print("Elapsed time: 5 minutes  ")

    except KeyboardInterrupt:
        _working_scpi.clear()
        log.info('closing everything')
        exit(0)
