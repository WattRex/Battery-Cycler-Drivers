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
from time import sleep

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
log = sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC, DrvScpiCmdTypeE
from wattrex_driver_base import (DrvBaseStatusE, DrvBaseStatusC, DrvBasePwrModeE, DrvBasePwrDeviceC,
                                DrvBasePwrPropertiesC, DrvBasePwrDataC)

#######################          MODULE IMPORTS          #######################
######################             CONSTANTS              ######################
from .context import (DEFAULT_TX_CHAN, DEFAULT_RX_CHAN, DEFAULT_MAX_MSG, DEFAULT_MAX_MESSAGE_SIZE,
                      DEFAULT_MAX_READS)
#######################              ENUMS               #######################
_MILI_UNITS = 1000


class _ScpiCmds(Enum):
    "Modes of the device"
    READ_INFO = '*IDN?'
    GET_MEAS  = 'MEASure:ARRay?'
    GET_OUTPUT = 'OUTPut?'
    CURR_NOM  = 'SYSTem:NOMinal:CURRent?'
    VOLT_NOM  = 'SYSTem:NOMinal:VOLTage?'
    POWER = 'SYSTem:NOMinal:POWer?'
    LOCK_ON = 'SYSTem:LOCK: ON'
    LOCK_OFF = 'SYSTem:LOCK: OFF'
    OUTPUT_ON = 'OUTPut: ON'
    OUTPUT_OFF = 'OUTPut: OFF'
    SEND_CURR = 'CURRent '
    SEND_VOLT = 'VOLTage '


#######################             CLASSES              #######################
class DrvEaPropertiesC(DrvBasePwrPropertiesC):
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
        super().__init__(model = model, serial_number = str(serial_number),
                         max_volt_limit = max_volt_limit,
                         max_current_limit = max_current_limit,
                         max_power_limit = max_power_limit)


class DrvEaDataC(DrvBasePwrDataC):
    "Data class of power supply device"
    def __init__(self, mode: DrvBasePwrModeE, status: DrvBaseStatusE,
                 voltage: int, current: int, power: int) -> None:
        '''
        Args:
            - mode (DrvBasePwrModeE): Mode of the device.
            - status (DrvBaseStatusC): Status of the device.
            - voltage (int): Voltage in mV.
            - current (int): Current in mA.
            - power (int): Power in mW.
        Raises:
            - None.
        '''
        stat: DrvBaseStatusC = DrvBaseStatusC(status)
        super().__init__(status = stat, mode = mode, voltage = voltage,
                         current = current, power = power)


class DrvEaDeviceC(DrvBasePwrDeviceC):
    "Principal class of ea power supply device"
    __instances = []

    def __change_last_mode(self, mode: DrvBasePwrModeE) -> None:
        ''' Change the last mode of the device.
        Args:
            - mode (DrvBasePwrModeE): Mode of the device.
        '''
        for i in DrvEaDeviceC.__instances:
            for j in DrvEaDeviceC.__instances:
                if i.__port == j.__port:
                    i.__last_mode = mode                    
                    j.__last_mode = mode
                    break
            

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
        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                  port = config.port,
                                  payload = config,
                                  rx_chan_name = DEFAULT_RX_CHAN+'_'+config.port.split('/')[-1])
        self.__tx_chan.send_data(add_msg)
        self.__rx_chan.delete_until_last()
        self.__wait_4_response: bool = False
        self.__last_mode: DrvBasePwrModeE = DrvBasePwrModeE.DISABLE
        self.last_data: DrvEaDataC = DrvEaDataC(mode = DrvBasePwrModeE.DISABLE,
                                                status = DrvBaseStatusE.OK,
                                                current = 0, voltage = 0, power = 0)

        self.properties: DrvEaPropertiesC = DrvEaPropertiesC(model = None, serial_number = 0,
                                                                max_volt_limit = 0,
                                                                max_current_limit = 0,
                                                                max_power_limit = 0)
        self.__read_device_properties()
        self.__initialize_control()
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
            raise ConnectionError("Device not found")
        DrvEaDeviceC.__instances.append(self)

    def read_buffer(self) -> None: #pylint: disable=too-many-branches, too-many-statements
        """
        Reads data from the receive channel and updates the device properties and last data.

        Returns:
            None
        """
        i = 0
        while i < DEFAULT_MAX_READS and not self.__rx_chan.is_empty(): #pylint: disable=too-many-nested-blocks
            msg: DrvScpiCmdDataC = self.__rx_chan.receive_data_unblocking()
            if msg is not None and msg.data_type == DrvScpiCmdTypeE.RESP: #pylint: disable=too-many-nested-blocks
                if hasattr(msg, 'status') and msg.status.value == DrvBaseStatusE.COMM_ERROR: #pylint: disable=attribute-defined-outside-init
                    log.critical("ERROR READING DEVICE")
                    self.last_data.status = DrvBaseStatusE.COMM_ERROR #pylint: disable=attribute-defined-outside-init
                for data in msg.payload: #pylint: disable=too-many-nested-blocks #pylint: disable=attribute-defined-outside-init
                    if len(data) >0 and not str(data).startswith(":"):
                        if 'No error' in data:
                            self.last_data.status = DrvBaseStatusE.OK #pylint: disable=attribute-defined-outside-init
                        elif all (x in data for x in ("error", "Error", "ERROR")):
                            self.last_data.status = DrvBaseStatusE.COMM_ERROR #pylint: disable=attribute-defined-outside-init
                        elif 'OFF' in data:
                            self.last_data.mode = self.__last_mode #pylint: disable=attribute-defined-outside-init
                        elif ('ON' in data and
                              (self.last_data.mode == DrvBasePwrModeE.WAIT or
                               self.last_data.mode == DrvBasePwrModeE.DISABLE)):
                            self.last_data.mode = self.__last_mode #pylint: disable=attribute-defined-outside-init
                        elif data.startswith('EA'):
                            data = data.split(',')
                            self.properties.model = data[1] #pylint: disable=attribute-defined-outside-init
                            self.properties.serial_number = data[2] #pylint: disable=attribute-defined-outside-init
                            log.debug(f"Serial number: {data[2]}")
                            log.debug(f"Model: {data[1]}")
                        elif all(x in data for x in ("V,", "A,", "W")):
                            meas_data = data.split(',')
                            voltage = int(float(meas_data[0].replace('V', '')) * _MILI_UNITS)
                            self.last_data.voltage = voltage #pylint: disable=attribute-defined-outside-init
                            current = int(float(meas_data[1].replace('A', '')) * _MILI_UNITS)
                            self.last_data.current = current #pylint: disable=attribute-defined-outside-init
                            power = int(float(meas_data[2].replace('W', '')) * _MILI_UNITS)
                            self.last_data.power = power #pylint: disable=attribute-defined-outside-init
                            log.debug(f"Power: {power} mW, last mode: {self.__last_mode}")
                            if ((power > 0 or (voltage > 0 and current > 0))
                                and self.__last_mode != DrvBasePwrModeE.DISABLE):
                                self.last_data.mode = self.__last_mode #pylint: disable=attribute-defined-outside-init
                            else:
                                if self.__last_mode == DrvBasePwrModeE.WAIT:
                                    self.last_data.mode = DrvBasePwrModeE.WAIT #pylint: disable=attribute-defined-outside-init
                                else:
                                    self.last_data.mode = DrvBasePwrModeE.DISABLE #pylint: disable=attribute-defined-outside-init
                            self.__wait_4_response = False
                        elif "W" in data and len(data.split(' ')) == 2:
                            max_power = int(float(data.split(' ')[0]) * _MILI_UNITS)
                            self.properties.max_power_limit = max_power #pylint: disable=attribute-defined-outside-init
                        elif "V" in data and len(data.split(' ')) == 2:
                            max_volt = int(float(data.split(' ')[0]) * _MILI_UNITS)
                            self.properties.max_volt_limit = max_volt #pylint: disable=attribute-defined-outside-init
                        elif "A" in data and len(data.split(' ')) == 2:
                            max_curr = int(float(data.split(' ')[0]) * _MILI_UNITS)
                            self.properties.max_current_limit = max_curr #pylint: disable=attribute-defined-outside-init
                        log.debug(f"Response: {data}")
            elif msg is None:
                pass
            else:
                log.error(f'Unknown message type received: {msg.__dict__}')
            i += 1

    def __initialize_control(self) -> None:
        ''' Initialize the device.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                              port = self.__port,
                              payload = _ScpiCmds.LOCK_ON.value)
        self.__tx_chan.send_data(msg)
        self.read_buffer()
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
        self.read_buffer()
        #Max current limit
        self.__get_nominal_value(_ScpiCmds.CURR_NOM.value)
        #Max voltage limit
        self.__get_nominal_value(_ScpiCmds.VOLT_NOM.value)
        #Max power limit
        self.__get_nominal_value(_ScpiCmds.POWER.value)
        self.read_buffer()


    def __get_nominal_value(self, payload: str) -> None:
        ''' Get nominal value.
        Args:
            - payload (str): Payload of the message.
        Returns:
            - result (int): Nominal value.
        Raises:
            - None.
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = payload)
        self.__tx_chan.send_data(msg)
        # Try to read message
        self.read_buffer()

    def get_data(self) -> DrvEaDataC:
        '''Read the device data.
        Args:
            - None.
        Returns:
            - result (DrvEaDataC): Returns the device data.
        Raises:
            - None.
        '''
        log.debug("Get meas...")
        if not self.__wait_4_response:
            self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port = self.__port,
                                payload = _ScpiCmds.GET_MEAS.value))
            self.__wait_4_response = True
        self.read_buffer()
        return self.last_data


    def set_cc_mode(self, curr_ref: int, voltage_limit: int|None= None) -> None:
        '''
        Use source in constant current mode.
        Sink mode will be set with negative current values.
        Security voltage limit can be also set.
        Args:
            - curr_ref (int): current reference (mili Amps)
            - voltage_limit (int): voltage limit (milivolts)
                if None, the maximum voltage limit will be used.
        Returns:
            - None
        Raises:
            - None
        '''
        self.__change_last_mode(DrvBasePwrModeE.CC_MODE)
        current = round(float(curr_ref) / _MILI_UNITS, 2)
        if current > self.properties.max_current_limit:
            current = self.properties.max_current_limit
        if voltage_limit is None or voltage_limit > self.properties.max_volt_limit:
            voltage_limit = self.properties.max_volt_limit
        voltage = round(float(voltage_limit / _MILI_UNITS), 2)

        #Check if the power limit is exceeded
        if self.properties.max_power_limit != 0:
            max_power_limit = self.properties.max_power_limit / _MILI_UNITS
            if current * voltage > max_power_limit:
                voltage = max_power_limit / curr_ref
        else:
            current = 0
            voltage = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_CURR.value + str(current))
        self.__tx_chan.send_data(msg)
        self.read_buffer()
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_VOLT.value + str(voltage))
        self.__tx_chan.send_data(msg)
        self.read_buffer()
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.OUTPUT_ON.value)
        self.__tx_chan.send_data(msg)
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.GET_OUTPUT.value)
        self.__tx_chan.send_data(msg)
        self.read_buffer()


    def set_cv_mode(self, volt_ref: int, current_limit: int|None= None) -> None:
        '''
        Use source in constant voltage mode .
        Security current limit can be also set for both sink and source modes. 
        It is recommended to set both!
        Args:
            - volt_ref (int): voltage reference (milivolts)
            - current_limit (int): current limit (mili Amps),
                if None the maximum current limit will be used.
        Returns:
            - None
        Raises:
            - None
        '''
        self.__change_last_mode(DrvBasePwrModeE.CV_MODE)
        voltage = round(float(volt_ref)/_MILI_UNITS, 2)
        current = round(float(current_limit/_MILI_UNITS), 2)
        #Check if the power limit is exceeded
        if self.properties.max_power_limit != 0:
            max_power_limit = self.properties.max_power_limit/_MILI_UNITS
            if voltage * current > max_power_limit:
                current = max_power_limit / volt_ref
        elif current > self.properties.max_current_limit:
            current = self.properties.max_current_limit
        elif voltage > self.properties.max_volt_limit:
            voltage = self.properties.max_volt_limit
        else:
            current = 0
            voltage = 0
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_CURR.value + str(current))
        self.__tx_chan.send_data(msg)
        self.read_buffer()
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.SEND_VOLT.value + str(voltage))
        self.__tx_chan.send_data(msg)
        self.read_buffer()
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                port = self.__port, payload = _ScpiCmds.OUTPUT_ON.value)
        self.__tx_chan.send_data(msg)
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port, payload = _ScpiCmds.GET_OUTPUT.value)
        self.__tx_chan.send_data(msg)
        self.read_buffer()

    def set_wait_mode(self) -> None:
        ''' Set the device in standby mode.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None 
        '''
        log.critical("Disabling SOURCE...")
        self.__change_last_mode(DrvBasePwrModeE.WAIT)
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                port = self.__port,
                                payload = _ScpiCmds.OUTPUT_OFF.value)
        self.__tx_chan.send_data(msg)
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port = self.__port,
                                payload = _ScpiCmds.GET_OUTPUT.value))

    def disable(self) -> None:
        ''' Set the device in standby mode.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None 
        '''
        log.critical("Disabling SOURCE...")
        self.__change_last_mode(DrvBasePwrModeE.DISABLE)
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                port = self.__port,
                                payload = _ScpiCmds.OUTPUT_OFF.value)
        self.__tx_chan.send_data(msg)
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port = self.__port,
                                payload = _ScpiCmds.GET_OUTPUT.value))


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
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                                                 port = self.__port,
                                                 payload = _ScpiCmds.LOCK_OFF.value))
        del_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                  port = self.__port) # pylint: disable=no-member
        self.__tx_chan.send_data(del_msg)
        self.__tx_chan.close()
        self.read_buffer()
        self.__rx_chan.terminate()
