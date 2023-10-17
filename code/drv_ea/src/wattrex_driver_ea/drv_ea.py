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
    GET_MEAS  = ':MEASure:FLOW?\n'
    CURR_NOM  = 'SYSTem:NOMinal:CURRent?'
    VOLT_NOM  = 'SYSTem:NOMinal:VOLTage?'
    POWER = 'SYSTem:NOMinal:POWer?'

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
        self.model: str = model
        self.serial_number: int = serial_number
        self.max_volt_limit: int = max_volt_limit
        self.max_current_limit: int = max_current_limit
        self.max_power_limit: int = max_power_limit
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


class DrvEaDataC():
    "Data class of power supply device"
    def __init__(self, mode: DrvEaModeE, status: DrvBaseStatusE,\
                 voltage: int, current: int, power: int) -> None:
        '''
        Args:
            - mode (DrvEaModeE|None): Mode of the device.
            - status (DrvBaseStatusC): Status of the device.
            - voltage (int): Voltage in mV.
            - current (int): Current in mA.
            - power (int): Power in mW.
        Raises:
            - None.
        '''
        self.mode: DrvEaModeE|None = mode
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
        self.__last_meas: DrvEaDataC = DrvEaDataC(mode = DrvEaModeE.STANDBY, \
                                                  status = DrvBaseStatusC(DrvBaseStatusE.OK), \
                                                  current = 0, voltage = 0, power = 0)

        self.__properties: DrvEaPropertiesC = DrvEaPropertiesC(model = '0', serial_number = 0,
                                                                max_volt_limit = 0, \
                                                                max_current_limit = 0, \
                                                                max_power_limit = 0)
        self.__wait_4_response = False
        self.__read_device_properties()
        self.__chan_two = False
        if '2384' in self.__properties.model:
            self.__chan_two = True

        if self.__chan_two:
            self.__last_meas_chan_two: DrvEaDataC = self.__last_meas

        self.__initialize_control()


    @property
    def properties(self) -> DrvEaPropertiesC:
        "Get the properties of the device."
        return self.__properties


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
                              payload = 'SYSTem:LOCK: ON')
        self.__tx_chan.send_data(msg)
        if self.__chan_two:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                  port = self.__port, \
                                  payload = 'SYSTem:LOCK: ON (@2)')
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
        exception = True
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
                self.__properties.model = msg[1]
                self.__properties.serial_number = int(msg[2])

        #Max current limit
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.CURR_NOM.value)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _CONSTANTS._MAX_WAIT_TIME:
            sleep(_CONSTANTS._TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0].split(' ')
                self.__properties.max_current_limit = int(float(msg[0]) * _CONSTANTS._MILI_UNITS)

        #Max voltage limit
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.VOLT_NOM.value)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _CONSTANTS._MAX_WAIT_TIME:
            sleep(_CONSTANTS._TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0].split(' ')
                self.__properties.max_volt_limit = int(float(msg[0]) * _CONSTANTS._MILI_UNITS)

        #Max power limit
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.POWER.value)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _CONSTANTS._MAX_WAIT_TIME:
            sleep(_CONSTANTS._TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0].split(' ')
                self.__properties.max_power_limit = int(float(msg[0]) * _CONSTANTS._MILI_UNITS)

        # self.__rx_chan.delete_until_last()
        # if exception:
        #     raise ConnectionError("Device not found")


    def get_data(self, channel: int) -> DrvEaDataC:
        '''Read the device data.
        Args:
            - None.
        Returns:
            - (DrvEaDataC): Returns the device data.
        Raises:
            - None.
        '''
        if channel == 1:
            mode = self.__last_meas.mode
        else:
            mode = self.__last_meas_chan_two.mode
        log.info(f"Get meas of channel {channel}")
        result: DrvEaDataC = DrvEaDataC(mode = mode, \
                                        status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR), \
                                        voltage = 0, current = 0, power = 0)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, \
                            port = self.__port, \
                            payload = f'MEASure:ARRay? (@{channel})')
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


    def get_meas_chan_one(self) -> DrvEaDataC:
        ''' Obtain the measurement of the channel 1 device.
        Args:
            - None.
        Returns:
            - (DrvEaDataC): Returns the device data.
        Raises:
            - None.
        '''
        self.__last_meas = self.get_data(channel = 1)
        return self.__last_meas


    def get_meas_chan_two(self) -> DrvEaDataC:
        ''' Obtain the measurement of the channel 2 device.
        Args:
            - None.
        Returns:
            - (DrvEaDataC): Returns the device data.
        Raises:
            - ValueError: The device doesn t have a channel 2.
        '''
        if self.__chan_two:
            self.__last_meas_chan_two = self.get_data(channel = 2)
            return self.__last_meas_chan_two
        else:
            log.error("Try to get meas of a channel that doesn´t exist")
            raise ValueError


    def set_cc_mode(self, curr_ref: int, voltage_limit: int, channel: int = 1) -> None:
        '''
        Use source in constant current mode.
        Sink mode will be set with negative current values.
        Security voltage limit can be also set.
        Args:
            - curr_ref (int): current consign (milli Amps)
            - voltage_limit (int): voltage limit (millivolts)
            - channel (int): channel to apply the mode
                    if the device has more than one, if not will always apply to the channel 1
        Returns:
            - None
        Raises:
            - None
        '''
        if channel == 1:
            self.__last_meas.mode = DrvEaModeE.CC_MODE
        else:
            self.__last_meas_chan_two.mode = DrvEaModeE.CC_MODE

        current = round(float(curr_ref) / _CONSTANTS._MILI_UNITS, 2)
        voltage = round(float(voltage_limit / _CONSTANTS._MILI_UNITS), 2)

        #Check if the power limit is exceeded
        if self.__properties.max_power_limit != 0:
            max_power_limit = self.__properties.max_power_limit / _CONSTANTS._MILI_UNITS
            if current * voltage > max_power_limit:
                voltage = max_power_limit / curr_ref
        else:
            current = 0
            voltage = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = f"CURRent {current} (@{channel})")
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = f"VOLTage {voltage} (@{channel})")
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = f'OUTPut ON (@{channel})')
        self.__tx_chan.send_data(msg)


    def set_cv_mode(self, volt_ref: int, current_limit: int, channel: int = 1) -> None:
        '''
        Use source in constant voltage mode .
        Security current limit can be also set for both sink and source modes. 
        It is recommended to set both!
        Args:
            - volt_ref (int): voltage consign (millivolts)
            - current_limit (int): current limit (milli Amps)
        Returns:
            - None
        Raises:
            - None
        '''
        if channel == 1:
            self.__last_meas.mode = DrvEaModeE.CV_MODE
        else:
            self.__last_meas_chan_two.mode = DrvEaModeE.CV_MODE
        voltage = round(float(volt_ref)/_CONSTANTS._MILI_UNITS, 2)
        current = round(float(current_limit/_CONSTANTS._MILI_UNITS), 2)
        #Check if the power limit is exceeded
        if self.__properties.max_power_limit != 0:
            max_power_limit = self.__properties.max_power_limit/_CONSTANTS._MILI_UNITS
            if voltage * current > max_power_limit:
                current = max_power_limit / volt_ref
        else:
            current = 0
            voltage = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = f"CURRent {current} (@{channel})")
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = f"VOLTage {voltage} (@{channel})")
        self.__tx_chan.send_data(msg)

        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = f'OUTPut ON (@{channel})')
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
                                payload = 'OUTPut: OFF')
        self.__tx_chan.send_data(msg)
        self.__last_meas.mode = DrvEaModeE.STANDBY
        if self.__chan_two:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = 'OUTPut: OFF (@2)')
            self.__tx_chan.send_data(msg)
            self.__last_meas_chan_two.mode = DrvEaModeE.STANDBY


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