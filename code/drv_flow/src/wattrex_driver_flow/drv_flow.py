#!/usr/bin/python3
'''
Driver of ea power supply.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum
import serial


#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
#from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
#if __name__ == '__main__':
#    cycler_logger = SysLogLoggerC()
#log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
class _CONSTANTS:
    SERIAL_PORT = "/dev/ttyACM1"
    MILI_UNITS = 1000
    MAX_ATTEMPTS = 5

class ScpiCmds(Enum):
    "Modes of the device"
    REQ_INFO = 'IDN*?'
    REQ_MEAS  = ':MEASure:FLOW?'
    MEAS_DATA = ':MEASure:FLOW:DATA'

#######################             CLASSES              #######################

class DrvFlowDataC():
    "Data class of flowmeter"
    def __init__(self, flow_p: int, flow_n: int ) -> None:
        self.flow_p = flow_p
        self.flow_n = flow_n

    def __str__(self) -> str:
        return f"Flow->\tPOS [{self.flow_p}] - \tNEG:[{self.flow_n}]"

class DrvFlowDeviceC():
    "Principal class of flowmeter"
    def __init__(self, serial_port: str = _CONSTANTS.SERIAL_PORT) -> None:
        self.serial = serial.Serial(port = serial_port, baudrate=9600, timeout=1,
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

    def get_meas(self) -> DrvFlowDataC:
        """ Get the measurement of the flowmeter"""
        req_msg = (ScpiCmds.REQ_MEAS.value + '\n').encode()
        self.serial.write(req_msg)

        n_tries = 0
        datos = None
        while n_tries < _CONSTANTS.MAX_ATTEMPTS:
            res = self.serial.readline()
            print(res)
            if res != b'':
                datos = res.decode()
                break
            n_tries += 1

        print(f"----------\n{datos}----------")
        res = None
        if datos is not None and datos.startswith(ScpiCmds.MEAS_DATA.value):
            flows = datos.split(' ')
            print(f"Data received: {flows}")
            res = DrvFlowDataC(int(flows[1]), int(flows[2]))
        return res

    def close(self):
        """ Close the serial port"""
        self.serial.close()
