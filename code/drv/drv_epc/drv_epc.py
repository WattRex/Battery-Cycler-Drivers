#!/usr/bin/python3
"""
This module will manage CAN messages and channels
in order to configure channels and send/received messages.
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
from drv.drv_pwr import DrvPwrPropertiesC, DrvPwrDeviceC, DrvPwrDataC, DrvPwrStatusC
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
    DISABLE = 4
    WAIT    = 0
    CV_MODE = 1
    CC_MODE = 2
    CP_MODE = 3

class _ConstantsC:
    TO_DECI_WATS = 100000
    MAX_READS    = 100

#######################             CLASSES              #######################
class DrvEpcPropertiesC(DrvPwrPropertiesC):
    '''
    Properties a epc can have
    '''
    def __init__(self, can_id: int, sw_version: int, hw_version: int,
                 min_ls_volt_limit: int, max_ls_volt_limit: int,
                 min_ls_curr_limit: int, max_ls_curr_limit: int,
                 min_ls_pwr_limit:  int, max_ls_pwr_limit: int,
                 min_hs_volt_limit: int, max_hs_volt_limit: int,
                 model: str, serial_number: str, max_volt_limit: int,
                 max_current_limit: int, max_pwr_limit: int,
                 max_temp_limit: int, min_temp_limit: int) -> None:
        #Check can id is correct
        if can_id >= 0x0 and can_id <= 0x7FF:
            self.can_id    = can_id
        else:
            log.error(f"Wrong can id {hex(can_id)}, should be between 0x0 and 0x7ff")
            raise ValueError
        #Check software version is correct
        if sw_version >= 0:
            self.sw_version    = sw_version
        else:
            log.error(f"Wrong sw version {sw_version}, should be over 0")
            raise ValueError
        #Check hardware version is correct
        if hw_version >= 0:
            self.hw_version    = int2ba(hw_version, length=13, endian= 'little')
        else:
            log.error(f"Wrong hw version {hw_version}, should be over 0")
            raise ValueError
        #Check low side voltage limits are correct
        if (min_ls_volt_limit < max_ls_volt_limit and min_ls_volt_limit >=400
            and max_ls_volt_limit <= 5100):
            self.min_ls_volt_limit = min_ls_volt_limit
        else:
            log.error(f"Wrong ls_volt limits, should between 400 and 5100 mV, \
                      but has been introduced {min_ls_volt_limit} and {max_ls_volt_limit}")
            raise ValueError
        #Check low side current limits are correct
        if (min_ls_curr_limit < max_ls_curr_limit and min_ls_curr_limit >= -15500
            and max_ls_curr_limit <= 15500):
            self.min_ls_curr_limit = min_ls_curr_limit
        else:
            log.error(f"Wrong ls current limits, should between +-15500 mA, \
                      but has been introduced {min_ls_curr_limit} and {max_ls_curr_limit}")
            raise ValueError
        #Check low side power limits are correct
        if (min_ls_pwr_limit < max_ls_pwr_limit and min_ls_pwr_limit >=400
            and max_ls_pwr_limit <= 5100):
            self.min_ls_pwr_limit = min_ls_pwr_limit
        else:
            log.error(f"Wrong ls power limits, should between +-800 dW, \
                      but has been introduced {min_ls_pwr_limit} and {max_ls_pwr_limit}")
            raise ValueError
        #Check high side voltage limits are correct
        if (min_hs_volt_limit < max_hs_volt_limit and min_hs_volt_limit >=5300
            and max_hs_volt_limit <= 14100):
            self.min_hs_volt_limit = min_hs_volt_limit
            self.max_hs_volt_limit = max_hs_volt_limit
        else:
            log.error(f"Wrong hs volt limits, should between 5300 and 14100 mV, \
                      but has been introduced {min_hs_volt_limit} and {max_hs_volt_limit}")
            raise ValueError
        #Check temperature limits are correct
        if (min_temp_limit < max_temp_limit and min_temp_limit >=-200
            and max_temp_limit <= 700):
            self.min_temp_limit = min_temp_limit
            self.max_temp_limit = max_temp_limit
        else:
            log.error(f"Wrong hs volt limits, should between 5300 and 14100 mV, \
                      but has been introduced {min_hs_volt_limit} and {max_hs_volt_limit}")
            raise ValueError
        #As max ls atributes came from the super class,
        # if no value error has raise, can be initialize
        super().__init__(model, serial_number, max_volt_limit, max_current_limit,
                         max_pwr_limit)

class DrvEpcDataC(DrvPwrDataC):
    """
    Data that can store the epc device, refered to measurements, status and mode.
    """
    def __init__(self, status: DrvPwrStatusC, mode: DrvEpcModeE,
                 voltage: int, current: int, power: int, hs_voltage: int,
                 temp_body: int, temp_amb: int, temp_anod: int) -> None:
        super().__init__(status, mode, voltage, current, power)
        self.hs_voltage = hs_voltage
        self.temp_body = temp_body
        self.temp_amb = temp_amb
        self.temp_anod = temp_anod
        self.lim_ref : int
        self.lim_mode : DrvEpcLimitE
        self.ref : int

class DrvEpcDeviceC(DrvPwrDeviceC):
    """Class to create epc devices with all the properties needed.

    """
    def __init__(self, dev_id: int, device_handler: SysShdChanC, tx_can_queue: SysShdChanC) -> None:
        super().__init__(device_handler)
        self.__dev_id= dev_id
        self.__tx_can = tx_can_queue
        self.__live_data : DrvEpcDataC
        self.__properties: DrvEpcPropertiesC

    def __send_to_can(self, type_msg: DrvCanCmdTypeE, msg: DrvCanMessageC|DrvCanFilterC)-> None:
        """Send a message to the CAN transmission queue .

        Args:
            msg (DrvCanMessageC): [Message to be send]
        """
        cmd = DrvCanCmdDataC(type_msg, msg)
        self.__tx_can.send_data(cmd)

    def read_can_buffer(self):
        """Receive data from the device .
        """
        if self.__device_handler.is_empty():
            log.info("The device doesn`t have any message to read")
        else:
            i=0
            while not self.__device_handler.is_empty() and i<=_ConstantsC.MAX_READS:
                # Read a message from the can queue of the device
                msg: DrvCanMessageC = self.__device_handler.receive_data()
                # Get the message id and transform the data to bitarray
                msg_id= msg.addr & 0xFF0
                msg_bitarray = int2ba(int.from_bytes(msg.data,'little'),length=64, endian='little')
                #------   0xYY0 EPC mode   ------
                if msg_id == 0x0:
                    self.__live_data.mode = DrvEpcModeE(ba2int(msg_bitarray[1:4]))
                    self.__live_data.ref = ba2int(msg_bitarray[16:32],signed=True)
                    self.__live_data.lim_mode = DrvEpcLimitE(ba2int(msg_bitarray[4:7]))
                    self.__live_data.lim_ref = ba2int(msg_bitarray[32:],signed=True)
                #------   0xYY1 EPC request  ------
                elif msg_id == 0x1:
                    log.error("The message send to request data has a format error")
                #------   0xYY2 EPC LS Voltage Limits  ------
                elif msg_id == 0x2:
                    self.__properties.max_volt_limit = ba2int(msg_bitarray[:16])
                    self.__properties.min_ls_volt_limit = ba2int(msg_bitarray[16:32])
                    log.info(f"LS Voltage limits are /n Max:{self.__properties.max_volt_limit} /n\
                            Min: {self.__properties.min_ls_volt_limit}")
                #------   0xYY3 EPC LS Current Limits  ------
                elif msg_id == 0x3:
                    max_curr = ba2int(msg_bitarray[:16],signed=True)
                    min_curr = ba2int(msg_bitarray[16:32],signed=True)
                    self.__properties.max_current_limit = max_curr
                    self.__properties.min_ls_curr_limit = min_curr
                    log.info(f"LS Current limits are /n Max:{max_curr} mA /n\
                            Min: {min_curr} mA")
                #------   0xYY4 EPC HS Voltage Limits  ------
                elif msg_id == 0x4:
                    self.__properties.max_hs_volt_limit = ba2int(msg_bitarray[:16])
                    self.__properties.min_hs_volt_limit = ba2int(msg_bitarray[16:32])
                    log.info(f"HS Voltage limits are /n Max:{self.__properties.max_hs_volt_limit}/n\
                            Min: {self.__properties.min_hs_volt_limit}")
                #------   0xYY5 EPC LS Power Limits  ------
                elif msg_id == 0x5:
                    max_pwr = ba2int(msg_bitarray[:16],signed=True)
                    min_pwr = ba2int(msg_bitarray[16:32],signed=True)
                    self.__properties.max_power_limit = max_pwr
                    self.__properties.min_ls_pwr_limit = min_pwr
                    log.info(f"LS Voltage limits are /n Max:{max_pwr} /n\
                            Min: {min_pwr}")
                #------   0xYY5 EPC Temperature Limits  ------
                elif msg_id == 0x6:
                    max_temp = ba2int(msg_bitarray[:16],signed=True)
                    min_temp = ba2int(msg_bitarray[16:32],signed=True)
                    self.__properties.max_temp_limit = max_temp
                    self.__properties.min_temp_limit = min_temp
                    log.info(f"Temperature limits are /n Max:{max_temp} /n\
                            Min: {min_temp}")
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
                        self.__live_data.status= DrvPwrStatusC(error)
                        log.info(f"Last rised error: {ba2int(msg_bitarray[6:])}")
                #------   0xYYC EPC Electrical Measures  ------
                elif msg_id == 0xC:
                    volt = ba2int(msg_bitarray[:16])
                    self.__live_data.voltage = volt
                    log.info(f"LS Voltage [mV]: {volt}")
                    curr = ba2int(msg_bitarray[16:32], signed = True)
                    self.__live_data.current = curr
                    log.info(f"LS Current [mA]: {curr}")
                    hs_volt = ba2int(msg_bitarray[32:])
                    self.__live_data.hs_voltage = hs_volt
                    log.info(f"HS Voltage [mV]: {hs_volt}")
                    power = curr * volt / _ConstantsC.TO_DECI_WATS
                    log.info(f"LS Power [dW]: {power}")
                    self.__live_data.power = int(power)
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
                    log.error("The id of the message can not be interpreted by the epc")

    def set_cv_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CV mode for a specific reference, limit type and limit reference.
        When sending this message the output will always be enable

        Args:
            ref (int): [Value in mV dessire to be set as reference, must be a positive value]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        if ref <0:
            log.error(f"Error setting the refence for CV, \
                      introduced {ref} and it should be positive")
            raise ValueError
        elif limit_type == DrvEpcLimitE.VOLTAGE:
            log.error("Limit can not be voltage when mode is CV")
            raise ValueError
        id_msg = self.__dev_id + 0x0
        data_msg= limit_ref << 32 | ref<<16 | limit_type.value << 4 | 1<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_cc_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CC mode for a specific reference, limit type and limit reference .

        Args:
            ref (int): [Value in mA dessire to be set as reference]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        if ref <0:
            log.error(f"Error setting the refence for CV, \
                      introduced {ref} and it should be positive")
            raise ValueError
        elif limit_type == DrvEpcLimitE.CURRENT:
            log.error("Limit can not be current when mode is CC")
            raise ValueError
        id_msg = self.__dev_id + 0x0
        data_msg= limit_ref << 32 | ref<<16 | limit_type.value << 4 | 2<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_cp_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CV mode for a specific reference, limit type and limit reference .

        Args:
            ref (int): [Value in dW dessire to be set as reference]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        if limit_type == DrvEpcLimitE.POWER:
            log.error("Limit can not be power when mode is CP")
            raise ValueError
        id_msg = self.__dev_id + 0x0
        data_msg= limit_ref << 32 | ref<<16 | limit_type.value << 4 | 3<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_wait_mode(self, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the WAIT mode with a specific limit type and limit reference.

        Args:
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        id_msg = self.__dev_id + 0x0
        data_msg= limit_ref << 32 | 0<<16 | limit_type.value << 4 | 0<<1 | 0
        msg = DrvCanMessageC(addr= id_msg, size= 8, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def disable(self) -> None:
        """Disable the output

        Args:
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed]
        """
        id_msg = self.__dev_id + 0x0
        data_msg= 10 << 32 | 0<<16 | 0 << 4 | 0<<1 | 0
        msg = DrvCanMessageC(addr= id_msg, size= 8, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def get_data(self) -> DrvEpcDataC | None:
        """Getter to the private attribute of live_data.
        Before returning the info it check if there is any message in can queue
        and update the attributes

        Returns:
            [DrvEpcDataC]: [description]
        """
        self.read_can_buffer()
        return self.__live_data

    def get_properties(self) -> DrvEpcPropertiesC | None:
        """Getter to the private attribute of __properties.
        Before returning the info it check if there is any message in can queue
        and update the attributes
        Returns:
            [DrvEpcPropertiesC]: [description]
        """
        self.read_can_buffer()
        return self.__properties

    def get_elec_meas(self, periodic_flag: bool) -> dict|None:
        """Get the current electric measures of the device .

        Returns:
            [dict]: [Dictionary with the voltage, current and power in low side 
                    and voltage in high side]
        """
        if not periodic_flag:
            id_msg = self.__dev_id + 0x1
            data_msg = 3
            msg = DrvCanMessageC(addr= id_msg, size= 1, payload = data_msg)
            self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return {'ls_volt': self.__live_data.voltage, 'ls_curr': self.__live_data.current,
                'ls_pwr': self.__live_data.power, 'hs_volt': self.__live_data.hs_voltage}

    def get_temp_meas(self, periodic_flag: bool) -> dict|None:
        """Get the current temperatures measure of the device .

        Returns:
            [dict]: [Dictionary with the 3 possible temperatures the device can measure]
        """
        if not periodic_flag:
            id_msg = self.__dev_id + 0x1
            data_msg = 4
            msg = DrvCanMessageC(addr= id_msg, size= 1, payload = data_msg)
            self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        res = dict()
        if self.__properties.hw_version[9] == 1:
            res['body_temperature'] = self.__live_data.temp_body
        if ba2int(self.__properties.hw_version[7:9]) != 0:
            res['anode_temperature'] = self.__live_data.temp_anod
        if self.__properties.hw_version[10] == 1:
            res['ambient_temperature'] = self.__live_data.temp_amb
        return res

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
        id_msg = self.__dev_id + 0x7
        data_msg= (temp_period << 33 | temp_en<<32 | elect_period<<17
                 | elect_en << 16 | ack_period<<1 | ack_en)
        msg = DrvCanMessageC(addr= id_msg, size= 8, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_volt_limit(self, max_lim: int, min_lim: int):
        """Set the Low Side voltage limits on the device.

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id + 0x2
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_curr_limit(self, max_lim: int, min_lim: int):
        """Set the Low Side current limit on the device.

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id + 0x3
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_hs_volt_limit(self, max_lim: int, min_lim: int):
        """Set the high side voltage limit of the device .

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id + 0x4
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_pwr_limit(self, max_lim: int, min_lim: int):
        """Set the low side `power` limit of the device

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id + 0x5
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_temp_limit(self, max_lim: int, min_lim: int):
        """Set the temperature limits of the device .

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        id_msg = self.__dev_id + 0x6
        data_msg= min_lim << 16 | max_lim
        msg = DrvCanMessageC(addr= id_msg, size= 4, payload = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def open(self, addr: int, mask: int) -> None:
        """Open a device filter .

        Args:
            addr (int): [addr of the device]
            mask (int): [mask apply to the addr in order to save the can messages]
        """
        open_filter = DrvCanFilterC(addr, mask, self.__device_handler)
        self.__send_to_can(DrvCanCmdTypeE.ADD_FILTER, open_filter)

    def close(self, addr: int, mask: int) -> None: #
        """Close the current device, and delete all messages in handler
        """
        self.read_can_buffer()
        close_filter = DrvCanFilterC(addr, mask, self.__device_handler)
        self.__send_to_can(DrvCanCmdTypeE.REMOVE_FILTER, close_filter)
        self.__device_handler.delete_until_last()
