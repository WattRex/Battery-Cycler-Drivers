#!/usr/bin/python3
"""
Driver for SCPI devices.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import re

#######################         GENERIC IMPORTS          #######################
from typing import List
from serial import Serial

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log

if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from .drv_scpi_cmd import DrvScpiSerialConfC, DrvScpiStatusE, DrvScpiCmdTypeE, DrvScpiCmdDataC # pylint: disable=wrong-import-position

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
NUM_ATTEMPTS = 5

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
        '''
        Args:
            - serial_conf (DrvScpiSerialConfC): Configuration of the serial port.
        Raises:
            - None.
        '''
        self.__serial: Serial = Serial(port               = serial_conf.port,
                                       baudrate           = serial_conf.baudrate,
                                       bytesize           = serial_conf.bytesize,
                                       parity             = serial_conf.parity,
                                       stopbits           = serial_conf.stopbits,
                                       timeout            = serial_conf.timeout,
                                       write_timeout      = serial_conf.write_timeout,
                                       inter_byte_timeout = serial_conf.inter_byte_timeout)
        self.__separator: str = serial_conf.separator
        self.__rx_chan_name = self.__serial.port.split('/')[-1]
        self.__rx_chan: SysShdIpcChanC = SysShdIpcChanC(name = f"rx_{self.__rx_chan_name}")
        self.status: DrvScpiStatusE = DrvScpiStatusE.OK
        self.wait_4_response: bool = False
        self.num_attempts_read: int = 0


    def decode_numbers(self, data: str) -> float:
        """Decode str to integers.
        Args:
            - data (str): Value to convert to float.
        Returns:
            - msg_decode (float): Value decoded.
        Raises:
            - DrvScpiErrorC: Error decoding data.
        """
        result: list = re.findall(r"-?\d*\.?\d+", data)
        if len(result) < 2:
            msg_decode = float(result[0])
        else:
            msg_decode = float(result[0]) * 10 ** int(result[1])
        return msg_decode


    def decode_and_split(self, data: bytes) -> List[str]:
        """Decode str to integers and split the data.
        Args:
            data (bytes): Value to decode and split.
        Returns:
            msg_decode (List[str]): Message decoded and splited.
        Raises:
            - None.
        """
        data_dec = data.decode("utf-8")
        msg_decode = data_dec.split(f"{self.__separator}")
        return msg_decode


    def send(self, msg: str) -> None:
        ''' Send a message to the serial device.
        Args:
            - msg (str): Message to send.
        Returns:
            - None.
        Raises:
            - None.
        '''
        log.info(f"Port: {self.__rx_chan_name}. Message to send: {msg}") # pylint: disable=logging-fstring-interpolation
        msg = msg + self.__separator
        self.__serial.write(bytes(msg.encode("utf-8")))


    def read(self) -> None:
        ''' Send a message to the serial device and read the response.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        log.info(f"Reading port: {self.__rx_chan_name}...") # pylint: disable=logging-fstring-interpolation
        msg_read = self.__serial.readline() #TODO: Check if this is the best way to read
        if len(msg_read) > 0:
            msg_read_decoded = self.decode_and_split(msg_read)
            msg_read_decoded = f"{msg_read_decoded}"
            send_data = DrvScpiCmdDataC(port = self.__serial.port, data_type = DrvScpiCmdTypeE.RESP,
                                        payload = msg_read_decoded)
            self.__rx_chan.send_data(send_data)
            self.wait_4_response = False
            self.num_attempts_read = 0
            self.status = DrvScpiStatusE.OK
        else:
            self.num_attempts_read += 1
            if self.num_attempts_read >= NUM_ATTEMPTS:
                log.critical(f"Port: {self.__rx_chan_name}. No response from device") # pylint: disable=logging-fstring-interpolation
                self.status = DrvScpiStatusE.COMM_ERROR


    def close(self) -> None:
        ''' Close the serial connection.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        self.__serial.close()
        self.__rx_chan.terminate()
