#!/usr/bin/python3
"""
This module contains all the classes needed to instantiate a epc device and process data from and to
it.
"""
# TODO: Reorganize code to have a smaller file
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum
#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################
from bitarray.util import int2ba

#######################          MODULE IMPORTS          #######################

#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################
class DrvEpcLimitE(Enum):
    """
    Type of limit imposed to the epc .
    """
    TIME = 0
    VOLTAGE = 1
    CURRENT = 2
    POWER = 3

class DrvEpcModeE(Enum):
    """
    Type of mode the epc can be on
    """
    IDLE    = 4
    ERROR   = 5
    WAIT    = 0
    CV_MODE = 1
    CC_MODE = 2
    CP_MODE = 3

class DrvEpcStatusE(Enum):
    '''Status of the epc.
    '''
    COMM_ERROR = -1
    OK = 0
    INTERNAL_ERROR = 1

class EpcConstC:
    ''' Constants the script may need
    '''
    MIN_CAN_ID          = 0x000     # As the last 4 bits will identify the messages are reserved
    MAX_CAN_ID          = 0x7FF     # In standard mode the can id max value is 0x7FF
    MAX_HS_VOLT         = 14100     # Max high side voltage the epc has as hardware limits
    MIN_HS_VOLT         = 5300      # Min high side voltage the epc has as hardware limits
    MAX_LS_VOLT         = 5100      # Max low side voltage the epc has as hardware limits
    MIN_LS_VOLT         = 400       # Min low side voltage the epc has as hardware limits
    MAX_LS_CURR         = 15500     # Max low side current the epc has as hardware limits
    MIN_LS_CURR         = -15500    # Min low side current the epc has as hardware limits
    MAX_LS_PWR          = 800       # Max low side power the epc has as hardware limits
    MIN_LS_PWR          = -800      # Min low side power the epc has as hardware limits
    MAX_TEMP            = 700       # Max temperature the epc has as hardware limits
    MIN_TEMP            = -200      # Min temperature the epc has as hardware limits
    MASK_CAN_DEVICE     = 0x7F0
    MASK_CAN_MESSAGE    = 0x00F
    LOW_SIDE_BITFIELD   = 16
    MID_SIDE_BITFIELD   = 32
    MIN_MSG_SIZE        = 150
    TO_DECI_WATS        = 100000
    MAX_READS           = 3000

#######################             CLASSES              #######################
class DrvEpcStatusC:
    '''Handles status of the driver epc.
    '''
    def __init__(self, error: int|DrvEpcStatusE) -> None:
        if isinstance(error, DrvEpcStatusE):
            self.__status = error
            self.__error_code = error.value
        else:
            self.__error_code = error
            if error > 0:
                self.__status = DrvEpcStatusE.INTERNAL_ERROR
            else:
                self.__status = DrvEpcStatusE(error)

    def __str__(self) -> str:
        result = f"Error code: {self.__error_code} \t Status: {self.__status}"
        return result

    def __eq__(self, cmp_obj: Enum) -> bool:
        return self.__status == cmp_obj

    @property
    def error_code(self) -> int:
        '''The error code associated with this request .
        Args:
            - None
        Returns:
            - (int): The error code associated with this request.
        Raises:
            - None
        '''
        return self.__error_code

    @property
    def value(self) -> int:
        ''' Value of status.
        Args:
            - None
        Returns:
            - (int): Value of status.
        Raises:
            - None
        '''
        return self.__status.value

    @property
    def name(self) -> str:
        ''' Name of status.
        Args:
            - None
        Returns:
            - (int): name of status.
        Raises:
            - None
        '''
        return self.__status.name

class DrvEpcLimitsC:
    """Class to storage maximum and minimum value of different limits.
    """
    def __init__(self, max_value: int = 0, min_value: int = 0) -> None:
        self.max = max_value
        self.min = min_value

class DrvEpcPropInfoC:
    """
    Data that stores info about the device
    """
    def __init__(self, sw_version: int|None = None, hw_version: int = 0,
                 can_id: int = 0, serial_number: str = '') -> None:
        self.serial_number = str(serial_number)
        #Check can id is correct
        if EpcConstC.MIN_CAN_ID <= can_id <= EpcConstC.MAX_CAN_ID:
            self.can_id :int = can_id
        else:
            log.error(f"Wrong can id {hex(can_id)}, should be between 0x0 and 0x7ff")
            raise ValueError(f"Wrong can id {hex(can_id)}, should be between 0x0 and 0x7ff")
        #Check software version is correct
        if sw_version is None:
            self.sw_version= None
        elif sw_version >= 0:
            self.sw_version : int = sw_version
        else:
            log.error(f"Wrong sw version {sw_version}, should be positive")
            raise ValueError(f"Wrong sw version {sw_version}, should be positive")
        #Check hardware version is correct
        if hw_version is None:
            self.hw_version= None
        elif hw_version >= 0:
            self.hw_version    = int2ba(hw_version, length=13, endian= 'little')
        else:
            log.error(f"Wrong hw version {hw_version}, should positive")
            raise ValueError(f"Wrong hw version {hw_version}, should positive")

class DrvEpcPropertiesC(DrvEpcPropInfoC): # pylint: disable= too-many-instance-attributes
    '''
    Properties a epc can have
    '''
    def __init__(self, can_id: int = 0 , # pylint: disable= too-many-arguments
                 sw_version: int|None = None, hw_version: int= 0,
                 ls_volt_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(EpcConstC.MAX_LS_VOLT,EpcConstC.MIN_LS_VOLT),
                 ls_curr_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(EpcConstC.MAX_LS_CURR,EpcConstC.MIN_LS_CURR),
                 ls_pwr_limit:  DrvEpcLimitsC =
                    DrvEpcLimitsC(EpcConstC.MAX_LS_PWR,EpcConstC.MIN_LS_PWR),
                 hs_volt_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(EpcConstC.MAX_HS_VOLT,EpcConstC.MIN_HS_VOLT),
                 temp_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(EpcConstC.MAX_TEMP,EpcConstC.MIN_TEMP),
                 model: str = '', serial_number: str = '') -> None:
        self.model: str|None = model

        can_id = can_id <<  4 # In order to have the can id as 0xIDX it has to be moved 4 positions
        DrvEpcPropInfoC.__init__(self,sw_version, hw_version, can_id, serial_number)
        #Check low side voltage limits are correct
        if (ls_volt_limit.min < ls_volt_limit.max and ls_volt_limit.min >=EpcConstC.MIN_LS_VOLT
            and ls_volt_limit.max <= EpcConstC.MAX_LS_VOLT):
            self.ls_volt_limit: DrvEpcLimitsC = ls_volt_limit
        else:
            log.error((f"Wrong ls_volt limits, should between {EpcConstC.MIN_LS_VOLT} and "
                    f"{EpcConstC.MAX_LS_VOLT} mV, but has been introduced {ls_volt_limit.min} and "
                    f"{ls_volt_limit.max}"))
            raise ValueError((f"Wrong ls_volt limits, should between {EpcConstC.MIN_LS_VOLT} and "
                    f"{EpcConstC.MAX_LS_VOLT} mV, but has been introduced {ls_volt_limit.min} and "
                    f"{ls_volt_limit.max}"))
        #Check low side current limits are correct
        if (ls_curr_limit.min < ls_curr_limit.max and ls_curr_limit.min >= EpcConstC.MIN_LS_CURR
            and ls_curr_limit.max <= EpcConstC.MAX_LS_CURR):
            self.ls_curr_limit: DrvEpcLimitsC = ls_curr_limit
        else:
            log.error((f"Wrong ls current limits, should between +-{EpcConstC.MAX_LS_CURR} mA,"
                        f" but has been introduced {ls_curr_limit.min} and {ls_curr_limit.max}"))
            raise ValueError((f"Wrong ls current limits, should between +-{EpcConstC.MAX_LS_CURR}"
                    f" mA, but has been introduced {ls_curr_limit.min} and {ls_curr_limit.max}"))
        #Check low side power limits are correct
        if (ls_pwr_limit.min < ls_pwr_limit.max and ls_pwr_limit.min >=EpcConstC.MIN_LS_PWR
            and ls_pwr_limit.max <= EpcConstC.MAX_LS_PWR):
            self.ls_pwr_limit: DrvEpcLimitsC = ls_pwr_limit

        else:
            log.error((f"Wrong ls power limits, should between +-{EpcConstC.MAX_LS_PWR} dW, "
                      f"but has been introduced {ls_pwr_limit.min} and {ls_pwr_limit.max}"))
            raise ValueError((f"Wrong ls power limits, should between +-{EpcConstC.MAX_LS_PWR} dW, "
                             f"but has been introduced {ls_pwr_limit.min} and {ls_pwr_limit.max}"))
        #Check high side voltage limits are correct
        if (hs_volt_limit.min < hs_volt_limit.max and hs_volt_limit.min >=EpcConstC.MIN_HS_VOLT
            and hs_volt_limit.max <= EpcConstC.MAX_HS_VOLT):
            self.hs_volt_limit: DrvEpcLimitsC = hs_volt_limit

        else:
            log.error((f"Wrong hs volt limits, should between {EpcConstC.MIN_HS_VOLT} and "
                    f"{EpcConstC.MAX_HS_VOLT} mV, but has been introduced {hs_volt_limit.min} "
                    f"and {hs_volt_limit.max}"))
            raise ValueError((f"Wrong hs volt limits, should between {EpcConstC.MIN_HS_VOLT} and "
                    f"{EpcConstC.MAX_HS_VOLT} mV, but has been introduced {hs_volt_limit.min} "
                    f"and {hs_volt_limit.max}"))
        #Check temperature limits are correct
        if (temp_limit.min < temp_limit.max and temp_limit.min >=EpcConstC.MIN_TEMP
            and temp_limit.max <= EpcConstC.MAX_TEMP):
            self.temp_limit: DrvEpcLimitsC = temp_limit
        else:
            log.error((f"Wrong temp limits, should between {EpcConstC.MIN_TEMP} and "
        f"{EpcConstC.MAX_TEMP} dºC, but has been introduced {temp_limit.min} and {temp_limit.max}"))
            raise ValueError((f"Wrong temp limits, should between {EpcConstC.MIN_TEMP} and "
        f"{EpcConstC.MAX_TEMP} dºC, but has been introduced {temp_limit.min} and {temp_limit.max}"))

class DrvEpcDataElectC:
    """
    Data that stores power measurements
    """
    def __init__(self, ls_voltage: int|None = None, ls_current: int|None = None,
                ls_power: int|None = None, hs_voltage: int|None = None) -> None:
        self.ls_voltage = ls_voltage
        self.ls_current = ls_current
        self.ls_power = ls_power
        self.hs_voltage = hs_voltage

class DrvEpcDataTempC:
    """
    Data that stores temp measurements
    """
    def __init__(self, temp_body: int|None = None, temp_amb: int|None = None,
                 temp_anod: int|None = None) -> None:
        self.temp_body = temp_body
        self.temp_amb = temp_amb
        self.temp_anod = temp_anod

class DrvEpcDataCtrlC:
    """
    Data that stores mode, reference and limit reference
    """
    def __init__(self, mode: DrvEpcModeE = DrvEpcModeE.IDLE, ref: int = 0,
                 lim: DrvEpcLimitE = DrvEpcLimitE.TIME, lim_ref: int = 0) -> None:
        self.lim_ref : int = lim_ref
        self.lim_mode : DrvEpcLimitE = lim
        self.mode : DrvEpcModeE = mode
        self.ref : int = ref

class DrvEpcDataC(DrvEpcDataElectC, # pylint: disable= too-many-instance-attributes
                  DrvEpcDataTempC, DrvEpcDataCtrlC):
    """
    Data that can store the epc device, refered to measurements, status and mode.
    """
    def __init__(self, # pylint: disable= too-many-arguments
                ls_voltage: int|None = None, ls_current: int|None = None, ls_power: int|None = None,
                hs_voltage: int|None = None, temp_body: int|None = None, temp_amb: int|None = None,
                temp_anod: int|None = None, status: DrvEpcStatusC = DrvEpcStatusC(0),
                mode: DrvEpcModeE = DrvEpcModeE.IDLE) -> None:
        DrvEpcDataElectC.__init__(self, ls_voltage, ls_current, ls_power, hs_voltage)
        DrvEpcDataTempC.__init__(self, temp_body, temp_amb, temp_anod)
        DrvEpcDataCtrlC.__init__(self, mode)
        self.status = status
