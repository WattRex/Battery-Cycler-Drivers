#!/usr/bin/python3
'''
Driver of RS.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from enum import Enum
from time import sleep

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
from wattrex_driver_base import (DrvBaseStatusE, DrvBaseStatusC, DrvBasePwrModeE, DrvBasePwrDeviceC,
                                DrvBasePwrPropertiesC, DrvBasePwrDataC)

#######################          MODULE IMPORTS          #######################

######################             CONSTANTS              ######################
from .context import (DEFAULT_TX_CHAN, DEFAULT_RX_CHAN,
                      DEFAULT_MAX_MSG, DEFAULT_MAX_MESSAGE_SIZE,
                      DEFAULT_MAX_READS)

#######################              ENUMS               #######################
_MILI_UNITS = 1000

class _ScpiCmds(Enum):
    "Modes of the device"
    READ_INFO   = '*IDN?'
    LOCK_ON     = ':SYST:LOCK 1'
    LOCK_OFF    = 'SYST:LOCK 0'
    OUTPUT_ON   = ':INP 1'
    OUTPUT_OFF  = ':INP 0'
    MAX_CURRENT = ':CURRent:UPPer?'
    MAX_VOLTAGE = ':VOLTage:UPPer?'
    MAX_POWER   = ':POWer:UPPer?'
    GET_MODE    = ':FUNC?'
    GET_CURR    = ':MEASure:CURRent?'
    GET_VOLT    = ':MEASure:VOLTage?'
    GET_POW     = ':MEASure:POWer?'

#######################             CLASSES              #######################
class DrvRsPropertiesC(DrvBasePwrPropertiesC):
    "Properties of load device"
    def __init__(self, model: str, serial_number: int, max_volt_limit: int, \
                 max_current_limit: int, max_power_limit: int) -> None:
        '''
        Args:
            - model (str): Model of the device.
            - serial_number (int): Serial number of the device.
            - max_volt_limit (int): Maximum voltage of the device in milivolts.
            - max_current_limit (int): Maximum current of the device in miliamps.
            - max_power_limit (int): Maximum power of the device in miliwatts.
        '''
        super().__init__(model = model, serial_number = serial_number,
                         max_volt_limit = max_volt_limit,
                         max_current_limit = max_current_limit,
                         max_power_limit = max_power_limit)


class DrvRsDataC(DrvBasePwrDataC):
    "Data class of RS device"
    def __init__(self, mode: DrvBasePwrModeE, voltage: int, current: int, power: int,
                 status: DrvBaseStatusE = DrvBaseStatusE.OK) -> None:
        '''
        Args:
            - mode (DrvEaModeE): Mode of the device.
            - status (DrvBaseStatusC): Status of the device.
            - voltage (int): Voltage in mV.
            - current (int): Current in mA.
            - power (int): Power in mW.
        Raises:
            - None.
        '''
        stat = DrvBaseStatusC(status)
        super().__init__(status = stat, mode = mode, voltage = voltage,
                         current = current, power = power)
        self.status: DrvBaseStatusC = stat
        self.mode: DrvBasePwrModeE = mode


class DrvRsDeviceC(DrvBasePwrDeviceC): #pylint: disable=too-many-instance-attributes
    "Principal class of RS device"
    def __init__(self, config: DrvScpiSerialConfC) -> None:
        '''
        Args:
            - config (DrvScpiSerialConfC): Configuration of the serial port.
            - rx_chan_name (str): Name of the channel to receive the messages.
        Raises:
            - None.
        '''
        super().__init__()
        self.__tx_chan = SysShdIpcChanC(name = DEFAULT_TX_CHAN)
        self.__rx_chan = SysShdIpcChanC(name = DEFAULT_RX_CHAN+'_'+config.port.split('/')[-1],
                                      max_msg = DEFAULT_MAX_MSG,
                                      max_message_size = DEFAULT_MAX_MESSAGE_SIZE)
        self.__port = config.port
        self.__separator = config.separator
        self.__wait_4_response = False
        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                  port = config.port,
                                  payload = config,
                                  rx_chan_name = DEFAULT_RX_CHAN+'_'+config.port.split('/')[-1])
        self.__tx_chan.send_data(add_msg)
        self.__rx_chan.delete_until_last()
        self.properties: DrvRsPropertiesC = DrvRsPropertiesC(model = None, serial_number = 0,
                                                             max_volt_limit = 0,
                                                             max_current_limit = 0,
                                                             max_power_limit = 0)
        self.last_data: DrvRsDataC = DrvRsDataC(mode = DrvBasePwrModeE.DISABLE,
                                                status = DrvBaseStatusE.OK,
                                                voltage = 0, current = 0, power = 0)
        self.__initialize_device()
        i = 0
        while self.properties.model is None and i<=DEFAULT_MAX_READS:
            self.read_buffer()
            sleep(1)
            i += 1
        i = 0
        while self.properties.max_power_limit == 0 and i<=DEFAULT_MAX_READS:
            self.read_buffer()
            sleep(1)
            i += 1
        if self.properties.model is None:
            log.error("Device not found")
            self.close()
            raise ConnectionError("Device not found")

    def read_buffer(self) -> None: #pylint: disable=too-many-branches, too-many-statements
        """
        Reads data from the receive channel and updates the device properties and last data.
        Returns:
            None
        """
        i = 0
        while i < DEFAULT_MAX_READS and not self.__rx_chan.is_empty(): #pylint: disable=too-many-nested-blocks
            msg: DrvScpiCmdDataC = self.__rx_chan.receive_data_unblocking()
            if msg is not None and msg.data_type == DrvScpiCmdTypeE.RESP:
                if hasattr(msg, 'status') and msg.status.value == DrvBaseStatusE.COMM_ERROR: #pylint: disable=attribute-defined-outside-init
                    log.critical("ERROR READING DEVICE")
                    self.last_data.status = DrvBaseStatusE.COMM_ERROR
                for data in msg.payload: #pylint: disable=too-many-nested-blocks #pylint: disable=attribute-defined-outside-init
                    if len(data) >0 and not str(data).startswith(":"):
                        if data.startswith('RS'):
                            data = data.split(' ')
                            self.properties.model = data[0] #pylint: disable=attribute-defined-outside-init
                            self.properties.serial_number = data[2].split(':')[-1] #pylint: disable=attribute-defined-outside-init
                            log.debug(f"Serial number: {data[2].split(':')[-1]}")
                            log.debug(f"Model: {data[0]}")
                        elif "W" in data and len(data.split('.')) == 2:
                            power = int(float(data.replace('W','')) * _MILI_UNITS)
                            if self.__wait_4_response:
                                self.last_data.power = power #pylint: disable=attribute-defined-outside-init
                                ##  Power is the one to set to false as is the last value requested
                                if power <= 0:
                                    self.last_data.mode = DrvBasePwrModeE.DISABLE
                                self.__wait_4_response = False
                                log.debug(f"Power: {power}")
                            else:
                                self.properties.max_power_limit = power #pylint: disable=attribute-defined-outside-init
                        elif "V" in data and len(data.split('.')) == 2:
                            volt = int(float(data.replace('V','')) * _MILI_UNITS)
                            if self.__wait_4_response:
                                self.last_data.voltage = volt #pylint: disable=attribute-defined-outside-init
                                log.debug(f"Voltage: {volt}")
                            else:
                                self.properties.max_volt_limit = volt #pylint: disable=attribute-defined-outside-init
                        elif "A" in data and len(data.split('.')) == 2:
                            curr = int(float(data.replace('A','')) * _MILI_UNITS)
                            if self.__wait_4_response:
                                self.last_data.current = curr #pylint: disable=attribute-defined-outside-init
                                log.debug(f"Current: {curr}")
                            else:
                                self.properties.max_current_limit = curr #pylint: disable=attribute-defined-outside-init
                        elif "CV" in data:
                            self.last_data.mode = DrvBasePwrModeE.CV_MODE
                            log.debug(f"New mode set to: {self.last_data.mode}")
                        elif "CC" in data:
                            self.last_data.mode = DrvBasePwrModeE.CC_MODE
                            log.debug(f"New mode set to: {self.last_data.mode}")
                        elif "CW" in data:
                            self.last_data.mode = DrvBasePwrModeE.CP_MODE
                            log.debug(f"New mode set to: {self.last_data.mode}")
            elif msg is None:
                pass
            else:
                log.error(f'Unknown message type received: {msg.__dict__}')
            i += 1

    def __initialize_device(self) -> None:
        ''' Initialize the control of the device.
        '''
        #disable manual inputs
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                              port = self.__port,
                              payload = (f"{_ScpiCmds.LOCK_ON.value}{self.__separator}"
                                         f"{_ScpiCmds.OUTPUT_OFF.value}{self.__separator}"
                                         f"{_ScpiCmds.READ_INFO.value}{self.__separator}"
                                         f"{_ScpiCmds.MAX_CURRENT.value}{self.__separator}"
                                         f"{_ScpiCmds.MAX_VOLTAGE.value}{self.__separator}"
                                         f"{_ScpiCmds.MAX_POWER.value}"))
        self.__tx_chan.send_data(msg)
        self.read_buffer()



    def get_data(self) -> DrvRsDataC:
        ''' Get the measurements of the device.
        Args:
            - payload (str): Payload of the message.
        Returns:
            - (DrvRsDataC): Measurement.
        '''
        if not self.__wait_4_response:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port = self.__port,
                                payload = (f"{_ScpiCmds.GET_MODE.value}{self.__separator}"
                                            f"{_ScpiCmds.GET_CURR.value}{self.__separator}"
                                            f"{_ScpiCmds.GET_VOLT.value}{self.__separator}"
                                            f"{_ScpiCmds.GET_POW.value}"))
            self.__tx_chan.send_data(msg)
            self.__wait_4_response = True
        # Wait until receive the message
        self.read_buffer()
        return self.last_data

    def set_cv_mode(self, volt_ref: int) -> None:
        ''' Set the device in CV mode.
        Args:
            - volt_ref (int): Voltage reference in milivolts.
        '''
        log.debug("Set CV mode...")
        if volt_ref > self.properties.max_volt_limit:
            volt_ref = self.properties.max_volt_limit
        voltage = float(volt_ref / _MILI_UNITS)
        if voltage > 0.0:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                    port = self.__port,
                                    payload = (f":VOLT {round(voltage, 4)}V{self.__separator}"
                                                f"{_ScpiCmds.OUTPUT_ON.value}"))
            self.__tx_chan.send_data(msg)
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        else:
            self.disable()
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.INTERNAL_ERROR)


    def set_cc_mode(self, curr_ref: int) -> None:
        ''' Set the device in CC mode.
        Args:
            - curr_ref (int): Current reference.
        '''
        log.debug("Set CC mode...")
        if curr_ref > self.properties.max_current_limit:
            curr_ref = self.properties.max_current_limit
        current = float(curr_ref / _MILI_UNITS)

        if current > 0.0:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                    port = self.__port,
                                    payload = f':CURR {round(current, 4)}A')
            self.__tx_chan.send_data(msg)
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                    port = self.__port,
                                    payload = _ScpiCmds.OUTPUT_ON.value)

            self.__tx_chan.send_data(msg)
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        else:
            self.disable()
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.INTERNAL_ERROR)

    def set_wait_mode(self) ->None:
        ''' Set the device in WAIT mode.
        '''
        self.disable()

    def disable(self) -> None:
        ''' Disable power input.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                port = self.__port,
                                payload = _ScpiCmds.OUTPUT_OFF.value)
        self.__tx_chan.send_data(msg)
        # self.last_data.mode = DrvBasePwrModeE.WAIT


    def close(self) -> None:
        ''' Desactivates the load and close the serial port.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        log.info("Close the load device...")
        self.disable()
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                port = self.__port,
                                payload = _ScpiCmds.LOCK_OFF.value)
        self.__tx_chan.send_data(msg)
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                port = self.__port))
        self.__tx_chan.close()
        self.__rx_chan.close()
