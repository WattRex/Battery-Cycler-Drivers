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
    def __init__(self, data_type: DrvScpiCmdTypeE, port: str, **kwargs:any):
        '''
        Args:
            - data_type (DrvScpiCmdTypeE): Type of command to be sent to the device.
            - port (str): Port to be used to communicate with the device.
            - kwargs (optional): Payload to be sent to the device.
        Raises:
            - TypeError: If the data_type is ADD_DEV and the payload is
                         not a DrvScpiSerialConfC object.
            - TypeError: If the data_type is WRITE, WRITE_READ or RESP
                         and the payload is not a string.
        '''
        self.data_type: DrvScpiCmdTypeE = data_type
        self.port: str = port
        self.__dict__.update(kwargs)
        if self.data_type is not DrvScpiCmdTypeE.DEL_DEV:
            if hasattr(self, 'payload'):
                if self.data_type == DrvScpiCmdTypeE.ADD_DEV:
                    if not isinstance(self.payload, DrvScpiSerialConfC):
                        raise TypeError("No exist payload or must be a DrvScpiSerialConfC object")
                elif (self.data_type == DrvScpiCmdTypeE.WRITE or \
                    self.data_type == DrvScpiCmdTypeE.WRITE_READ or \
                    self.data_type == DrvScpiCmdTypeE.RESP) and (not isinstance(self.payload, str)):
                    raise TypeError("No exist payload or must be a string")
            else:
                log.error("No exist payload")


class DrvScpiSerialConfC:
    "Configuration of SCPI device."
    def __init__(self, port: str,           separator: str,
                 baudrate: int = 115200,    bytesize = EIGHTBITS,
                 parity = PARITY_NONE,      stopbits = STOPBITS_ONE,
                 timeout: float = 0.5,      write_timeout: float = 0.5,
                 inter_byte_timeout: float = 21) -> None:
        '''
        Args:
            - port (str): Name of the port to be used.
            - separator (str): Separator to be used to scpi commands.
            - baudrate (int, optional): SCPI baudrate value. Defaults to 115200.
            - bytesize (int, optional): SCPI bytesize value. Defaults to EIGHTBITS.
            - parity (str, optional): SCPI parity value. Defaults to PARITY_NONE.
            - stopbits (int, optional): SCPI stopbits value. Defaults to STOPBITS_ONE.
            - timeout (float, optional): SCPI timeout value. Defaults to 0.5.
            - write_timeout (float, optional): SCPI write_timeout value. Defaults to 0.5.
            - inter_byte_timeout (float, optional): SCPI inter_byte_timeout value. Defaults to 21.
        Raises:
            - None.
        '''
        self.port               = port
        self.separator          = separator
        self.baudrate           = baudrate
        self.bytesize           = bytesize
        self.parity             = parity
        self.stopbits           = stopbits
        self.timeout            = timeout
        self.write_timeout      = write_timeout
        self.inter_byte_timeout = inter_byte_timeout
