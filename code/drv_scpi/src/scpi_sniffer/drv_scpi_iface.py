#!/usr/bin/python3
"""
Driver for SCPI devices.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import re

#######################         GENERIC IMPORTS          #######################
from enum import Enum
from typing import List
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, Serial

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log

if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
class _DefSerParamsC:
    "Default serial parameters"
    _BAUD_RATE = 115200
    _BYTESIZE = EIGHTBITS
    _PARITY = PARITY_NONE
    _STOP_BITS = STOPBITS_ONE
    _READ_TIMEOUT = 0.5
    _WRITE_TIMEOUT = 0.5
    _INTER_BYTE_TIMEOUT = 0.5
    _MAX_LEN_IN_BYTES = 21


class DrvScpiStatusE(Enum):
    "Status of SCPI."
    COMM_ERROR = -1
    OK = 0
    INTERNAL_ERROR = 1

#######################             CLASSES              #######################
class DrvScpiErrorC(Exception):
    "Error class for SCPI driver."

    def __init__(self, message: str, error_code: int) -> None:
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"Error: {self.message} \t Code: {self.error_code}"


class DrvScpiSerialConfC:
    "Configuration of SCPI device."

    def __init__(self, port: str, separator: str,
                 baudrate: int              = _DefSerParamsC._BAUD_RATE,
                 bytesize                   = _DefSerParamsC._BYTESIZE,
                 parity                     = _DefSerParamsC._PARITY,
                 stopbits                   = _DefSerParamsC._STOP_BITS,
                 timeout: float             = _DefSerParamsC._READ_TIMEOUT,
                 write_timeout: float       = _DefSerParamsC._WRITE_TIMEOUT,
                 inter_byte_timeout: float  = _DefSerParamsC._INTER_BYTE_TIMEOUT) -> None:
        self.port               = port
        self.separator          = separator
        self.baudrate           = baudrate
        self.bytesize           = bytesize
        self.parity             = parity
        self.stopbits           = stopbits
        self.timeout            = timeout
        self.write_timeout      = write_timeout
        self.inter_byte_timeout = inter_byte_timeout


class DrvScpiHandlerC:
    "Driver for SCPI devices."

    def __init__(self, serial_conf: DrvScpiSerialConfC) -> None:
        self.__serial: Serial = Serial(port = serial_conf.port,
                                       baudrate           = serial_conf.baudrate,
                                       bytesize           = serial_conf.bytesize,
                                       parity             = serial_conf.parity,
                                       stopbits           = serial_conf.stopbits,
                                       timeout            = serial_conf.timeout,
                                       write_timeout      = serial_conf.write_timeout,
                                       inter_byte_timeout = serial_conf.inter_byte_timeout)
        self.__separator: str = serial_conf.separator
        self.__rx_chan: SysShdIpcChanC = None  #TODO: Se construye con el puerto aqui rx_nombrepuerto
        self.status: DrvScpiStatusE = None

    def decode_numbers(self, data: str) -> List[int]:
        ''' Decode bytes to integers.
        Args:
            - data (str): Value to convert to int.
        Returns:
            - msg_decode (List[int]): List of value decoded.
        Raises:
            - DrvScpiErrorC: Error decoding data.
        '''
        msg_decode = []
        return msg_decode


    def decode_and_split(self, data: str) -> List[str]:
        ''' Decode str to integers and split the data.
        Args:
            - data (str): Value to decode and split.
        Returns:
            msg_decode (List[str]): List of message decoded and splited.
        Raises:
            - None
        '''
        msg_decode = []
        return msg_decode


    def read_device_info(self) -> List[str]:
        ''' Reads the list of device information.
        Args:
            - None
        Returns:
            - result (List[str]): List of device information.
        Raises:
            - DrvScpiErrorC: Error decoding data.
        '''
        result = []
        return result


    def send_msg(self, msg: str) -> None:
        ''' Send a message to the serial device.
        Args:
            - msg (str): Message to send.
        Returns:
            - None
        Raises:
            - None
        '''
        pass


    def send_and_read(self, msg: str) -> List[str | int]:
        ''' Send a message to the serial device and read the response.
        Args:
            - msg (str): Message to send.
        Returns:
            - result (List[str | int]): Received message.
        Raises:
            - None
        '''
        result = []
        return result


    def close(self) -> None:
        ''' Close the serial connection.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        pass









# CODIGO VIEJO || DELETE
# def decode_numbers(self, data: str) -> float:
#     """Decode bytes to integers.
#     Args:
#         - data (str): Value to convert to float.
#     Returns:
#         - msg_decode (float): Value decoded.
#     Raises:
#         - DrvScpiErrorC: Error decoding data.
#     """
#     result: list = re.findall(r"-?\d*\.?\d+", data)
#     if len(result) < 2:
#         msg_decode = float(result[0])
#     elif len(result) == 2:
#         msg_decode = float(result[0]) * 10 ** int(result[1])
#     else:
#         raise DrvScpiErrorC(message="Error decoding data", error_code=1)
#     return msg_decode

# def decode_and_split(self, data: bytes) -> List[str]:
#     """Decode str to integers and split the data.
#     Args:
#         data (bytes): Value to decode and split.
#     Returns:
#         msg_decode (List[str]): Message decoded and splited.
#     Raises:
#         - None
#     """
#     data_dec = data.decode("utf-8")
#     msg_decode = data_dec.split(f"{self.__separator}")
#     return msg_decode

# def read_device_info(self) -> List[str]:
#     """Reads the list of device information.
#     Args:
#         - None
#     Returns:
#         - msg (List[str]): List of device information.
#     Raises:
#         - DrvScpiErrorC: Error decoding data.
#     """
#     msg = self.send_and_read("*IDN?")
#     if len(msg) > 0:
#         return msg
#     raise DrvScpiErrorC(message="Error reading device information",
#                         error_code=2)

# def send_msg(self, msg: str) -> None:
#     """Send a message to the serial device.
#     Args:
#         - msg (str): Message to send.
#     Returns:
#         - None
#     Raises:
#         - None
#     """
#     msg = msg + self.__separator
#     self.__serial.write(bytes(msg.encode("utf-8")))

# def receive_msg(self) -> List[str]:
#     """
#     Read until an separator is found, the size is exceeded or until timeout occurs.
#     Args:
#         - None
#     Returns:
#         - msg_decoded (List[str]): Received message of the device.
#     Raises:
#         - None
#     """
#     msg = self.__serial.readline()
#     msg_decoded = self.decode_and_split(msg)
#     return msg_decoded

# def send_and_read(self, msg: str) -> List[str]:
#     """Send a message to the serial device and read the response.
#     Args:
#         - msg (str): Message to send.
#     Returns:
#         - msg (List[str]): Received message.
#     Raises:
#         - None
#     """
#     self.send_msg(msg)
#     response: list = self.receive_msg()
#     return response

# def close(self) -> None:
#     """Close the serial connection.
#     Args:
#         - None
#     Returns:
#         - None
#     Raises:
#         - None
#     """
#     self.__serial.close()
