#!/usr/bin/python3
'''
Driver of multimeter.
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
from wattrex_driver_pwr import DrvPwrPropertiesC, DrvPwrDataC, DrvPwrStatusC,\
        DrvPwrStatusE, DrvPwrDeviceC

#######################          MODULE IMPORTS          #######################


#######################              ENUMS               #######################
class _CONST():
    MILI_UNITS = 1000
    MAX_VOLT = 1000 #V
    MAX_CURR = 20 #A
    MAX_PWR = MAX_CURR * MAX_VOLT #W

class DrvBkModeE(Enum):
    "Modes of the device"
    VOLT_AUTO           = 'VOLT:DC:RANGE:AUTO ON'
    VOLT_R200_MILI_V    = 'VOLT:DC:RANGE 0.2'
    VOLT_R2_V           = 'VOLT:DC:RANGE 2'
    VOLT_R20_V          = 'VOLT:DC:RANGE 20'
    VOLT_R200_V         = 'VOLT:DC:RANGE 200'
    VOLT_R1000_V        = 'VOLT:DC:RANGE 1000'
    CURR_AUTO           = 'CURR:DC:RANGE:AUTO ON'
    CURR_R2_MILI_A      = 'CURR:DC:RANGE 0.002'
    CURR_R20_MILI_A     = 'CURR:DC:RANGE 0.02'
    CURR_R200_MILI_A    = 'CURR:DC:RANGE 0.2'
    CURR_R2_A           = 'CURR:DC:RANGE 2'
    CURR_R20_A          = 'CURR:DC:RANGE 20'

class _DrvBkIntegrationRateE(Enum):
    "Integration rate of the device"
    SLOW = '10'
    MEDIUM = '1'
    FAST = '0.1'


#######################             CLASSES              #######################
class DrvBkPropertiesC(DrvPwrPropertiesC):
    "Properties of bk device"
    def __init__(self, model: str|None = None, serial_number: str|None = None,
                 MAX_VOLT: int = 0, MAX_CURR: int = 0,
                 MAX_PWR: int = 0) -> None:
        super().__init__(model, serial_number, MAX_VOLT, MAX_CURR, MAX_PWR)


class DrvBkDataC(DrvPwrDataC):
    "Data class of bk device"
    def __init__(self, mode: DrvBkModeE, status: DrvPwrStatusC, \
                 voltage: int, current: int, power: int) -> None:
        super().__init__(status = status, mode = mode, voltage = voltage, \
                         current = current, power = power)


class DrvBkDeviceC(DrvPwrDeviceC):
    "Principal class of bk device"
    def __init__(self, handler: DrvScpiHandlerC) -> None:
        self.device_handler: DrvScpiHandlerC
        super().__init__(handler = handler)
        self.__actual_data: DrvBkDataC = DrvBkDataC(mode = DrvBkModeE.VOLT_AUTO, \
                                                     status = DrvPwrStatusC(DrvPwrStatusE.OK), \
                                                     voltage = 0, current = 0, power = 0)

        self.__properties: DrvBkPropertiesC = DrvBkPropertiesC(model            = None, \
                                                               serial_number    = None, \
                                                               MAX_VOLT   = 0, \
                                                               MAX_CURR= 0, \
                                                               MAX_PWR  = 0)
        self.__initialize_control()
        self.__read_device_properties()


    def __initialize_control(self) -> None:
        '''Initialize the device control.
        Args:
            - None.
        Returns:    
            - None.
        Raises:
            - None.
        '''
        #Initialize device speed
        self.device_handler.send_and_read('VOLT:DC:NPLC '+ _DrvBkIntegrationRateE.MEDIUM.value)
        #Initialize device mode in auto voltage
        self.device_handler.send_and_read(DrvBkModeE.VOLT_AUTO.value)


    def __read_device_properties(self) -> None:
        '''Read the device properties .
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        # info = self.device_handler.read_device_info()
        # info = info[1].split()
        self.device_handler.send_and_read('*IDN?')
        info = self.device_handler.receive_msg()[0]
        info = info.split(',')

        if info is not None:
            model = info[0]
            serial_number = info[-1]
        else:
            model = None
            serial_number = None
        self.__properties = DrvBkPropertiesC(model = model, \
                                             serial_number = serial_number, \
                                             MAX_VOLT = _CONST.MAX_VOLT * _CONST.MILI_UNITS,\
                                             MAX_CURR = _CONST.MAX_CURR * _CONST.MILI_UNITS,\
                                             MAX_PWR = _CONST.MAX_PWR * _CONST.MILI_UNITS)


    def set_mode(self, meas_mode: DrvBkModeE) -> None:
        '''Set the device mode.
        Args:
            - meas_mode (DrvBkModeE): Mode to set.
        Returns:
            - None.
        Raises:
            - None.
        '''
        mode_cod = meas_mode.value.split(':')[0]+':' + meas_mode.value.split(':')[1]
        #Change mode to voltage or current
        self.device_handler.send_and_read('FUNC '+ mode_cod)
        #Change range of the mode
        self.device_handler.send_and_read(meas_mode.value)
        self.__actual_data.mode = meas_mode


    def get_data(self) -> DrvBkDataC:
        '''Read the device measures.
        Args:
            - None.
        Returns:
            - (DrvBkDataC): Returns the device measures.
        Raises:
            - None
        '''
        current = 0
        voltage = 0
        status = DrvPwrStatusC(DrvPwrStatusE.COMM_ERROR)
        #Read measure
        self.device_handler.send_and_read('FETC?')
        response = self.device_handler.receive_msg()[0]
        if response != '':
            response = self.device_handler.decode_numbers(response)
            response = int(response * _CONST.MILI_UNITS)
            status = DrvPwrStatusC(DrvPwrStatusE.OK)

            if self.__actual_data.mode.value.split(':')[0] == 'VOLT':
                voltage = response
            elif self.__actual_data.mode.value.split(':')[0] == 'CURR':
                current = response
        else:
            status = DrvPwrStatusC(DrvPwrStatusE.COMM_ERROR)

        self.__actual_data = DrvBkDataC(mode = self.__actual_data.mode, status = status,\
                                        voltage = voltage, current = current, power = 0)
        return self.__actual_data


    def get_properties(self) -> DrvBkPropertiesC:
        '''Read the device properties.
        Args:
            - None.
        Returns:
            - (DrvBkPropertiesC): Returns the device properties.
        Raises:
            - None.
        '''
        return self.__properties


    def close(self) -> None:
        '''Close communication with the device.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        self.device_handler.close()
