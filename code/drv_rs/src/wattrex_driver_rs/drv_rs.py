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
from wattrex_driver_base import DrvBaseStatusE, DrvBaseStatusC, DrvBasePwrModeE , DrvBasePwrDeviceC, \
                                DrvBasePwrPropertiesC, DrvBasePwrDataC

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
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
    LOCK_ON = ':SYST:LOCK 1'
    LOCK_OFF = 'SYST:LOCK 0'
    DEVICE_ON = ':INP 1'
    DEVICE_OFF = ':INP 0'
    MAX_CURRENT =  ':CURRent:UPPer?'
    MAX_VOLTAGE = ':VOLTage:UPPer?'
    MAX_POWER = ':POWer:UPPer?'
    OUTPUT_ON = 'OUTPut ON'

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
        super().__init__(model = model, serial_number = serial_number, \
                         max_volt_limit = max_volt_limit, \
                         max_current_limit = max_current_limit, \
                         max_power_limit = max_power_limit)


class DrvRsDataC(DrvBasePwrDataC):
    "Data class of RS device"
    def __init__(self, mode: DrvBasePwrModeE, status: DrvBaseStatusE,\
                 voltage: int, current: int, power: int) -> None:
        '''
        Args:
            - mode (DrvEaModeE): Mode of the device.
            - status (DrvBaseStatusC): Status of the device.
            - voltage (int): Voltage in mV?????????. #TODO: Check units.
            - current (int): Current in mA?????????. #TODO: Check units.
            - power (int): Power in mW?????????. #TODO: Check units.
        Raises:
            - None.
        '''
        super().__init__(status = status, mode = mode, voltage = voltage, \
                         current = current, power = power)


class DrvRsDeviceC(DrvBasePwrDeviceC):
    "Principal class of RS device"
    def __init__(self, config: DrvScpiSerialConfC, rx_chan_name: str) -> None:
        '''
        Args:
            - config (DrvScpiSerialConfC): Configuration of the serial port.
            - rx_chan_name (str): Name of the channel to receive the messages.
        Raises:
            - None.
        '''
        self.__tx_chan = SysShdIpcChanC(name = _TX_CHAN_NAME)
        self.__rx_chan = SysShdIpcChanC(name = rx_chan_name,
                                      max_msg = _MAX_MSG,
                                      max_message_size = _MAX_MESSAGE_SIZE)
        self.__port = config.port
        self.__wait_4_response = False #TODO: It not used. Check if it is necessary.
        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV, \
                                  port = config.port, \
                                  payload = config, \
                                  rx_chan_name = rx_chan_name)
        self.__tx_chan.send_data(add_msg)
        self.__rx_chan.delete_until_last()
        self.properties: DrvRsPropertiesC = DrvRsPropertiesC(model = '', serial_number = 0,
                                                             max_volt_limit = 0, \
                                                             max_current_limit = 0, \
                                                             max_power_limit = 0)
        self.last_data: DrvRsDataC = DrvRsDataC(mode = DrvBasePwrModeE.WAIT, \
                                                status = DrvBaseStatusC(DrvBaseStatusE.OK), \
                                                voltage = 0, current = 0, power = 0)
        self.__initialize_control()
        self.__read_device_properties()


    def __initialize_control(self) -> None:
        ''' Initialize the control of the device.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        #disable manual inputs
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                              port = self.__port, \
                              payload = _ScpiCmds.LOCK_ON.value)
        self.__tx_chan.send_data(msg)
        #disable power input
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                              port = self.__port, \
                              payload = _ScpiCmds.DEVICE_OFF.value)
        self.__tx_chan.send_data(msg)
        self.disable()

    def __read_device_properties(self) -> None:
        ''' Read the properties of the device.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        log.info("Getting device properties...")
        #Model and serial number
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, \
                              port = self.__port, \
                              payload = _ScpiCmds.READ_INFO.value)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _MAX_WAIT_TIME:
            sleep(_TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                msg = command_rec.payload[0]
                msg = msg.split(' ')
                self.properties.model = msg[0]
                self.properties.serial_number = msg[2].replace('SN:', '')
        #Max current, voltage and power limit
        self.properties.max_current = self.__read_meas(_ScpiCmds.MAX_CURRENT.value)
        self.properties.max_volt = self.__read_meas(_ScpiCmds.MAX_VOLTAGE.value)
        self.properties.max_power = self.__read_meas(_ScpiCmds.MAX_POWER.value)


    def __read_meas(self, payload: str) -> int:
        ''' Get the measurements of the device.
        Args:
            - payload (str): Payload of the message.
        Returns:
            - result (int): Measurement.
        Raises:
            - None.
        '''
        result = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, \
                              port = self.__port, \
                              payload = payload)
        self.__tx_chan.send_data(msg)
        # Wait until receive the message
        time_init = time()
        while (time() - time_init) < _MAX_WAIT_TIME:
            sleep(_TIME_BETWEEN_ATTEMPTS)
            if not self.__rx_chan.is_empty():
                command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
                meas = command_rec.payload[0][:-1]
                result = int(float(meas) * _MILI_UNITS)
        return result


    def get_data(self) -> DrvRsDataC:
        ''' Get the data of the device.
        Args:
            - None
        Returns:
            - result (DrvRsDataC): Data of the device.
        Raises:
            - None
        '''
        log.info("Getting datas...")
        result: DrvRsDataC = DrvRsDataC(mode = self.last_data.mode, \
                                        status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR), \
                                        voltage = 0, current = 0, power = 0)
        result.current = self.__read_meas(payload=':MEASure:CURRent?')
        result.voltage = self.__read_meas(payload=':MEASure:VOLTage?')
        result.power = self.__read_meas(payload=':MEASure:POWer?')
        result.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        self.last_data = result
        return self.last_data


    def set_cv_mode(self, volt_ref: int) -> None:
        ''' Set the device in CV mode.
        Args:
            - volt_ref (int): Voltage reference in milivolts.
        Returns:
            - None
        Raises:
            - None
        '''
        log.info("Set CV mode...")
        if volt_ref > self.properties.max_volt:
            volt_ref = self.properties.max_volt
        voltage = float(volt_ref / _MILI_UNITS)
        if voltage > 0.0:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = f':VOLT {round(voltage, 4)}V')
            self.__tx_chan.send_data(msg)
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = _ScpiCmds.OUTPUT_ON.value)
            self.__tx_chan.send_data(msg)
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = _ScpiCmds.DEVICE_ON.value)
            self.__tx_chan.send_data(msg)
            self.last_data.mode = DrvBasePwrModeE.CV_MODE
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        else:
            self.disable()
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.INTERNAL_ERROR)


    def set_cc_mode(self, curr_ref: int) -> None:
        ''' Set the device in CC mode.
        Args:
            - curr_ref (int): Current reference.
        Returns:
            - None
        Raises:
            - None
        '''
        log.info("Set CC mode...")
        if curr_ref > self.properties.max_current:
            curr_ref = self.properties.max_current
        current = float(curr_ref / _MILI_UNITS)

        if current > 0.0:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = f':CURR {round(current, 4)}A')
            self.__tx_chan.send_data(msg)
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = _ScpiCmds.OUTPUT_ON.value)
            self.__tx_chan.send_data(msg)
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                    port = self.__port, \
                                    payload = _ScpiCmds.DEVICE_ON.value)
            self.__tx_chan.send_data(msg)
            self.last_data.mode = DrvBasePwrModeE.CC_MODE
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        else:
            self.disable()
            self.last_data.status = DrvBaseStatusC(DrvBaseStatusE.INTERNAL_ERROR)


    def disable(self) -> None:
        ''' Disable power input.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                port = self.__port, \
                                payload = _ScpiCmds.DEVICE_OFF.value)
        self.__tx_chan.send_data(msg)
        self.last_data.mode = DrvBasePwrModeE.WAIT


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
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, \
                                port = self.__port, \
                                payload = _ScpiCmds.LOCK_OFF.value)
        self.__tx_chan.send_data(msg)
        self.__rx_chan.terminate()
