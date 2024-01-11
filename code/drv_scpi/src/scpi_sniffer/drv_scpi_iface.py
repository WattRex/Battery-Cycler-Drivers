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
from system_shared_tool import SysShdIpcChanC, SysShdNodeStatusE # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from .drv_scpi_cmd import DrvScpiSerialConfC, DrvScpiCmdTypeE, DrvScpiCmdDataC # pylint: disable=wrong-import-position

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
NUM_ATTEMPTS = 10

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
    def __init__(self, serial_conf: DrvScpiSerialConfC, rx_chan_name: str) -> None:
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
                                       inter_byte_timeout = serial_conf.inter_byte_timeout,
                                       xonxoff=True, rtscts=False, dsrdtr=False)
        self.__serial.readlines()
        self.__separator: str = serial_conf.separator
        self.__rx_chan_name = rx_chan_name
        self.__rx_chan: SysShdIpcChanC = SysShdIpcChanC(name = self.__rx_chan_name)
        self.status: SysShdNodeStatusE = SysShdNodeStatusE.OK
        self.wait_4_response: bool = False
        self.num_attempts_read: int = 0

    def decode_numbers(self, data: str) -> float: #TODO: Check this function with all devices
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
        msg_decode = data_dec.split(f"{self.__separator}")[0]
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
        log.info(f"Port: {self.__rx_chan_name}. Message send to device: {msg}") # pylint: disable=logging-fstring-interpolation
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
        if self.__serial.readable() and self.__serial.in_waiting > 0:
            msg_read = self.__serial.readlines()
            log.warning(f"Port: {self.__rx_chan_name} \t Message read RX: {msg_read}")

            resp_msg = DrvScpiCmdDataC(port = self.__serial.port, data_type = DrvScpiCmdTypeE.RESP,
                                        payload = [], status = SysShdNodeStatusE.OK)
            if len(msg_read) > 0:

                msg_read_decoded = [self.decode_and_split(msg_read_partially) for msg_read_partially in msg_read]
                self.wait_4_response = False
                self.num_attempts_read = 0
                self.status = SysShdNodeStatusE.OK

                # Update message
                resp_msg.payload = msg_read_decoded
                resp_msg.status = self.status
                log.info(f"Rx chan: {self.__rx_chan_name}. Message send: {resp_msg.payload}")
                self.__rx_chan.send_data(resp_msg)
            else:
                self.num_attempts_read += 1
                if self.num_attempts_read >= NUM_ATTEMPTS and self.wait_4_response:
                    log.critical(f"rx chan: {self.__rx_chan_name}. No response from device") # pylint: disable=logging-fstring-interpolation
                    self.status = SysShdNodeStatusE.COMM_ERROR

                    # Update message
                    resp_msg.payload = []
                    resp_msg.status = self.status
                    self.__rx_chan.send_data(resp_msg)

    def close(self) -> None:
        ''' Close the serial connection.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        self.__rx_chan.terminate()
        self.__serial.close()
