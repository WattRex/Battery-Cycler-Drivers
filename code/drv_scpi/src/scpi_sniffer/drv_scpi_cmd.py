#!/usr/bin/python3
'''
Driver for communication with SCPI devices.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log
if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################
from system_shared_tool import SysShdChanC

#######################          MODULE IMPORTS          #######################
from .drv_scpi_iface import DrvScpiHandlerC

#######################              ENUMS               #######################
class DrvScipiCmdTypeE(Enum):
    '''Types of commands to be sent to the device.'''
    WRITE = 0
    READ = 1
    WRITE_READ = 2
    ADD_DEV = 3

#######################             CLASSES              #######################
class DrvScpiCmdDataC:
    '''
    Hold the data to be sent to the device.
    '''
    def __init__(self, data_type: DrvScipiCmdTypeE, port: str, payload: str|DrvScpiHandlerC):
        self.data_type: DrvScipiCmdTypeE = data_type
        self.port: str = port
        self.payload: str|DrvScpiHandlerC = payload


class DrvScpiDeviceC:
    '''
    Principal class of the driver.
    '''
    def __init__(self, port: str, payload: DrvScpiHandlerC, chan: SysShdChanC):
        self.port : str= port
        self.payload : DrvScpiHandlerC = payload
        self.chan : SysShdChanC = chan
