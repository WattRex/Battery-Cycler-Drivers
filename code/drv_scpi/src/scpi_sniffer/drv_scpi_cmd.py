#!/usr/bin/python3
'''
Driver for communication with SCPI devices.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log
if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
class DrvScpiCmdTypeE(Enum):
    "Types of commands to be sent to the device."
    ADD_DEV     = 0
    DEL_DEV     = 1
    WRITE       = 2
    WRITE_READ  = 3
    RESP        = 4

class DrvScpiStatusE(Enum):
    "Status of SCPI."
    COMM_ERROR = -1
    OK = 0
    INTERNAL_ERROR = 1

#######################             CLASSES              #######################
class DrvScpiCmdDataC:
    "Principal class of the driver. Hold the data to be sent to the device."
    def __init__(self, data_type: DrvScpiCmdTypeE, port: str,\
                 payload: str|DrvScpiSerialConfC|None = None):
        self.data_type: DrvScpiCmdTypeE = data_type
        self.port: str = port
        self.payload: str|DrvScpiSerialConfC = payload


class DrvScpiSerialConfC:
    "Configuration of SCPI device."
    def __init__(self, port: str,           separator: str,
                 baudrate: int = 115200,    bytesize = EIGHTBITS,
                 parity = PARITY_NONE,      stopbits = STOPBITS_ONE,
                 timeout: float = 0.5,      write_timeout: float = 0.5,
                 inter_byte_timeout: float = 21) -> None:
        self.port               = port
        self.separator          = separator
        self.baudrate           = baudrate
        self.bytesize           = bytesize
        self.parity             = parity
        self.stopbits           = stopbits
        self.timeout            = timeout
        self.write_timeout      = write_timeout
        self.inter_byte_timeout = inter_byte_timeout
