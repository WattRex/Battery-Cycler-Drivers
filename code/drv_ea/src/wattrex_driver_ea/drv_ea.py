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
# from scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC, DrvScpiCmdTypeE
from scpi_sniffer import *
from wattrex_driver_base import DrvBaseStatusE, DrvBaseStatusC

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
class _CONSTANTS:
    "Constants of the module"
    _MILI_UNITS = 1000
    _MAX_WAIT_TIME = 1
    _TIME_BETWEEN_ATTEMPTS = 0.1
    _TIMEOUT_REC = 0.1
    _MAX_MSG = 100
    _MAX_MESSAGE_SIZE = 400
    _TX_CHAN_NAME = 'tx_scpi'

class _ScpiCmds(Enum):
    "Modes of the device"
    READ_INFO = '*IDN?'
    GET_MEAS  = 'MEASure:ARRay?'
    CURR_NOM  = 'SYSTem:NOMinal:CURRent?'
    VOLT_NOM  = 'SYSTem:NOMinal:VOLTage?'
    POWER = 'SYSTem:NOMinal:POWer?'
    LOCK_ON = 'SYSTem:LOCK: ON'
    LOCK_OFF = 'SYSTem:LOCK: OFF'
    OUTPUT_ON = 'OUTPut: ON'
    OUTPUT_OFF = 'OUTPut: OFF'
    SEND_CURR = 'CURRent'
    SEND_VOLT = 'VOLTage'

class DrvEaModeE(Enum):
    "Modes of the device"
    STANDBY = 0
    CV_MODE = 1
    CC_MODE = 2


#######################             CLASSES              #######################
class DrvEaPropertiesC():
    "Properties of power supply device"
    def __init__(self, model: str, serial_number: int, max_volt_limit: int, \
                 max_current_limit: int, max_power_limit: int) -> None:
        '''
        Args:
            - model (str): Model of the device.
            - serial_number (int): Serial number of the device.
            - max_volt_limit (int): Maximum voltage limit of the device.
            - max_current_limit (int): Maximum current limit of the device.
            - max_power_limit (int): Maximum power limit of the device.
        Raises:
            - None.
        '''
        self.model: str = model
        self.serial_number: int = serial_number
        self.max_volt_limit: int = max_volt_limit
        self.max_current_limit: int = max_current_limit
        self.max_power_limit: int = max_power_limit

    def __str__(self) -> str:
        '''
        Returns:
            - result (str): Values.
        Raises:
            - None.
        '''
        result = f"Model: [{self.model}] - \tSerial number: [{self.serial_number}]" +\
              f"- \tMax volt limit: [{self.max_volt_limit}]" +\
              f"- \tMax current limit: [{self.max_current_limit}]" +\
              f"- \tMax power limit: [{self.max_power_limit}]"
        return result


class DrvEaDataC(): #TODO: Hereda de DrvBasePwrDataC
    "Data class of power supply device"
    def __init__(self, mode: DrvEaModeE, status: DrvBaseStatusE,\
                 voltage: int, current: int, power: int) -> None:
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
        self.mode: DrvEaModeE = mode
        self.status: DrvBaseStatusC = status
        self.voltage: int = voltage
        self.current: int = current
        self.power: int = power


    def __str__(self) -> str:
        '''
        Returns:
            - result (str): Values.
        Raises:
            - None.
        '''
        result = f"Mode: [{self.mode}] - \tVOLT [{self.voltage}] - \tCURR [{self.current}]" +\
              f"- \tPOW [{self.power}] - \tStatus: [{self.status}]"
        return result


class DrvEaDeviceC(): #TODO: Hereda de DrvBasePwrDeviceC
    "Principal class of ea power supply device"
    def __init__(self, config: DrvScpiSerialConfC, rx_chan_name: str) -> None:
        '''
        Args:
            - config (DrvScpiSerialConfC): Configuration of the serial port.
            - rx_chan_name (str): Name of the channel to receive the messages.
        Raises:
            - None.
        '''
        self.__tx_chan = SysShdIpcChanC(name = _CONSTANTS._TX_CHAN_NAME)
        self.__rx_chan = SysShdIpcChanC(name = rx_chan_name,
                                      max_msg = _CONSTANTS._MAX_MSG,
                                      max_message_size = _CONSTANTS._MAX_MESSAGE_SIZE)
        self.__port = config.port
        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV, \
                                  port = config.port, \
                                  payload = config, \
                                  rx_chan_name = rx_chan_name)
        self.__tx_chan.send_data(add_msg)
        self.__rx_chan.delete_until_last()
        self.__last_data: DrvEaDataC = DrvEaDataC(mode = DrvEaModeE.STANDBY, \
                                                  status = DrvBaseStatusC(DrvBaseStatusE.OK), \
                                                  current = 0, voltage = 0, power = 0)

        self.properties: DrvEaPropertiesC = DrvEaPropertiesC(model = '', serial_number = 0,
                                                                max_volt_limit = 0, \
                                                                max_current_limit = 0, \
                                                                max_power_limit = 0)
        self.__wait_4_response = False
        self.__read_device_properties()
        self.__initialize_control()


    def __initialize_control(self) -> None:
        ''' Initialize the device.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                              port = self.__port, \
                              payload = _ScpiCmds.LOCK_ON.value)
        self.__tx_chan.send_data(msg)
        self.disable()


    def __read_device_properties(self) -> None:
        ''' Read device properties.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - ConnectionError: Device not found.
        '''
        #Model and serial number
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.READ_INFO.value)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _CONSTANTS._MAX_WAIT_TIME:
            sleep(_CONSTANTS._TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0].split(',')
                self.properties.model = msg[1]
                self.properties.serial_number = int(msg[2])
        #Max current limit
        self.properties.max_current_limit = self.__get_nominal_value(_ScpiCmds.CURR_NOM.value)
        #Max voltage limit
        self.properties.max_volt_limit = self.__get_nominal_value(_ScpiCmds.VOLT_NOM.value)
        #Max power limit
        self.properties.max_power_limit = self.__get_nominal_value(_ScpiCmds.POWER.value)


    def __get_nominal_value(self, payload: str) -> int:
        ''' Get nominal value.
        Args:
            - payload (str): Payload of the message.
        Returns:
            - result (int): Nominal value.
        Raises:
            - None.
        '''
        result = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = payload)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _CONSTANTS._MAX_WAIT_TIME:
            sleep(_CONSTANTS._TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0].split(' ')
                result = int(float(msg[0]) * _CONSTANTS._MILI_UNITS)
        return result


    def get_data(self) -> DrvEaDataC:
        '''Read the device data.
        Args:
            - None.
        Returns:
            - result (DrvEaDataC): Returns the device data.
        Raises:
            - None.
        '''
        log.info(f"Get meas...")
        result: DrvEaDataC = DrvEaDataC(mode = self.__last_data.mode, \
                                        status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR), \
                                        voltage = 0, current = 0, power = 0)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, \
                            port = self.__port, \
                            payload = _ScpiCmds.GET_MEAS.value)
        self.__tx_chan.send_data(msg)
        time_init = time()
        while (time() - time_init) < _CONSTANTS._MAX_WAIT_TIME:
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0].split(' ')
                result.voltage  = int(float(msg[0]) * _CONSTANTS._MILI_UNITS)
                result.current  = int(float(msg[2]) * _CONSTANTS._MILI_UNITS)
                result.power    = int(float(msg[4]) * _CONSTANTS._MILI_UNITS)
                result.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        return result


    def set_cc_mode(self, curr_ref: int, voltage_limit: int) -> None:
        '''
        Use source in constant current mode.
        Sink mode will be set with negative current values.
        Security voltage limit can be also set.
        Args:
            - curr_ref (int): current reference (mili Amps)
            - voltage_limit (int): voltage limit (milivolts)
        Returns:
            - None
        Raises:
            - None
        '''
        self.__last_data.mode = DrvEaModeE.CC_MODE
        current = round(float(curr_ref) / _CONSTANTS._MILI_UNITS, 2)
        voltage = round(float(voltage_limit / _CONSTANTS._MILI_UNITS), 2)

        #Check if the power limit is exceeded
        if self.properties.max_power_limit != 0:
            max_power_limit = self.properties.max_power_limit / _CONSTANTS._MILI_UNITS
            if current * voltage > max_power_limit:
                voltage = max_power_limit / curr_ref
        else:
            current = 0
            voltage = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_CURR.value + str(current))
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_VOLT.value + str(voltage))
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.OUTPUT_ON.value)
        self.__tx_chan.send_data(msg)


    def set_cv_mode(self, volt_ref: int, current_limit: int) -> None:
        '''
        Use source in constant voltage mode .
        Security current limit can be also set for both sink and source modes. 
        It is recommended to set both!
        Args:
            - volt_ref (int): voltage reference (milivolts)
            - current_limit (int): current limit (mili Amps)
        Returns:
            - None
        Raises:
            - None
        '''
        self.__last_data.mode = DrvEaModeE.CV_MODE
        voltage = round(float(volt_ref)/_CONSTANTS._MILI_UNITS, 2)
        current = round(float(current_limit/_CONSTANTS._MILI_UNITS), 2)
        #Check if the power limit is exceeded
        if self.properties.max_power_limit != 0:
            max_power_limit = self.properties.max_power_limit/_CONSTANTS._MILI_UNITS
            if voltage * current > max_power_limit:
                current = max_power_limit / volt_ref
        else:
            current = 0
            voltage = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_CURR.value + str(current))
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_VOLT.value + str(voltage))
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.OUTPUT_ON.value)
        self.__tx_chan.send_data(msg)


    def disable(self) -> None:
        ''' Set the device in standby mode.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None 
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                port = self.__port, \
                                payload = _ScpiCmds.OUTPUT_OFF.value)
        self.__tx_chan.send_data(msg)
        self.__last_data.mode = DrvEaModeE.STANDBY


    def close(self) -> None:
        ''' Close the serial port.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        self.disable()
        del_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                  port = self.__port) # pylint: disable=no-member
        self.__tx_chan.send_data(del_msg)
        self.__rx_chan.terminate()
