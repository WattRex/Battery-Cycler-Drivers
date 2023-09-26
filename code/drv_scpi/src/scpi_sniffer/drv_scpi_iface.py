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
from .drv_scpi_cmd import DrvScpiSerialConfC, DrvScpiStatusE

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class DrvScpiErrorC(Exception):
    "Error class for SCPI driver."
    def __init__(self, message: str, error_code: int) -> None:
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"Error: {self.message} \t Code: {self.error_code}"


class DrvScpiHandlerC:
    "Driver for SCPI devices."
    def __init__(self, serial_conf: DrvScpiSerialConfC) -> None:
        self.__serial: Serial = Serial(port               = serial_conf.port,
                                       baudrate           = serial_conf.baudrate,
                                       bytesize           = serial_conf.bytesize,
                                       parity             = serial_conf.parity,
                                       stopbits           = serial_conf.stopbits,
                                       timeout            = serial_conf.timeout,
                                       write_timeout      = serial_conf.write_timeout,
                                       inter_byte_timeout = serial_conf.inter_byte_timeout)
        self.__separator: str = serial_conf.separator
        port = self.__serial.port
        self.__rx_chan: SysShdIpcChanC = SysShdIpcChanC(name = f"RX_{port.split('/')[-1]}")
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


    def decode_and_split(self, data: bytes) -> List[str]:
        """Decode str to integers and split the data.
        Args:
            data (bytes): Value to decode and split.
        Returns:
            msg_decode (List[str]): Message decoded and splited.
        Raises:
            - None
        """
        data_dec = data.decode("utf-8")
        msg_decode = data_dec.split(f"{self.__separator}")
        return msg_decode


    def send_msg(self, msg: str) -> None:
        ''' Send a message to the serial device.
        Args:
            - msg (str): Message to send.
        Returns:
            - None
        Raises:
            - None
        '''
        port = self.__serial.port.split('/')[-1]
        log.info(f"Port: {port}. Message to send: {msg}")
        msg = msg + self.__separator
        self.__serial.write(bytes(msg.encode("utf-8")))


    def send_and_read(self, msg: str) -> List[str | int]:
        ''' Send a message to the serial device and read the response.
        Args:
            - msg (str): Message to send.
        Returns:
            - msg_read_decoded (List[str | int]): Received message.
        Raises:
            - None
        '''
        #"*IDN?" INFO DEVICE
        port = self.__serial.port.split('/')[-1]
        self.send_msg(msg)
        log.info(f"Reading port: {port}...")
        msg_read = self.__serial.readline()
        if len(msg_read) > 0:
            msg_read_decoded = self.decode_and_split(msg_read)
            self.__rx_chan.send_data(msg_read_decoded)
        else:
            log.error(f"Error during send port: {port}")
            msg_read_decoded = []
        return msg_read_decoded


    def close(self) -> None:
        ''' Close the serial connection.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        self.__serial.close()









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