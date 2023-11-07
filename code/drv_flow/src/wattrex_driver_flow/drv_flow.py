#!/usr/bin/python3
'''
Driver of ea power supply.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from enum import Enum
from time import sleep, time

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC, DrvScpiCmdTypeE
from wattrex_driver_base import DrvBaseStatusE, DrvBaseStatusC

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
_MAX_WAIT_TIME = 3
_TIME_BETWEEN_ATTEMPTS = 0.1
_TIMEOUT_REC = 0.1
_MAX_MSG = 100
_MAX_MESSAGE_SIZE = 300

class _ScpiCmds(Enum):
    "Modes of the device"
    READ_INFO = ':IDN*?\n'
    GET_MEAS  = ':MEASure:FLOW?\n'

#######################             CLASSES              #######################

class DrvFlowDataC():
    "Obtain the data of flowmeter"
    def __init__(self, flow_main: int, flow_aux: int ) -> None:
        '''
        Args:
            - flow_main (int): Value of main flow.
            - flow_aux (int): Value of auxiliar flow.
        Raises:
            - None.
        '''
        self.flow_main: int = flow_main
        self.flow_aux: int = flow_aux
        self.status: DrvBaseStatusC = DrvBaseStatusC(DrvBaseStatusE.OK)


    def __str__(self) -> str:
        '''
        Returns:
            - result (str): Value of flows.
        Raises:
            - None.
        '''
        result = f"Flow->\tPOS [{self.flow_main}] - \tNEG:[{self.flow_aux}]" +\
              f"- \tStatus: [{self.status}]"
        return result


class DrvFlowDeviceC():
    "Principal class of flowmeter"
    def __init__(self, dev_id: int, config: DrvScpiSerialConfC, rx_chan_name: str) -> None:
        '''
        Args:
            - config (DrvScpiSerialConfC): Configuration of the serial port.
        Raises:
            - None.
        '''
        self.__device_id: int = dev_id
        self.__firmware_version: int = 0
        self.__tx_chan = SysShdIpcChanC(name = 'tx_scpi')
        self.__rx_chan = SysShdIpcChanC(name = rx_chan_name,
                                      max_msg = _MAX_MSG,
                                      max_message_size= _MAX_MESSAGE_SIZE)
        self.__port = config.port

        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                  port = config.port,
                                  payload = config,
                                  rx_chan_name = rx_chan_name)
        self.__rx_chan.delete_until_last()
        self.__tx_chan.send_data(add_msg)
        self.__last_meas: DrvFlowDataC = DrvFlowDataC(flow_main = 0, flow_aux = 0)
        self.__wait_4_response = False
        self.__read_device_properties()


    @property
    def device_id(self) -> int:
        ''' Get the device id. '''
        return self.__device_id


    @property
    def firmware_version(self) -> int:
        ''' Get the firmware version. '''
        return self.__firmware_version


    def __read_device_properties(self) -> None:
        ''' Read device properties.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - ConnectionError: Device not found.
        '''
        exception = True
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.READ_INFO.value)
        self.__tx_chan.send_data(msg)

        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _MAX_WAIT_TIME:
            sleep(_TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0]
                if len(msg) > 0 and ('ERROR' not in msg) and ('IDN' in msg):
                    msg = msg.split(':')
                    self.__device_id = int(msg[msg.index('DEVice')+1])
                    self.__firmware_version = int(msg[msg.index('VERsion')+1])
                    exception = False
                else:
                    msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                            port = self.__port, payload = _ScpiCmds.READ_INFO.value)
                    self.__tx_chan.send_data(msg)
        self.__rx_chan.delete_until_last()
        if exception:
            raise ConnectionError("Device not found")


    def get_meas(self) -> DrvFlowDataC:
        ''' Get the measurement of the flowmeter.
        Args:
            - None.
        Returns:
            - res (DrvFlowDataC): Get the measurement of the flowmeter.
        Raises:
            - None.
        '''
        if not self.__wait_4_response:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port = self.__port,
                                payload = _ScpiCmds.GET_MEAS.value)
            self.__tx_chan.send_data(msg)
            self.__wait_4_response = True
        else:
            if not self.__rx_chan.is_empty():
                data : DrvScpiCmdDataC = self.__rx_chan.receive_data(timeout = _TIMEOUT_REC)
                msg_received = data.payload[0]
                self.__wait_4_response = False
                if len(msg_received) > 0 and ('ERROR' not in msg_received) and \
                    ('MEASure' in msg_received):
                    msg_received = msg_received.split(':')
                    self.__last_meas.flow_main = int(msg_received[msg_received.index('DATA')+1])
                    self.__last_meas.flow_aux = int(msg_received[msg_received.index('DATA')+2])
                    self.__last_meas.status = DrvBaseStatusC(DrvBaseStatusE.OK)
                else:
                    self.__last_meas.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
        return self.__last_meas


    def close(self) -> None:
        ''' Close the serial port.
        Args:
            - None.
        Returns:
            - res (DrvFlowDataC): Get the measurement of the flowmeter.
        Raises:
            - None.
        '''
        del_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                  port = self.__port) # pylint: disable=no-member
        self.__tx_chan.send_data(del_msg)
        self.__rx_chan.terminate()
