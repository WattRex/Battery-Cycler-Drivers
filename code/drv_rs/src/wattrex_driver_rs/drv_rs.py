#!/usr/bin/python3
'''
Driver of RS.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################
from enum import Enum

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiHandlerC
from wattrex_driver_pwr import DrvPwrPropertiesC, DrvPwrStatusC, DrvPwrStatusE,\
        DrvPwrDataC, DrvPwrDeviceC

#######################          MODULE IMPORTS          #######################


#######################              ENUMS               #######################
class _CONSTANTS:
    MILI_UNITS = 1000

class DrvRsModeE(Enum):
    "Driver modes"
    WAIT = 0
    CV_MODE = 1
    CC_MODE = 2
    CR_MODE = 3
    CP_MODE = 4

#######################             CLASSES              #######################
class DrvRsPropertiesC(DrvPwrPropertiesC):
    "Properties of RS device"
    def __init__(self, model: str|None = None, serial_number: str|None = None,
                 MAX_VOLT: int = 0, MAX_CURR: int = 0,
                 MAX_PWR: int = 0) -> None:
        super().__init__(model, serial_number, MAX_VOLT, MAX_CURR, MAX_PWR)


class DrvRsDataC(DrvPwrDataC):
    "Data class of RS device"
    def __init__(self, mode: DrvRsModeE, status: DrvPwrStatusC, \
                 voltage: int, current: int, power: int) -> None:
        super().__init__(status = status, mode = mode, voltage = voltage, \
                         current = current, power = power)
        self.mode: DrvRsModeE = mode


class DrvRsDeviceC(DrvPwrDeviceC):
    "Principal class of RS device"
    def __init__(self, handler: DrvScpiHandlerC) -> None:

        self.device_handler: DrvScpiHandlerC
        super().__init__(handler = handler)
        self.__actual_data: DrvRsDataC = DrvRsDataC(mode = DrvRsModeE.WAIT, \
                                                     status = DrvPwrStatusC(DrvPwrStatusE.OK), \
                                                     voltage = 0, current = 0, power = 0)

        self.__properties: DrvRsPropertiesC = DrvRsPropertiesC(model            = None, \
                                                               serial_number    = None, \
                                                               MAX_VOLT   = 0, \
                                                               MAX_CURR= 0, \
                                                               MAX_PWR  = 0)
        self.__initialize_control()
        self.__read_device_properties()


    def __initialize_control(self) -> None:
        ''' Initialize the control of the device.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        #disable manual inputs
        self.device_handler.send_msg(':SYST:LOCK 1')
        #disable power input
        self.device_handler.send_msg(':INP 0')


    def __read_device_properties(self) -> None:
        ''' Read the properties of the device.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        model: str|None = None
        serial_number: str|None = None
        max_current_limit: float = 0
        max_voltage_limit: float = 0
        max_power_limit: float = 0
        #Model and serial number
        info = self.device_handler.read_device_info()[0]
        if info is not None:
            info = info.split(' ')
            model = info[0]
            serial_number = info[2].replace('SN:', '')
        #Max current limit
        read_curr = self.device_handler.send_and_read(':CURRent:UPPer?')[0]
        if read_curr is not None:
            max_current_limit = self.device_handler.decode_numbers(read_curr)
            max_current_limit = int(max_current_limit * _CONSTANTS.MILI_UNITS)
        #Max voltage limit
        read_volt = self.device_handler.send_and_read(':VOLTage:UPPer?')[0]
        if read_volt is not None:
            max_voltage_limit = self.device_handler.decode_numbers(read_volt)
            max_voltage_limit = int(max_voltage_limit * _CONSTANTS.MILI_UNITS)
        #Max power limit
        read_power = self.device_handler.send_and_read(':POWer:UPPer?')[0]
        if read_power is not None:
            max_power_limit = self.device_handler.decode_numbers(read_power)
            max_power_limit = int(max_power_limit * _CONSTANTS.MILI_UNITS)

        self.__properties = DrvRsPropertiesC(model = model, serial_number = serial_number, \
                                                MAX_VOLT = max_voltage_limit, \
                                                MAX_CURR = max_current_limit, \
                                                MAX_PWR = max_power_limit)

    def set_cv_mode(self, volt_ref: int) -> None:
        ''' Set the device in CV mode.
        Args:
            - volt_ref (int): Voltage reference.
        Returns:
            - None
        Raises:
            - None
        '''
        if volt_ref > self.__properties.max_volt_limit:
            volt_ref = self.__properties.max_volt_limit
        voltage = float(volt_ref / _CONSTANTS.MILI_UNITS)

        if voltage > 0.0:
            self.device_handler.send_msg(f':VOLT {round(voltage, 4)}V')
            self.device_handler.send_msg('OUTPut ON')
            self.device_handler.send_msg(':INP 1')
            self.__actual_data.mode = DrvRsModeE.CV_MODE
            self.__actual_data.status = DrvPwrStatusC(DrvPwrStatusE.OK)

        else:
            self.disable()
            self.__actual_data.mode = DrvRsModeE.WAIT
            self.__actual_data.status = DrvPwrStatusC(DrvPwrStatusE.INTERNAL_ERROR)


    def set_cc_mode(self, curr_ref: int) -> None:
        ''' Set the device in CC mode.
        Args:
            - curr_ref (int): Current reference.
        Returns:
            - None
        Raises:
            - None
        '''
        if curr_ref > self.__properties.max_current_limit:
            curr_ref = self.__properties.max_current_limit
        current = float(curr_ref / _CONSTANTS.MILI_UNITS)

        if current > 0.0:
            self.device_handler.send_msg(f':CURR {round(current, 4)}A')
            self.device_handler.send_msg('OUTPut ON')
            self.device_handler.send_msg(':INP 1')
            self.__actual_data.mode = DrvRsModeE.CC_MODE
        # pylint: disable=fixme
        # TODO: Se podría leer la corriente y ver que es igual a la enviada, \
        # en vez de poner CC_MODE directamente
            self.__actual_data.status = DrvPwrStatusC(DrvPwrStatusE.OK)

        else:
            self.disable()
            self.__actual_data.mode = DrvRsModeE.WAIT
            self.__actual_data.status = DrvPwrStatusC(DrvPwrStatusE.INTERNAL_ERROR)


    def disable(self) -> None:
        ''' Disable power input.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        self.device_handler.send_msg('OUTPut OFF')
        self.device_handler.send_msg(':INP 0')


    def get_data(self) -> DrvRsDataC:
        ''' Get the data of the device.
        Args:
            - None
        Returns:
            - DrvRsDataC: Data of the device.
        Raises:
            - None
        '''
        current = 0
        voltage = 0
        power = 0
        status = DrvPwrStatusC(DrvPwrStatusE.COMM_ERROR)

        #Get current
        read_curr = self.device_handler.send_and_read(':MEASure:CURRent?')[0]
        if read_curr is not None:
            current = self.device_handler.decode_numbers(read_curr)
            self.__actual_data.current = int(current * _CONSTANTS.MILI_UNITS)
        #Get voltage
        read_volt = self.device_handler.send_and_read(':MEASure:VOLTage?')[0]
        if read_volt is not None:
            voltage = self.device_handler.decode_numbers(read_volt)
            self.__actual_data.voltage = int(voltage * _CONSTANTS.MILI_UNITS)
        #Get power
        read_power = self.device_handler.send_and_read(':MEASure:POWer?')[0]
        if read_power is not None:
            power = self.device_handler.decode_numbers(read_power)
            self.__actual_data.power = int(power * _CONSTANTS.MILI_UNITS)
        #Get status
        if current is not None and voltage is not None and power is not None:
            status = DrvPwrStatusC(DrvPwrStatusE.OK)
        self.__actual_data.status = status

        return self.__actual_data


    def get_properties(self) -> DrvRsPropertiesC:
        ''' Get the properties of the device.
        Args:
            - None
        Returns:
            - DrvRsPropertiesC: Properties of the device.
        Raises:
            - None
        '''
        return self.__properties


    def close(self) -> None:
        ''' Deactivates the load and closes the serial port.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        self.disable()
        self.device_handler.send_msg(':SYST:LOCK 0\n')
        self.device_handler.close()
