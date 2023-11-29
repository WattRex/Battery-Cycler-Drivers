#!/usr/bin/python3
'''
Example of drv_bms.
'''
#export R_PATH=/home/plc/Battery-Cycler-Controller

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from time import sleep
from threading import Event

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='../log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################
from can_sniffer import DrvCanNodeC
#######################          MODULE IMPORTS          #######################
from src.wattrex_driver_bms import DrvBmsDeviceC # pylint: disable=wrong-import-position

#######################              ENUMS               #######################
_CAN_ID = 4

#######################              CLASS               #######################

if __name__ == '__main__':
    log.info('Starting example')
    can_flag = Event()
    can_flag.set()
    can_node = DrvCanNodeC(working_flag=can_flag, tx_buffer_size= 100)
    sleep(1)
    can_node.start()
    device = DrvBmsDeviceC(can_id= _CAN_ID)
    try:
        while 1:
            device.get_data()
            sleep(0.0001)
    except KeyboardInterrupt:
        device.close()
        sleep(1)
        can_flag.clear()
        can_node.join()
        log.info('Exiting example')
