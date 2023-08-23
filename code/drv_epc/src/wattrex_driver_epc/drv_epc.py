#!/usr/bin/python3
"""
This module will create instances of epc device in order to control
the device and request info from it.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum

#######################       THIRD PARTY IMPORTS        #######################
from bitarray.util import ba2int, int2ba
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
from system_shared_tool import SysShdChanC
from can_sniffer import DrvCanMessageC, DrvCanCmdDataC, DrvCanCmdTypeE, DrvCanFilterC

if __name__ == '__main__':
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

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

class _EpcMsgTypeE(Enum):
    """
    Internal class for the message type epc.
    """
    MODE = 0x0
    REQUEST = 0x1
    LS_VOLT_LIM = 0x2
    LS_CURR_LIM = 0x3
    HS_VOLT_LIM = 0x4
    LS_PWR_LIM = 0x5
    TEMP_LIM = 0x6
    PERIODIC = 0x7
    INFO = 0xA
    STATUS = 0xB
    ELEC_MEAS = 0xC
    TEMP_MEAS = 0xD

class _ConstC:
    ''' Constants the script may need
    '''
    TO_DECI_WATS        = 100000
    MAX_READS           = 300
    MIN_CAN_ID          = 0x00F     # As the last 4 bits will identify the messages are reserved
    MAX_CAN_ID          = 0x7FF     # In standard mode the can id max value is 0x7FF
    MASK_CAN_DEVICE     = 0x7F0
    MASK_CAN_MESSAGE    = 0x00F
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
    LOW_SIDE_BITFIELD   = 16
    MID_SIDE_BITFIELD   = 32

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
        if _ConstC.MIN_CAN_ID <= can_id <= _ConstC.MAX_CAN_ID:
            self.can_id :int = can_id
        else:
            log.error(f"Wrong can id {hex(can_id)}, should be between 0x0 and 0x7ff")
            raise ValueError
        #Check software version is correct
        if sw_version is None:
            self.sw_version= None
        elif sw_version >= 0:
            self.sw_version : int = sw_version
        else:
            log.error(f"Wrong sw version {sw_version}, should be positive")
            raise ValueError
        #Check hardware version is correct
        if hw_version is None:
            self.hw_version= None
        elif hw_version >= 0:
            self.hw_version    = int2ba(hw_version, length=13, endian= 'little')
        else:
            log.error(f"Wrong hw version {hw_version}, should positive")
            raise ValueError

class DrvEpcPropertiesC(DrvEpcPropInfoC): # pylint: disable= too-many-instance-attributes
    '''
    Properties a epc can have
    '''
    def __init__(self, can_id: int = 0 , # pylint: disable= too-many-arguments
                 sw_version: int|None = None, hw_version: int= 0,
                 ls_volt_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(_ConstC.MAX_LS_VOLT,_ConstC.MIN_LS_VOLT),
                 ls_curr_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(_ConstC.MAX_LS_CURR,_ConstC.MIN_LS_CURR),
                 ls_pwr_limit:  DrvEpcLimitsC =
                    DrvEpcLimitsC(_ConstC.MAX_LS_PWR,_ConstC.MIN_LS_PWR),
                 hs_volt_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(_ConstC.MAX_HS_VOLT,_ConstC.MIN_HS_VOLT),
                 temp_limit: DrvEpcLimitsC =
                    DrvEpcLimitsC(_ConstC.MAX_TEMP,_ConstC.MIN_TEMP),
                 model: str = '', serial_number: str = '') -> None:
        self.model: str|None = model

        can_id = can_id <<  4 # In order to have the can id as 0xIDX it has to be moved 4 positions
        DrvEpcPropInfoC.__init__(self,sw_version, hw_version, can_id, serial_number)
        #Check low side voltage limits are correct
        if (ls_volt_limit.min < ls_volt_limit.max and ls_volt_limit.min >=_ConstC.MIN_LS_VOLT
            and ls_volt_limit.max <= _ConstC.MAX_LS_VOLT):
            self.ls_volt_limit: DrvEpcLimitsC = ls_volt_limit
        else:
            log.error(f"Wrong ls_volt limits, should between 400 and 5100 mV, \
                      but has been introduced {ls_volt_limit.min} and {ls_volt_limit.max}")
            raise ValueError
        #Check low side current limits are correct
        if (ls_curr_limit.min < ls_curr_limit.max and ls_curr_limit.min >= _ConstC.MIN_LS_CURR
            and ls_curr_limit.max <= _ConstC.MAX_LS_CURR):
            self.ls_curr_limit: DrvEpcLimitsC = ls_curr_limit
        else:
            log.error(f"Wrong ls current limits, should between +-15500 mA, \
                      but has been introduced {ls_curr_limit.min} and {ls_curr_limit.max}")
            raise ValueError
        #Check low side power limits are correct
        if (ls_pwr_limit.min < ls_pwr_limit.max and ls_pwr_limit.min >=_ConstC.MIN_LS_PWR
            and ls_pwr_limit.max <= _ConstC.MAX_LS_PWR):
            self.ls_pwr_limit: DrvEpcLimitsC = ls_pwr_limit

        else:
            log.error(f"Wrong ls power limits, should between +-800 dW, \
                      but has been introduced {ls_pwr_limit.min} and {ls_pwr_limit.max}")
            raise ValueError
        #Check high side voltage limits are correct
        if (hs_volt_limit.min < hs_volt_limit.max and hs_volt_limit.min >=_ConstC.MIN_HS_VOLT
            and hs_volt_limit.max <= _ConstC.MAX_HS_VOLT):
            self.hs_volt_limit: DrvEpcLimitsC = hs_volt_limit

        else:
            log.error(f"Wrong hs volt limits, should between 5300 and 14100 mV, \
                      but has been introduced {hs_volt_limit.min} and {hs_volt_limit.max}")
            raise ValueError
        #Check temperature limits are correct
        if (temp_limit.min < temp_limit.max and temp_limit.min >=_ConstC.MIN_TEMP
            and temp_limit.max <= _ConstC.MAX_TEMP):
            self.temp_limit: DrvEpcLimitsC = temp_limit
        else:
            log.error(f"Wrong temp limits, should between -200 and 700 dºC, \
                      but has been introduced {temp_limit.min} and {temp_limit.max}")
            raise ValueError

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
                  DrvEpcDataTempC,
                  DrvEpcDataCtrlC):
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


class DrvEpcDeviceC : # pylint: disable= too-many-public-methods
    """Class to create epc devices with all the properties needed.

    """
    def __init__(self, dev_id: int, device_handler: SysShdChanC, tx_can_queue: SysShdChanC) -> None:
        self.__device_handler = device_handler
        self.__dev_id= dev_id #pylint: disable=unused-private-member
        self.__tx_can = tx_can_queue
        self.__live_data : DrvEpcDataC = DrvEpcDataC()
        self.__properties: DrvEpcPropertiesC = DrvEpcPropertiesC(can_id = dev_id)

    def __send_to_can(self, type_msg: DrvCanCmdTypeE, msg: DrvCanMessageC|DrvCanFilterC)-> None:
        """Send a message to the CAN transmission queue.

        Args:
            msg (DrvCanMessageC): [Message to be send]
        """
        cmd = DrvCanCmdDataC(type_msg, msg)
        self.__tx_can.send_data(cmd)

    def read_can_buffer( # pylint: disable= too-many-statements, too-many-branches, too-many-locals
            self):
        """Receive data from the device .
        """
        if self.__device_handler.is_empty():
            log.debug("The device doesn`t have any message to read")
        else:
            i=0
            while not self.__device_handler.is_empty() and i<=_ConstC.MAX_READS:
                i = i+1
                # Read a message from the can queue of the device
                msg: DrvCanMessageC = self.__device_handler.receive_data()
                # Get the message id and transform the data to bitarray
                msg_id= msg.addr & 0x00F
                msg_bits = int2ba(int.from_bytes(msg.data,'little'),length=64, endian='little')
                #------   0xYY0 EPC mode   ------
                if msg_id == _EpcMsgTypeE.MODE.value:
                    # The message has in the first 4 bits if the output is enable and the mode
                    self.__live_data.mode = DrvEpcModeE(ba2int(msg_bits[1:4],signed=False))
                    #The next 3 bits corresponds to the type of limit
                    self.__live_data.lim_mode = DrvEpcLimitE(ba2int(msg_bits[4:6],signed=False))
                    # From the bit 16 to the 32 correspond to the mode reference
                    self.__live_data.ref = ba2int(
                        msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD],
                        signed=True)
                    # From the bit 32 forwards is the reference for the limit
                    self.__live_data.lim_ref = ba2int(msg_bits[_ConstC.MID_SIDE_BITFIELD:],
                                                      signed=True)
                #------   0xYY1 EPC request  ------
                elif msg_id == _EpcMsgTypeE.REQUEST.value:
                    log.error("The message send to request data has a format error")
                #------   0xYY2 EPC LS Voltage Limits  ------
                elif msg_id == _EpcMsgTypeE.LS_VOLT_LIM.value:
                    self.__properties.ls_volt_limit.max = ba2int(
                        msg_bits[:_ConstC.LOW_SIDE_BITFIELD])
                    self.__properties.ls_volt_limit.min = ba2int(
                        msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD])
                    log.info(f"LS Voltage limits are Max:{self.__properties.ls_volt_limit.max} mV"+\
                            f" Min: {self.__properties.ls_volt_limit.min} mV")
                #------   0xYY3 EPC LS Current Limits  ------
                elif msg_id == _EpcMsgTypeE.LS_CURR_LIM.value:
                    max_curr = ba2int(msg_bits[:_ConstC.LOW_SIDE_BITFIELD],signed=True)
                    min_curr = ba2int(
                        msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD],
                        signed=True)
                    self.__properties.ls_curr_limit.max = max_curr
                    self.__properties.ls_curr_limit.min = min_curr
                    log.info(f"LS Current limits are Max:{max_curr} mA "+\
                            f"Min: {min_curr} mA")
                #------   0xYY4 EPC HS Voltage Limits  ------
                elif msg_id == _EpcMsgTypeE.HS_VOLT_LIM.value:
                    self.__properties.hs_volt_limit.max = ba2int(
                        msg_bits[:_ConstC.LOW_SIDE_BITFIELD])
                    self.__properties.hs_volt_limit.min = ba2int(
                        msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD])
                    log.info(f"HS Voltage limits are Max:{self.__properties.hs_volt_limit.max} mV"+\
                            f" Min: {self.__properties.hs_volt_limit.min} mV")
                #------   0xYY5 EPC LS Power Limits  ------
                elif msg_id == _EpcMsgTypeE.LS_PWR_LIM.value:
                    max_pwr = ba2int(msg_bits[:_ConstC.LOW_SIDE_BITFIELD],signed=True)
                    min_pwr = ba2int(
                        msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD],
                        signed=True)
                    self.__properties.ls_pwr_limit.max = max_pwr
                    self.__properties.ls_pwr_limit.min = min_pwr
                    log.info(f"LS Power limits are Max:{max_pwr} dW "+ \
                            f"Min: {min_pwr} dW")
                #------   0xYY6 EPC Temperature Limits  ------
                elif msg_id == _EpcMsgTypeE.TEMP_LIM.value:
                    max_temp = ba2int(msg_bits[:_ConstC.LOW_SIDE_BITFIELD],signed=True)
                    min_temp = ba2int(
                        msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD],
                                      signed=True)
                    self.__properties.temp_limit.max = max_temp
                    self.__properties.temp_limit.min = min_temp
                    log.info(f"Temperature limits are Max:{max_temp} dºC "+ \
                            f"Min: {min_temp} dºC")
                #------   0xYY7 EPC Response Configuration  ------
                elif msg_id == _EpcMsgTypeE.PERIODIC.value:
                    log.info(f"Enable user ACK: {msg_bits[0]}")
                    log.info(f"Period user ACK: {ba2int(msg_bits[1:_ConstC.LOW_SIDE_BITFIELD])}")
                    en_elect = msg_bits[_ConstC.LOW_SIDE_BITFIELD]
                    log.info(f"Enable periodic electric meas: {en_elect}")
                    prd_elec = ba2int(msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD])
                    log.info(f"Period periodic electric meas: {prd_elec}")
                    en_temp = msg_bits[_ConstC.MID_SIDE_BITFIELD]
                    log.info(f"Enable periodic temp meas: {en_temp}")
                    prd_temp = ba2int(msg_bits[_ConstC.MID_SIDE_BITFIELD:])
                    log.info(f"Period periodic temp meas: {prd_temp}")
                #------   0xYYA EPC Info details  ------
                elif msg_id == _EpcMsgTypeE.INFO.value:
                    # The first 6 bits correspond to the can id
                    can_id = ba2int(msg_bits[:6])
                    self.__properties.can_id = can_id << 4
                    log.info(f"Device ID: {can_id}")
                    # The next 5 bits correspond to the fw version
                    fw_ver = ba2int(msg_bits[6:11])
                    self.__properties.sw_version = fw_ver
                    log.info(f"Device fw version: {fw_ver}")
                    # The next 13 bits correspond to the hw version
                    hw_ver = msg_bits[11:24]
                    self.__properties.hw_version = hw_ver
                    log.info(f"Device hw version: {ba2int(hw_ver)}")
                    # The last bits correspond to the serial number
                    self.__properties.serial_number = ba2int(msg_bits[24:32])
                #------   0xYYB EPC Status register  ------
                elif msg_id == _EpcMsgTypeE.STATUS.value:
                    # The first 5 bits correspond each one to a different error type
                    if msg_bits[0] == 1:
                        log.error("HS voltage error")
                    if msg_bits[1] == 1:
                        log.error("LS voltage error")
                    if msg_bits[2] == 1:
                        log.error("LS current error")
                    if msg_bits[3] == 1:
                        log.error("Communication error")
                    if msg_bits[4] == 1:
                        log.error("Temperature error")
                    if msg_bits[5] == 1:
                        log.error("Internal error")
                    # The next bits correspond to the value error given
                    error = ba2int(msg_bits[:6])
                    if error>0:
                        self.__live_data.status= DrvEpcStatusC(error)
                        log.error(f"Last rised error: {ba2int(msg_bits[6:])}")
                #------   0xYYC EPC Electrical Measures  ------
                elif msg_id == _EpcMsgTypeE.ELEC_MEAS.value:
                    # The electrical measures are codified, been the first 16 bits the ls volt
                    volt = ba2int(msg_bits[:_ConstC.LOW_SIDE_BITFIELD])
                    self.__live_data.ls_voltage = volt
                    log.info(f"LS Voltage [mV]: {volt}")
                    # The next 16 bits corresponds to the low side current
                    curr = ba2int(msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD],
                                  signed = True)
                    self.__live_data.ls_current = curr
                    log.info(f"LS Current [mA]: {curr}")
                    # Finally the last 16 bits correspond to the high side voltage
                    hs_volt = ba2int(msg_bits[_ConstC.MID_SIDE_BITFIELD:])
                    self.__live_data.hs_voltage = hs_volt
                    log.info(f"HS Voltage [mV]: {hs_volt}")
                    # The power is obtained from the measured values of ls current and voltage
                    power = curr * volt / _ConstC.TO_DECI_WATS
                    log.info(f"LS Power [dW]: {power}")
                    self.__live_data.ls_power = int(power)
                #------   0xYYD EPC Temperature measures  ------
                elif msg_id == _EpcMsgTypeE.TEMP_MEAS.value:
                    # The temperature measures are codified, been the first 16 bits the body temp
                    if self.__properties.hw_version[9] == 1:
                        temp_body = ba2int(msg_bits[:_ConstC.LOW_SIDE_BITFIELD], signed = True)
                        self.__live_data.temp_body = temp_body
                        log.info(f"Body temperature [dºC]: {temp_body}")
                    # The next 16 bits are the temperature in the anode
                    if ba2int(self.__properties.hw_version[7:9]) != 0:
                        temp_anod = ba2int(
                            msg_bits[_ConstC.LOW_SIDE_BITFIELD:_ConstC.MID_SIDE_BITFIELD],
                            signed = True)
                        self.__live_data.temp_anod = temp_anod
                        log.info(f"Anode temperature [dºC]: {temp_anod}")
                    # The last 16 bits are for the ambient temperature
                    if self.__properties.hw_version[10] == 1:
                        temp_amb = ba2int(msg_bits[_ConstC.MID_SIDE_BITFIELD:48], signed = True)
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
            limit_ref (int): [Reference for the limit imposed,
                depending on the limit units will be mA/dW/ms]
        """
        if not self.__properties.ls_volt_limit.min <= ref <= self.__properties.ls_volt_limit.max:
            log.error(f"Error setting the refence for CV, \
                      introduced {ref} and it should be between max and min limits")
            raise ValueError
        if limit_type == DrvEpcLimitE.VOLTAGE:
            log.error("Limit can not be voltage when mode is CV")
            raise ValueError
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.MODE.value
        ref = ba2int(int2ba(ref,length=16, signed = True), signed = False)
        if limit_type in (DrvEpcLimitE.CURRENT, DrvEpcLimitE.POWER):
            limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        data_msg= union_control(enable= True, mode= DrvEpcModeE.CV_MODE, lim_mode= limit_type,
                                ref=ref, lim_ref= limit_ref)
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_cc_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CC mode for a specific reference, limit type and limit reference .

        Args:
            ref (int): [Value in mA dessire to be set as reference]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed,
                depending on the limit units will be mV/dW/ms]
        """
        if not self.__properties.ls_curr_limit.min <= ref <= self.__properties.ls_curr_limit.max:
            log.error(f"Error setting the refence for CC, \
                      introduced {ref} and it should be "+
                    f" between max {self.__properties.ls_curr_limit.max}  and "+
                    f"min {self.__properties.ls_curr_limit.min} limits")
            raise ValueError
        if limit_type == DrvEpcLimitE.CURRENT:
            log.error("Limit can not be current when mode is CC")
            raise ValueError
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.MODE.value
        ref = ba2int(int2ba(ref,length=16, signed = True), signed = False)
        if limit_type in (DrvEpcLimitE.CURRENT, DrvEpcLimitE.POWER):
            limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        data_msg= union_control(enable= True, mode= DrvEpcModeE.CC_MODE, lim_mode= limit_type,
                                ref=ref, lim_ref= limit_ref)
        #limit_ref << 32 | ref<<16 | limit_type.value << 4 | 2<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_cp_mode(self, ref: int, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the CV mode for a specific reference, limit type and limit reference .

        Args:
            ref (int): [Value in dW dessire to be set as reference]
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed,
                depending on the limit units will be mV/mA/ms]
        """
        if not self.__properties.ls_pwr_limit.min <= ref <= self.__properties.ls_pwr_limit.max:
            log.error(f"Error setting the refence for CC, \
                      introduced {ref} and it should be between max and min limits")
        if limit_type == DrvEpcLimitE.POWER:
            log.error("Limit can not be power when mode is CP")
            raise ValueError
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.MODE.value
        ref = ba2int(int2ba(ref,length=16, signed = True), signed = False)
        if limit_type in (DrvEpcLimitE.CURRENT, DrvEpcLimitE.POWER):
            limit_ref = ba2int(int2ba(limit_ref,length=32, signed = True), signed = False)
        data_msg= union_control(enable= True, mode= DrvEpcModeE.CP_MODE, lim_mode= limit_type,
                                ref=ref, lim_ref= limit_ref)
        #limit_ref << 32 | ref<<16 | limit_type.value << 4 | 3<<1 | 1
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_wait_mode(self, limit_type: DrvEpcLimitE, limit_ref: int) -> None:
        """Set the WAIT mode with a specific limit type and limit reference.

        Args:
            limit_type (DrvEpcLimitE): [Type of limit dessired to have]
            limit_ref (int): [Reference for the limit imposed,
                depending on the limit units will be mV/mA/dW/ms]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.MODE.value
        data_msg= union_control(enable= False, mode= DrvEpcModeE.WAIT, lim_mode= limit_type,
                                ref=0, lim_ref= limit_ref)
        #limit_ref << 32 | 0<<16 | limit_type.value << 4 | 0<<1 | 0
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def disable(self) -> None:
        """
        Disable the output
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.MODE.value
        data_msg= union_control(enable= False, mode= DrvEpcModeE.WAIT, lim_mode= DrvEpcLimitE.TIME,
                                ref=0, lim_ref= 10) # 10 << 32 | 0<<16 | 0 << 4 | 0<<1 | 0
        msg = DrvCanMessageC(addr= id_msg, size= 8, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

    def set_periodic(self, # pylint: disable= too-many-arguments
                     ack_en: bool = False, ack_period: int = 10,
                     elect_en: bool = False, elect_period: int = 10,
                     temp_en: bool = False, temp_period: int = 10):
        """Set the periodic messages for the device .

        Args:
            ack_en (bool, optional): [description]. Defaults to False. \
            ack_period (int, optional): [Period to reset the device in 
            case it has not receive any message, the units are ms]. Defaults to 10. \
            elect_en (bool, optional): [description]. Defaults to False. \
            elect_period (int, optional): [Period in which the epc will send electric measures,
              the units are ms]. Defaults to 10. \
            temp_en (bool, optional): [description]. Defaults to False. \
            temp_period (int, optional): [Period in which the epc will send temperature measures,
              the units are ms]. Defaults to 10. \
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.PERIODIC.value
        # In order to send all the values in the same message the values as to be shifted
        # Following the specifications of the epc messages, the first bit of every 16 is to enable
        # the different periodic messages, the following 15 correspond to the period desired
        data_msg= (temp_period << 33 | temp_en<<32 | elect_period<<17
                 | elect_en << 16 | ack_period<<1 | ack_en)
        msg = DrvCanMessageC(addr= id_msg, size= 6, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_volt_limit(self, max_lim: int, min_lim: int):
        """Set the Low Side voltage limits on the device.

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.LS_VOLT_LIM.value
        data_msg= union_limits(max_lim, min_lim)
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_curr_limit(self, max_lim: int, min_lim: int):
        """Set the Low Side current limit on the device.

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.LS_CURR_LIM.value
        data_msg= union_limits(max_lim, min_lim)
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_hs_volt_limit(self, max_lim: int, min_lim: int):
        """Set the high side voltage limit of the device .

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.HS_VOLT_LIM.value
        data_msg= union_limits(max_lim, min_lim)
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_ls_pwr_limit(self, max_lim: int, min_lim: int):
        """Set the low side `power` limit of the device

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.LS_PWR_LIM.value
        data_msg= union_limits(max_lim, min_lim)
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def set_temp_limit(self, max_lim: int, min_lim: int):
        """Set the temperature limits of the device .

        Args:
            max_lim (int): [description]
            min_lim (int): [description]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.TEMP_LIM.value
        data_msg= union_limits(max_lim, min_lim)
        msg = DrvCanMessageC(addr= id_msg, size= 4, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)

    def get_data(self, update: bool = False) -> DrvEpcDataC:
        """Getter to the private attribute of live_data.
        Before returning the info it check if there is any message in can queue
        and update the attributes. If update is false, it won´t send the request messages
        to the epc and return the last values of the attributes. This can be useful in order to 
        not jam the can bus when the periodic messages are enable.
        
        Args:
            update (bool): [Choose between (True) sending a request message to the device
                  and update all the data or (False) just read the last updated attributes]
        Returns:
            [DrvEpcDataC]: [Return ]
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
        and update the attributes.
        If update is false, it won´t send the request messages
        to the epc and return the last values of the attributes. This can be useful in order to 
        not jam the can bus when the periodic messages are enable.
        
        Args:
            update (bool): [Choose between (True) sending a request message to the device
                  and update all the data or (False) just read the last updated attributes]
        Returns:
            [DrvEpcPropertiesC]: [description]
        """
        if update:
            self.get_info()
            self.get_temp_limits()
            self.get_hs_volt_limits()
            self.get_ls_curr_limits()
            self.get_ls_pwr_limits()
            self.get_ls_volt_limits()
        self.read_can_buffer()
        return self.__properties

    def get_info(self) -> DrvEpcPropInfoC:
        """Get the current temperature limits .

        Returns:
            DrvEpcPropInfoC: [Object with attributes: sw_verion, hw_version, can_id, serial_number]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 0x0
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return DrvEpcPropInfoC(self.__properties.sw_version,
                               ba2int(self.__properties.hw_version),
                               self.__properties.can_id,
                               self.__properties.serial_number)

    def get_mode(self) -> DrvEpcDataCtrlC:
        """Get the current mode.

        Returns:
            DrvEpcDataCtrlC: [Object with attributes: mode, limit, ref and limit_ref]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 1
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()

        return DrvEpcDataCtrlC(self.__live_data.mode, self.__live_data.ref,
                                self.__live_data.lim_mode, self.__live_data.lim_ref)

    def get_status(self) -> DrvEpcStatusC:
        """Get the status of the device .

        Returns:
            DrvEpcDataCtrlC: [Object with the errors of the device, 
            been the attributes the following:
            error_code, error
            The value of the error code is a string with the hexadecimal value]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 2
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__live_data.status

    def get_elec_meas(self, periodic_flag: bool= False) -> DrvEpcDataElectC:
        """Get the current electric measures of the device.
        The units of the electric measures are the same as the epc has.
        In this case mV mA dW

        Returns:
            [DrvEpcDataElectC]: [Object with the voltage, current and power in low side 
                    and voltage in high side as attributes]
        """
        if not periodic_flag:
            # The id send is the union of the device can id and type of the message to send
            id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
            data_msg = 3
            msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
            self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return DrvEpcDataElectC(self.__live_data.ls_voltage, self.__live_data.ls_current,
                                self.__live_data.ls_power, self.__live_data.hs_voltage)

    def get_temp_meas(self, periodic_flag: bool = False) -> DrvEpcDataTempC:
        """Get the current temperatures measure of the device.
        The units of the temperature measures are the same as the epc has.
        In this case dºC

        Returns:
            [DrvEpcDataTempC]: [Object with the 3 possible temperatures the device can measure
                    body_temperature, anode_temperature, ambient_temperature as attributes]
        """
        if not periodic_flag:
            # The id send is the union of the device can id and type of the message to send
            id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
            data_msg = 4
            msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
            self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return DrvEpcDataTempC(self.__live_data.temp_body, self.__live_data.temp_amb,
                               self.__live_data.temp_anod)

    def get_ls_volt_limits(self) -> DrvEpcLimitsC:
        """Get the low side voltage limits .

        Returns:
            DrvEpcLimitsC: [Object with attributes: max, min]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 6
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.ls_volt_limit

    def get_ls_curr_limits(self) -> DrvEpcLimitsC:
        """Get the low side current limits .

        Returns:
            DrvEpcLimitsC: [Object with attributes: max, min]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 7
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.ls_curr_limit

    def get_hs_volt_limits(self) -> DrvEpcLimitsC:
        """Get the high side voltage limits for the device .

        Returns:
            DrvEpcLimitsC: [Object with attributes: max, min]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 8
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.hs_volt_limit

    def get_ls_pwr_limits(self) -> DrvEpcLimitsC:
        """Get the LWM limit limits .

        Returns:
            DrvEpcLimitsC: [Object with attributes: max, min]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 9
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.ls_pwr_limit

    def get_temp_limits(self) -> DrvEpcLimitsC:
        """Get the current temperature limits .

        Returns:
            DrvEpcLimitsC: [Object with attributes: max, min]
        """
        # The id send is the union of the device can id and type of the message to send
        id_msg = self.__properties.can_id | _EpcMsgTypeE.REQUEST.value
        data_msg = 0xA
        msg = DrvCanMessageC(addr= id_msg, size= 1, data = data_msg)
        self.__send_to_can(DrvCanCmdTypeE.MESSAGE, msg)
        self.read_can_buffer()
        return self.__properties.temp_limit

    def open(self) -> None:
        """Open a device filter .

        Args:
            addr (int): [addr of the device]
            mask (int): [mask apply to the addr in order to save the can messages]
        """
        open_filter = DrvCanFilterC(self.__properties.can_id,
                    _ConstC.MASK_CAN_DEVICE, self.__device_handler)
        self.__send_to_can(DrvCanCmdTypeE.ADD_FILTER, open_filter)
        # Once the device can receive messages it has to know which hw version has
        # in order to identificate which sensors are present
        self.get_properties(update= True)
        self.get_data(update= True)

    def close(self) -> None:
        """Close the current device, and delete all messages in handler
        """
        self.read_can_buffer()
        close_filter = DrvCanFilterC(self.__properties.can_id,
                    _ConstC.MASK_CAN_DEVICE, self.__device_handler)
        self.__send_to_can(DrvCanCmdTypeE.REMOVE_FILTER, close_filter)
        self.__device_handler.delete_until_last()

#######################             FUNCTIONS              #######################

def union_limits(max_value: int, min_value:int) -> int:
    """Returns the union of the maximum and minimum value, in order to be send by can.
    Following the specifications of the device messages,
    the first 16 bits correspond to the max value and the following 16 to the min values.
    So the min value needs to be shifted 16 to the left

    Args:
        max_value ([int]): [Max value to apply]
        min_value ([int]): [Min value to apply]

    Returns:
        int: []
    """
    return min_value << 16 | max_value

def union_control(enable:bool, mode:DrvEpcModeE,
                  lim_mode: DrvEpcLimitE, ref:int, lim_ref:int) -> int:
    """Return a union control number .

    Args:
        enable (bool): [Bool to describe if the output is enable or not]
        mode (DrvEpcModeE): [Mode desired]
        lim_mode (DrvEpcLimitE): [Type of limit desired]]
        ref (int): [Value to set as reference]
        lim_ref (int): [Value given for the limit]

    Returns:
        int: [description]
    """
    return lim_ref << 32 | ref<<16 | lim_mode.value << 4 | mode.value<<1 | int(enable)
