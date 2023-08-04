#!/usr/bin/python3
"""
This module will create instances of epc device in order to control
the device and request info from it.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import os
import sys

#######################         GENERIC IMPORTS          #######################
# from typing import Any, Iterable, Callable, Mapping
from enum import Enum


#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path

from sys_abs.sys_shd import SysShdChanC
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################
from bitarray.util import ba2int, int2ba
#######################          MODULE IMPORTS          #######################


#######################          PROJECT IMPORTS         #######################
from drv.drv_can import DrvCanMessageC, DrvCanCmdDataC, DrvCanCmdTypeE, DrvCanFilterC

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

class _ConstantsC:
    ''' Constants the script may need
    '''
    TO_DECI_WATS = 100000
    MAX_READS    = 300
    MASK         = 0x7F0

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
    def __init__(self, sw_version: int = 0, hw_version: int = 0,
                 can_id: int = 0, serial_number: str = '') -> None:
        self.serial_number = str(serial_number)
        #Check can id is correct
        if 0x0 <= can_id <= 0x7FF:
            self.can_id :int = can_id
        else:
            log.error(f"Wrong can id {hex(can_id)}, should be between 0x0 and 0x7ff")
            raise ValueError
        #Check software version is correct
        if sw_version >= 0:
            self.sw_version : int = sw_version
        else:
            log.error(f"Wrong sw version {sw_version}, should be positive")
            raise ValueError
        #Check hardware version is correct
        if hw_version >= 0:
            self.hw_version    = int2ba(hw_version, length=13, endian= 'little')
        else:
            log.error(f"Wrong hw version {hw_version}, should positive")
            raise ValueError

class DrvEpcPropertiesC(DrvEpcPropInfoC):
    '''
    Properties a epc can have
    '''
    def __init__(self, can_id: int = 0 , sw_version: int = 0, hw_version: int = 0,
                 ls_volt_limit: DrvEpcLimitsC = DrvEpcLimitsC(5100,400),
                 ls_curr_limit: DrvEpcLimitsC = DrvEpcLimitsC(5100,400),
                 ls_pwr_limit:  DrvEpcLimitsC = DrvEpcLimitsC(510,-510),
                 hs_volt_limit: DrvEpcLimitsC = DrvEpcLimitsC(14100,5300),
                 temp_limit: DrvEpcLimitsC = DrvEpcLimitsC(660,-160),
                 model: str = '', serial_number: str = '') -> None:
        self.model: str|None = model
        DrvEpcPropInfoC.__init__(self,sw_version, hw_version, can_id, serial_number)
        #Check low side voltage limits are correct
        if (ls_volt_limit.min < ls_volt_limit.max and ls_volt_limit.min >=400
            and ls_volt_limit.max <= 5100):
            self.ls_volt_limit: DrvEpcLimitsC = ls_volt_limit
        else:
            log.error(f"Wrong ls_volt limits, should between 400 and 5100 mV, \
                      but has been introduced {ls_volt_limit.min} and {ls_volt_limit.max}")
            raise ValueError
        #Check low side current limits are correct
        if (ls_curr_limit.min < ls_curr_limit.max and ls_curr_limit.min >= -15500
            and ls_curr_limit.max <= 15500):
            self.ls_curr_limit: DrvEpcLimitsC = ls_curr_limit
        else:
            log.error(f"Wrong ls current limits, should between +-15500 mA, \
                      but has been introduced {ls_curr_limit.min} and {ls_curr_limit.max}")
            raise ValueError
        #Check low side power limits are correct
        if (ls_pwr_limit.min < ls_pwr_limit.max and ls_pwr_limit.min >=-800
            and ls_pwr_limit.max <= 800):
            self.ls_pwr_limit: DrvEpcLimitsC = ls_pwr_limit

        else:
            log.error(f"Wrong ls power limits, should between +-800 dW, \
                      but has been introduced {ls_pwr_limit.min} and {ls_pwr_limit.max}")
            raise ValueError
        #Check high side voltage limits are correct
        if (hs_volt_limit.min < hs_volt_limit.max and hs_volt_limit.min >=5300
            and hs_volt_limit.max <= 14100):
            self.hs_volt_limit: DrvEpcLimitsC = hs_volt_limit

        else:
            log.error(f"Wrong hs volt limits, should between 5300 and 14100 mV, \
                      but has been introduced {hs_volt_limit.min} and {hs_volt_limit.max}")
            raise ValueError
        #Check temperature limits are correct
        if (temp_limit.min < temp_limit.max and temp_limit.min >=-200
            and temp_limit.max <= 700):
            self.temp_limit: DrvEpcLimitsC = temp_limit
        else:
            log.error(f"Wrong temp limits, should between -200 and 700 dºC, \
                      but has been introduced {temp_limit.min} and {temp_limit.max}")
            raise ValueError

class DrvEpcDataElectC:
    """
    Data that stores power measurements
    """
    def __init__(self, ls_voltage: int = 0, ls_current: int = 0, ls_power: int = 0,
                hs_voltage: int = 0) -> None:
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

class DrvEpcDataC(DrvEpcDataElectC, DrvEpcDataTempC, DrvEpcDataCtrlC):
    """
    Data that can store the epc device, refered to measurements, status and mode.
    """
    def __init__(self, ls_voltage: int = 0, ls_current: int = 0, ls_power: int = 0,
                hs_voltage: int = 0, temp_body: int|None = None, temp_amb: int|None = None,
                temp_anod: int|None = None, status: DrvEpcStatusC = DrvEpcStatusC(0),
                mode: DrvEpcModeE = DrvEpcModeE.IDLE) -> None:
        DrvEpcDataElectC.__init__(self, ls_voltage, ls_current, ls_power, hs_voltage)
        DrvEpcDataTempC.__init__(self, temp_body, temp_amb, temp_anod)
        DrvEpcDataCtrlC.__init__(self, mode)
        self.status = status


class DrvEpcDeviceC :
    """Class to create epc devices with all the properties needed.

    """
    def __init__(self, dev_id: int, device_handler: SysShdChanC, tx_can_queue: SysShdChanC) -> None:
        self.__device_handler = device_handler
        self.__dev_id= dev_id
        self.__tx_can = tx_can_queue
        self.__live_data : DrvEpcDataC = DrvEpcDataC()
        self.__properties: DrvEpcPropertiesC = DrvEpcPropertiesC(can_id = dev_id<<4)

    def __send_to_can(self, type_msg: DrvCanCmdTypeE, msg: DrvCanMessageC|DrvCanFilterC)-> None:
        """Send a message to the CAN transmission queue.

        Args:
            msg (DrvCanMessageC): [Message to be send]
        """
        cmd = DrvCanCmdDataC(type_msg, msg)
        self.__tx_can.send_data(cmd)

    def read_can_buffer(self):
        """Receive data from the device .
        """
        if self.__device_handler.is_empty():
            log.debug("The device doesn`t have any message to read")
        else:
            i=0
            while not self.__device_handler.is_empty() and i<=_ConstantsC.MAX_READS:
                i = i+1
                # Read a message from the can queue of the device
                msg: DrvCanMessageC = self.__device_handler.receive_data()
                # Get the message id and transform the data to bitarray
                msg_id= msg.addr & 0x00F
                msg_bitarray = int2ba(int.from_bytes(msg.data,'little'),length=64, endian='little')
                #------   0xYY0 EPC mode   ------
                if msg_id == 0x0:
                    self.__live_data.mode = DrvEpcModeE(ba2int(msg_bitarray[1:4],signed=False))
                    self.__live_data.ref = ba2int(msg_bitarray[16:32],signed=True)
                    self.__live_data.lim_mode = DrvEpcLimitE(ba2int(msg_bitarray[4:6],signed=False))
                    self.__live_data.lim_ref = ba2int(msg_bitarray[32:],signed=True)
                #------   0xYY1 EPC request  ------
                elif msg_id == 0x1:
                    log.error("The message send to request data has a format error")
                #------   0xYY2 EPC LS Voltage Limits  ------
                elif msg_id == 0x2:
                    self.__properties.ls_volt_limit.max = ba2int(msg_bitarray[:16])
                    self.__properties.ls_volt_limit.min = ba2int(msg_bitarray[16:32])
                    log.info(f"LS Voltage limits are Max:{self.__properties.ls_volt_limit.max} mV"+\
                            f" Min: {self.__properties.ls_volt_limit.min} mV")
                #------   0xYY3 EPC LS Current Limits  ------
                elif msg_id == 0x3:
                    max_curr = ba2int(msg_bitarray[:16],signed=True)
                    min_curr = ba2int(msg_bitarray[16:32],signed=True)
                    self.__properties.ls_curr_limit.max = max_curr
                    self.__properties.ls_curr_limit.min = min_curr
                    log.info(f"LS Current limits are Max:{max_curr} mA "+\
                            f"Min: {min_curr} mA")
                #------   0xYY4 EPC HS Voltage Limits  ------
                elif msg_id == 0x4:
                    self.__properties.hs_volt_limit.max = ba2int(msg_bitarray[:16])
                    self.__properties.hs_volt_limit.min = ba2int(msg_bitarray[16:32])
                    log.info(f"HS Voltage limits are Max:{self.__properties.hs_volt_limit.max} mV"+\
                            f" Min: {self.__properties.hs_volt_limit.min} mV")
                #------   0xYY5 EPC LS Power Limits  ------
                elif msg_id == 0x5:
                    max_pwr = ba2int(msg_bitarray[:16],signed=True)
                    min_pwr = ba2int(msg_bitarray[16:32],signed=True)
                    self.__properties.ls_pwr_limit.max = max_pwr
                    self.__properties.ls_pwr_limit.min = min_pwr
                    log.info(f"LS Power limits are Max:{max_pwr} dW "+ \
                            f"Min: {min_pwr} dW")
                #------   0xYY5 EPC Temperature Limits  ------
                elif msg_id == 0x6:
                    max_temp = ba2int(msg_bitarray[:16],signed=True)
                    min_temp = ba2int(msg_bitarray[16:32],signed=True)
                    self.__properties.temp_limit.max = max_temp
                    self.__properties.temp_limit.min = min_temp
                    log.info(f"Temperature limits are Max:{max_temp} dºC "+ \
                            f"Min: {min_temp} dºC")
                #------   0xYY7 EPC Response Configuration  ------
                elif msg_id == 0x7:
                    log.info(f"Enable user ACK: {msg_bitarray[0]}")
                    log.info(f"Period user ACK: {ba2int(msg_bitarray[1:16])}")
                    log.info(f"Enable periodic electric meas: {msg_bitarray[16]}")
                    log.info(f"Period periodic electric meas: {ba2int(msg_bitarray[16:32])}")
                    log.info(f"Enable periodic temp meas: {msg_bitarray[32]}")
                    log.info(f"Period periodic temp meas: {ba2int(msg_bitarray[32:])}")
                #------   0xYYA EPC Info details  ------
                elif msg_id == 0xA:
                    can_id = ba2int(msg_bitarray[:6])
                    self.__properties.can_id = can_id
                    log.info(f"Device ID: {can_id}")
                    fw_ver = ba2int(msg_bitarray[6:11])
                    self.__properties.sw_version = fw_ver
                    log.info(f"Device fw version: {fw_ver}")
                    hw_ver = msg_bitarray[11:]
                    self.__properties.hw_version = hw_ver
                    log.info(f"Device hw version: {ba2int(hw_ver)}")
                #------   0xYYB EPC Status register  ------
                elif msg_id == 0xB:
                    if msg_bitarray[0] == 1:
                        log.info("HS voltage error")
                    if msg_bitarray[1] == 1:
                        log.info("LS voltage error")
                    if msg_bitarray[2] == 1:
                        log.info("LS current error")
                    if msg_bitarray[3] == 1:
                        log.info("Communication error")
                    if msg_bitarray[4] == 1:
                        log.info("Temperature error")
                    if msg_bitarray[5] == 1:
                        log.info("Internal error")
                    error = ba2int(msg_bitarray[:6])
                    if error>0:
                        self.__live_data.status= DrvEpcStatusC(error)
                        log.info(f"Last rised error: {ba2int(msg_bitarray[6:])}")
                #------   0xYYC EPC Electrical Measures  ------
                elif msg_id == 0xC:
                    volt = ba2int(msg_bitarray[:16])
                    self.__live_data.ls_voltage = volt
                    log.info(f"LS Voltage [mV]: {volt}")
                    curr = ba2int(msg_bitarray[16:32], signed = True)
                    self.__live_data.ls_current = curr
                    log.info(f"LS Current [mA]: {curr}")
                    hs_volt = ba2int(msg_bitarray[32:])
                    self.__live_data.hs_voltage = hs_volt
                    log.info(f"HS Voltage [mV]: {hs_volt}")
                    power = curr * volt / _ConstantsC.TO_DECI_WATS
                    log.info(f"LS Power [dW]: {power}")
                    self.__live_data.ls_power = int(power)
                #------   0xYYD EPC Temperature measures  ------
                elif msg_id == 0xD:
                    if self.__properties.hw_version[9] == 1:
                        temp_body = ba2int(msg_bitarray[:16], signed = True)
                        self.__live_data.temp_body = temp_body
                        log.info(f"Body temperature [dºC]: {temp_body}")
                    if ba2int(self.__properties.hw_version[7:9]) != 0:
                        temp_anod = ba2int(msg_bitarray[16:32], signed = True)
                        self.__live_data.temp_anod = temp_anod
                        log.info(f"Anode temperature [dºC]: {temp_anod}")
                    if self.__properties.hw_version[10] == 1:
                        temp_amb = ba2int(msg_bitarray[32:48], signed = True)
                        self.__live_data.temp_amb = temp_amb
                        log.info(f"Ambient temperature [dºC]: {temp_amb}")
                else:
                    log.error(f"The id of the message can not \
                              be interpreted by the epc {hex(msg_id)}")

    def set_cv_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CV mode for a specific reference, limit type and limit reference.
        When sending this message the output will always be enable

        Args:
            ref (int): [Value in mV dessire to be set as reference, must be a positive value]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        if not (self.__properties.ls_volt_limit.min <= ref <= self.__properties.ls_volt_limit.max):
            log.error(f"Error setting the refence for CV, \
                      introduced {ref} and it should be between max and min limits")
            raise ValueError
        if limit_type == DrvEpcLimitE.VOLTAGE:
            log.error("Limit can not be voltage when mode is CV")
            raise ValueError
        id_msg = self.__properties.can_id << 4 | 0x0
        ref = ba2int(int2ba(ref,length=16, signed = True), signed = False)
        if limit_type.name in (DrvEpcLimitE.CURRENT, DrvEpcLimitE.POWER):
            limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        data_msg= limit_ref << 32 | ref<<16 | limit_type.value << 4 | 1<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_cc_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CC mode for a specific reference, limit type and limit reference .

        Args:
            ref (int): [Value in mA dessire to be set as reference]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        if not (self.__properties.ls_curr_limit.min <= ref <= self.__properties.ls_curr_limit.max):
            log.error(f"Error setting the refence for CC, \
                      introduced {ref} and it should be "+
                    f" between max {self.__properties.ls_curr_limit.max}  and "+
                    f"min {self.__properties.ls_curr_limit.min} limits")
            raise ValueError
        if limit_type == DrvEpcLimitE.CURRENT:
            log.error("Limit can not be current when mode is CC")
            raise ValueError
        id_msg = self.__dev_id << 4 | 0x0
        ref = ba2int(int2ba(ref,length=16, signed = True), signed = False)
        if limit_type.name in (DrvEpcLimitE.CURRENT, DrvEpcLimitE.POWER):
            limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        data_msg= limit_ref << 32 | ref<<16 | limit_type.value << 4 | 2<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_cp_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CV mode for a specific reference, limit type and limit reference .

        Args:
            ref (int): [Value in dW dessire to be set as reference]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        if not (self.__properties.ls_pwr_limit.min <= ref <= self.__properties.ls_pwr_limit.max):
            log.error(f"Error setting the refence for CC, \
                      introduced {ref} and it should be between max and min limits")
        if limit_type == DrvEpcLimitE.POWER:
            log.error("Limit can not be power when mode is CP")
            raise ValueError
        id_msg = self.__dev_id << 4 | 0x0
        ref = ba2int(int2ba(ref,length=16, signed = True), signed = False)
        if limit_type.name in (DrvEpcLimitE.CURRENT, DrvEpcLimitE.POWER):
            limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        data_msg= limit_ref << 32 | ref<<16 | limit_type.value << 4 | 3<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_wait_mode(self, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the WAIT mode with a specific limit type and limit reference.

        Args:
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        id_msg = self.__dev_id << 4 | 0x0
        data_msg= limit_ref << 32 | 0<<16 | limit_type.value << 4 | 0<<1 | 0
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def disable(self) -> None:
        """Disable the output

        Args:
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        id_msg = self.__dev_id << 4 | 0x0
        data_msg= 10 << 32 | 0<<16 | 0 << 4 | 0<<1 | 0
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def get_data(self, update: bool = False) -> DrvEpcDataC:
        """Getter to the private attribute of live_data.
        Before returning the info it check if there is any message in can queue
        and update the attributes

        Returns:
            [DrvEpcDataC]: [description]
        """
        if update:
            self.get_elec_meas()
            self.get_temp_meas()
            self.get_mode()
            self.get_status()
        self.read_can_buffer()
        return self.__live_data

    def get_properties(self, update: bool = False) -> DrvEpcPropertiesC:
        """Getter to the private attribute of __properties.
        Before returning the info it check if there is any message in can queue
        and update the attributes
        Returns:
            [DrvEpcPropertiesC]: [description]
        """
        if update:
            self.get_temp_limits()
            self.get_hs_volt_limits()
            self.get_ls_curr_limits()
            self.get_ls_pwr_limits()
            self.get_ls_volt_limits()
            self.get_info()
        self.read_can_buffer()
        return self.__properties

    def get_elec_meas(self, periodic_flag: bool= False) -> DrvEpcDataElectC:
        """Get the current electric measures of the device .

        Returns:
            [dict]: [Dictionary with the voltage, current and power in low side 
                    and voltage in high side]
        """
        if not periodic_flag:
            id_msg = self.__dev_id << 4 | 0x1
            data_msg = 3
            msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
            self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return DrvEpcDataElectC(self.__live_data.ls_voltage, self.__live_data.ls_current,
                                self.__live_data.ls_power, self.__live_data.hs_voltage)

    def get_temp_meas(self, periodic_flag: bool = False) -> DrvEpcDataTempC:
        """Get the current temperatures measure of the device .

        Returns:
            [dict]: [Dictionary with the 3 possible temperatures the device can measure
                    body_temperature, anode_temperature, ambient_temperature]
        """
        if not periodic_flag:
            id_msg = self.__dev_id << 4 | 0x1
            data_msg = 4
            msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
            self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return DrvEpcDataTempC(self.__live_data.temp_body, self.__live_data.temp_amb,
                               self.__live_data.temp_anod)

    def get_mode(self) -> DrvEpcDataCtrlC:
        """Get the current mode.

        Returns:
            dict: [Dictionary with keys: mode, limit, ref and limit_ref]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 1
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

        return DrvEpcDataCtrlC(self.__live_data.mode, self.__live_data.ref,
                                self.__live_data.lim_mode, self.__live_data.lim_ref)

    def get_status(self) -> DrvEpcStatusC:
        """Get the status of the device .

        Returns:
            dict: [Dictionary with the errors of the device, been the keys the following:
            error_code, error
            The value of the error code is a string with the hexadecimal value]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 2
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__live_data.status

    def set_periodic(self, ack_en: bool = False, ack_period: int = 10,
                     elect_en: bool = False, elect_period: int = 10,
                     temp_en: bool = False, temp_period: int = 10):
        """Set the periodic messages for the device .

        Args:
            ack_en (bool, optional): [description]. Defaults to False.
            ack_period (int, optional): [description]. Defaults to 10.
            elect_en (bool, optional): [description]. Defaults to False.
            elect_period (int, optional): [description]. Defaults to 10.
            temp_en (bool, optional): [description]. Defaults to False.
            temp_period (int, optional): [description]. Defaults to 10.
        """
        id_msg = self.__dev_id << 4 | 0x7
        data_msg= (temp_period << 33 | temp_en<<32 | elect_period<<17
                 | elect_en << 16 | ack_period<<1 | ack_en)
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_volt_limit(self, max_lim: int, min_lim: int):
        """Set the Low Side voltage limits on the device.

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id << 4 | 0x2
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_curr_limit(self, max_lim: int, min_lim: int):
        """Set the Low Side current limit on the device.

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id << 4 | 0x3
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_hs_volt_limit(self, max_lim: int, min_lim: int):
        """Set the high side voltage limit of the device .

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id << 4 | 0x4
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_pwr_limit(self, max_lim: int, min_lim: int):
        """Set the low side `power` limit of the device

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id << 4 | 0x5
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_temp_limit(self, max_lim: int, min_lim: int):
        """Set the temperature limits of the device .

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id << 4 | 0x6
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def get_ls_volt_limits(self) -> DrvEpcLimitsC:
        """Get the low side voltage limits .

        Returns:
            dict: [Dictionary with the keys: max_ls_volt, min_ls_volt]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 6
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.ls_volt_limit

    def get_ls_curr_limits(self) -> DrvEpcLimitsC:
        """Get the low side current limits .

        Returns:
            dict: [Dictionary with the keys: max_ls_curr, min_ls_curr]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 7
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.ls_curr_limit

    def get_hs_volt_limits(self) -> DrvEpcLimitsC:
        """Get the high side voltage limits for the device .

        Returns:
            dict: [Dictionary with the keys: max_hs_volt, min_hs_volt]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 8
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.hs_volt_limit

    def get_ls_pwr_limits(self) -> DrvEpcLimitsC:
        """Get the LWM limit limits .

        Returns:
            dict: [Dictionary with the keys: max_pwr, min_pwr]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 9
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.ls_pwr_limit

    def get_temp_limits(self) -> DrvEpcLimitsC:
        """Get the current temperature limits .

        Returns:
            dict: [Dictionary with the keys: max_temp, min_temp]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 0xA
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.temp_limit

    def get_info(self) -> DrvEpcPropInfoC:
        """Get the current temperature limits .

        Returns:
            dict: [Dictionary with the keys: dev_id, sw_version, hw_version]
        """
        id_msg = self.__dev_id << 4 | 0x1
        data_msg = 0x0
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return DrvEpcPropInfoC(self.__properties.sw_version,
                               ba2int(self.__properties.hw_version),
                               self.__properties.can_id,
                               self.__properties.serial_number)

    def open(self) -> None:
        """Open a device filter .

        Args:
            addr (int): [addr of the device]
            mask (int): [mask apply to the addr in order to save the can messages]
        """
        open_filter = DrvCanFilterC(self.__dev_id << 4, _ConstantsC.MASK, self.__device_handler)
        self.__send_to_can(DrvCanCmdTypeE.ADD_FILTER, open_filter)

    def close(self) -> None:
        """Close the current device, and delete all messages in handler
        """
        self.read_can_buffer()
        close_filter = DrvCanFilterC(self.__dev_id << 4, _ConstantsC.MASK, self.__device_handler)
        self.__send_to_can(DrvCanCmdTypeE.REMOVE_FILTER, close_filter)
        self.__device_handler.delete_until_last()
