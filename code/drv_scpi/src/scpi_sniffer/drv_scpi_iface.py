#!/usr/bin/python3
"""
Driver for SCPI devices.
"""
#######################        MANDATORY IMPORTS         #######################
import re

#######################         GENERIC IMPORTS          #######################
from typing import List
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, Serial

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log

if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################


#######################              ENUMS               #######################
class _DefaultSerialParamsC:
    "Communication constants"
    _BAUD_RATE = 115200
    _BYTESIZE = EIGHTBITS
    _PARITY = PARITY_NONE
    _STOP_BITS = STOPBITS_ONE
    _READ_TIMEOUT = 0.5
    _WRITE_TIMEOUT = 0.5
    _INTER_BYTE_TIMEOUT = 0.5
    _MAX_LEN_IN_BYTES = 21


#######################             CLASSES              #######################
class DrvScpiErrorC(Exception):
    """Error class for SCPI driver."""

    def __init__(self, message: str, error_code: int) -> None:
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"Error: {self.message} \t Code: {self.error_code}"


class DrvScpiHandlerC:
    """Driver for SCPI devices."""

    #pylint: disable=too-many-arguments
    def __init__(self, port: str, separator: str,
                baudrate: int = _DefaultSerialParamsC._BAUD_RATE,
                bytesize=_DefaultSerialParamsC._BYTESIZE,
                parity=_DefaultSerialParamsC._PARITY,
            stopbits=_DefaultSerialParamsC._STOP_BITS,
            timeout=_DefaultSerialParamsC._READ_TIMEOUT,
            write_timeout=_DefaultSerialParamsC._WRITE_TIMEOUT,
            inter_byte_timeout=_DefaultSerialParamsC._INTER_BYTE_TIMEOUT,
            ) -> None:

        self.__serial: Serial = Serial(port=port, baudrate=baudrate,
                                       bytesize=bytesize, parity=parity,
                                       stopbits=stopbits, timeout=timeout,
                                       write_timeout=write_timeout,
                                       inter_byte_timeout=inter_byte_timeout)
        self.__separator: str = separator

    def decode_numbers(self, data: str) -> float:
        """Decode bytes to integers.
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
        elif len(result) == 2:
            msg_decode = float(result[0]) * 10 ** int(result[1])
        else:
            raise DrvScpiErrorC(message="Error decoding data", error_code=1)
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

    def read_device_info(self) -> List[str]:
        """Reads the list of device information.
        Args:
            - None
        Returns:
            - msg (List[str]): List of device information.
        Raises:
            - DrvScpiErrorC: Error decoding data.
        """
        msg = self.send_and_read("*IDN?")
        if len(msg) > 0:
            return msg
        raise DrvScpiErrorC(message="Error reading device information",
                            error_code=2)

    def send_msg(self, msg: str) -> None:
        """Send a message to the serial device.
        Args:
            - msg (str): Message to send.
        Returns:
            - None
        Raises:
            - None
        """
        msg = msg + self.__separator
        self.__serial.write(bytes(msg.encode("utf-8")))

    def receive_msg(self) -> List[str]:
        """
        Read until an separator is found, the size is exceeded or until timeout occurs.
        Args:
            - None
        Returns:
            - msg_decoded (List[str]): Received message of the device.
        Raises:
            - None
        """
        msg = self.__serial.readline()
        msg_decoded = self.decode_and_split(msg)
        return msg_decoded

    def send_and_read(self, msg: str) -> List[str]:
        """Send a message to the serial device and read the response.
        Args:
            - msg (str): Message to send.
        Returns:
            - msg (List[str]): Received message.
        Raises:
            - None
        """
        self.send_msg(msg)
        response: list = self.receive_msg()
        return response

    def close(self) -> None:
        """Close the serial connection.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        """
        self.__serial.close()
