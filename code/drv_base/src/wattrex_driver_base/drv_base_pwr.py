#!/usr/bin/python3
'''
Create a base class used to register devices status.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum
#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
from .drv_base_status import DrvBaseStatusC, DrvBaseStatusE

#######################              ENUMS               #######################
class DrvBasePwrModeE(Enum):
    '''
    Working modes of power devices.
    '''
    DISABLE = 5
    WAIT = 0
    CC_MODE = 1
    CV_MODE = 2
    CP_MODE = 3
    CR_MODE = 4

#######################             CLASSES              #######################

class DrvBasePwrDataC:
    '''
    The data of a power device.
    '''

    def __init__(self, status : DrvBaseStatusC = DrvBaseStatusE.OK,\
            mode : DrvBasePwrModeE = DrvBasePwrModeE.DISABLE, voltage : int = 0,\
            current : int = 0, power : int = 0) -> None:
        '''
        Intialize power data object .

        Args:
            status (DrvBaseStatusC, optional): Device status.
                Defaults to DrvBaseStatusE.OK.
            mode (DrvBasePwrModeE, optional): Device working mode.
                Defaults to DrvBasePwrModeE.DISABLE.
            voltage (int, optional): Measured voltage. Defaults to 0.
            current (int, optional): Measured current. Defaults to 0.
            power (int, optional): Measured power. Defaults to 0.
        '''
        self.status = status
        self.mode = mode
        self.voltage = voltage
        self.current = current
        self.power = power

class DrvBasePwrPropertiesC:
    '''
    Properties of a power device.
    '''

    def __init__(self, model : str = None, serial_number : str = None, max_volt_limit : int = 0,\
                max_current_limit : int = 0, max_power_limit : int = 0) -> None:
        '''
        Intialize properties object .

        Args:
            model (str, optional): device model. Defaults to None.
            serial_number (str, optional): device serial number. Defaults to None.
            max_volt_limit (int, optional): device max. voltage supported. Defaults to 0.
            max_current_limit (int, optional): device max. current supported. Defaults to 0.
            max_power_limit (int, optional): device max. power supported. Defaults to 0.
        '''
        self.model = model
        self.serial_number = serial_number
        self.max_volt_limit = max_volt_limit
        self.max_current_limit = max_current_limit
        self.max_power_limit = max_power_limit

class DrvBasePwrDeviceC:
    '''
    Base handler used to manage a power device.
    '''

    def __init__(self) -> None:
        '''
        Initialize the interface of a handler class used to manager a power device.
        '''
        self.properties = DrvBasePwrPropertiesC()
        self.last_data = DrvBasePwrDataC()

    def get_data(self) -> DrvBasePwrDataC:
        '''
        Get the last measured data of the device.

        Returns:
            DrvBasePwrDataC: device data
        '''
        return self.last_data

    def get_properties(self) -> DrvBasePwrPropertiesC:
        '''
        Returns the device propertie.

        Returns:
            DrvBasePwrPropertiesC: device property
        '''
        return self.properties

    def close(self) -> None:
        '''
        Close the connection.
        '''
