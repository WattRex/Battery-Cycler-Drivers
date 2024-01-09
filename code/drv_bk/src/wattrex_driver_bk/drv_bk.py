#!/usr/bin/python3
'''
Driver of multimeter.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################
from enum import Enum
from time import time, sleep

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC
#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC, DrvScpiCmdTypeE
from wattrex_driver_base import (DrvBasePwrPropertiesC, DrvBasePwrDataC, DrvBaseStatusC,
        DrvBaseStatusE, DrvBasePwrDeviceC)

#######################          MODULE IMPORTS          #######################

######################             CONSTANTS              ######################
from .context import (DEFAULT_MAX_VOLT, DEFAULT_MAX_CURR, DEFAULT_TX_CHAN, DEFAULT_RX_CHAN,
                      DEFAULT_MAX_MSG, DEFAULT_MAX_MESSAGE_SIZE, DEFAULT_MAX_WAIT_TIME,
                      DEFAULT_TIME_BETWEEN_ATTEMPTS, DEFAULT_MAX_READS)

#######################              ENUMS               #######################
_MILI_UNITS = 1000
_MAX_PWR = DEFAULT_MAX_VOLT * DEFAULT_MAX_CURR #W

class DrvBkModeE(Enum):
    "Modes of the device"
    VOLT_DC = 1
    CURR_DC = 2
    VOLT_AC = 3
    CURR_AC = 4
    RESISTANCE = 5
class DrvBkModeCmdE(Enum):
    "Commands to change between modes of the device"
    VOLT_DC = 'VOLT:DC'
    CURR_DC = 'CURR:DC'
    VOLT_AC = 'VOLT:AC'
    CURR_AC = 'CURR:AC'
    ### Trabajo futuro no aplicable al ciclador
    RESISTANCE = 'RES'

class DrvBkRangeE(Enum):
    "Modes of the device"
    AUTO        = ':RANGE:AUTO ON'
    R2_MILI_A   = ':RANGE 0.002'
    R20_MILI_A  = ':RANGE 0.02'
    R200_MILI   = ':RANGE 0.2'
    R2          = ':RANGE 2'
    R20         = ':RANGE 20'
    R200_V      = ':RANGE 200'
    R1000_V     = ':RANGE 1000'

class _DrvBkIntegrationRateE(Enum):
    "Integration rate of the device"
    SLOW = '10'
    MEDIUM = '1'
    FAST = '0.1'

class _ScpiCmds(Enum):
    INIT_DEV_SPEED= ":VOLT:DC:NPLC "+ str(_DrvBkIntegrationRateE.FAST.value)
    READ_INFO= "*IDN?"
    CHANGE_MODE= ":FUNC "
    READ_MODE= ":FUNC?"
    READ_DATA= ":FETC?"

#######################             CLASSES              #######################
class DrvBkPropertiesC(DrvBasePwrPropertiesC):
    "Properties of bk device"
    def __init__(self, model: str|None = None, serial_number: str|None = None, #pylint: disable= useless-parent-delegation
                 max_volt: int = 0, max_curr: int = 0,
                 max_pwr: int = 0) -> None:
        super().__init__(model, serial_number, max_volt, max_curr, max_pwr)


class DrvBkDataC(DrvBasePwrDataC):
    "Data class of bk device"
    def __init__(self, mode: DrvBkModeE, meas_range: DrvBkRangeE, status: DrvBaseStatusC, #pylint: disable= too-many-arguments
                 voltage: int, current: int, power: int) -> None:
        self.range: DrvBkRangeE = meas_range
        super().__init__(status = status, mode = mode, voltage = voltage,
                         current = current, power = power)


class DrvBkDeviceC(DrvBasePwrDeviceC):
    "Principal class of bk device"
    def __init__(self, config: DrvScpiSerialConfC) -> None:
        super().__init__()
        self.__tx_chan = SysShdIpcChanC(name = DEFAULT_TX_CHAN)
        self.__rx_chan = SysShdIpcChanC(name = DEFAULT_RX_CHAN+'_'+config.port.split('/')[-1],
                                        max_msg= DEFAULT_MAX_MSG,
                                        max_message_size= DEFAULT_MAX_MESSAGE_SIZE)
        self.__port = config.port
        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                  port = config.port,
                                  payload = config,
                                  rx_chan_name = DEFAULT_RX_CHAN+'_'+config.port.split('/')[-1])
        self.__rx_chan.delete_until_last()
        self.__tx_chan.send_data(add_msg)
        self.last_data: DrvBkDataC = DrvBkDataC(mode = DrvBkModeE.VOLT_DC,
                                            meas_range = DrvBkRangeE.AUTO,
                                            status = DrvBaseStatusC(DrvBaseStatusE.OK),
                                            voltage = 0, current = 0, power = 0)

        self.properties: DrvBkPropertiesC = DrvBkPropertiesC(model= None,
                                                            serial_number= None,
                                                            max_volt = 0, max_curr = 0, max_pwr = 0)
        self.__initialize_control()
        self.read_buffer()
        self.__read_device_properties()
        self.read_buffer()

    def read_buffer(self) -> None:
        '''Read the buffer of the device.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        i = 0
        while i < DEFAULT_MAX_READS or not self.__rx_chan.is_empty():
            self.__parse_msg()
            i += 1

    def __exp_number(self,str_msg: str) -> int|None:
        """
        Converts a string representation of a number in scientific notation to an integer.
        
        Args:
            str_msg (str): The string representation of the number in scientific notation.
        
        Returns:
            int|None: The converted integer value if successful, None otherwise.
        """
        response = None
        if (len(str_msg.split('.')) == 2 and str_msg.split('.')[0].isdigit() and
            str_msg.split('.')[1].split('e')[1].replace('-','').isdigit()):
            response = int(float(str_msg)*_MILI_UNITS)
        return response

    def __parse_msg(self) -> None: #pylint: disable=too-many-branches
        '''Parse the message received from the device.
        Args:
            - msg (DrvScpiCmdDataC): Message received from the device.
        Returns:
            - None.
        Raises:
            - None.
        '''
        msg: DrvScpiCmdDataC = self.__rx_chan.receive_data_unblocking()
        if msg is not None and msg.data_type == DrvScpiCmdTypeE.RESP: #pylint: disable=too-many-nested-blocks
            if hasattr(msg, 'status') and msg.status.value == DrvBaseStatusE.COMM_ERROR: #pylint: disable=attribute-defined-outside-init
                log.critical("ERROR READING DEVICE")
                self.last_data.status = DrvBaseStatusE.COMM_ERROR #pylint: disable=attribute-defined-outside-init
            for data in msg.payload: #pylint: disable=too-many-nested-blocks #pylint: disable=attribute-defined-outside-init
                if len(data) >0 and not str(data).startswith(":"):
                    data = self.__exp_number(data) if self.__exp_number(data) is not None else data
                    if isinstance(data, str):
                        if 'volt' in data:
                            if 'ac' in data:
                                self.last_data.mode = DrvBkModeE.VOLT_AC #pylint: disable=attribute-defined-outside-init
                            else:
                                self.last_data.mode = DrvBkModeE.VOLT_DC #pylint: disable=attribute-defined-outside-init
                        elif 'curr' in data:
                            if 'ac' in data:
                                self.last_data.mode = DrvBkModeE.CURR_AC #pylint: disable=attribute-defined-outside-init
                            else:
                                self.last_data.mode = DrvBkModeE.CURR_DC #pylint: disable=attribute-defined-outside-init
                        elif 'NO ERROR' in data:
                            self.last_data.status = DrvBaseStatusE.OK #pylint: disable=attribute-defined-outside-init
                        elif 'ERROR' in data:
                            self.last_data.status = DrvBaseStatusE.COMM_ERROR #pylint: disable=attribute-defined-outside-init
                        elif len(data.split(',')) == 3:
                            data = data.split(',')
                            self.properties = DrvBkPropertiesC(model = data[0],
                                            serial_number = data[1],
                                            max_volt = DEFAULT_MAX_VOLT * _MILI_UNITS,
                                            max_curr = DEFAULT_MAX_CURR * _MILI_UNITS,
                                            max_pwr  = _MAX_PWR * _MILI_UNITS)
                            log.debug(f"Serial number: {data[-1]}")
                            log.debug(f"Model: {data[0]}")
                        log.debug(f"Response: {data}")
                    else:
                        if self.last_data.mode in (DrvBkModeE.VOLT_DC, DrvBkModeE.VOLT_AC):
                            self.last_data.voltage = data #pylint: disable=attribute-defined-outside-init
                        else:
                            self.last_data.current = data #pylint: disable=attribute-defined-outside-init
                        log.debug(f"Value read: {data}")
        elif msg is None:
            pass
        else:
            log.error(f'Unknown message type received: {msg.__dict__}')

    def __initialize_control(self) -> None:
        '''Initialize the device control.
        '''
        #Initialize device speed
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port= self.__port,
                        payload= _ScpiCmds.INIT_DEV_SPEED.value)
        self.__tx_chan.send_data(msg)
        time_init = time()
        while (time()-time_init) < DEFAULT_MAX_WAIT_TIME:
            sleep(DEFAULT_TIME_BETWEEN_ATTEMPTS)
            self.read_buffer()
        #Initialize device mode in auto voltage
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port= self.__port,
                            payload= f"{_ScpiCmds.CHANGE_MODE.value}{DrvBkModeCmdE.VOLT_DC.value}")
        self.__tx_chan.send_data(msg)
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port= self.__port,
                            payload=f"{DrvBkModeCmdE.VOLT_DC.value}{DrvBkRangeE.AUTO.value}")
        self.__tx_chan.send_data(msg)
        self.read_buffer()

    def __read_device_properties(self) -> None:
        '''Read the device properties .
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port= self.__port,
                        payload= _ScpiCmds.READ_INFO.value)
        self.__tx_chan.send_data(msg)
        i = 0
        while self.properties.model is None and i<=DEFAULT_MAX_READS:
            self.read_buffer()
            sleep(1)
            log.info("Waiting to read device properties")
            i +=1
        if self.properties.model is None:
            raise ConnectionError("Device not found")


    def set_mode(self, meas_mode: DrvBkModeE, meas_range: DrvBkRangeE = DrvBkRangeE.AUTO) -> None:
        '''Set the device mode.
        Args:
            - meas_mode (DrvBkModeE): Mode to set.
        Returns:
            - None.
        Raises:
            - None.
        '''
        self.read_buffer()
        mode_cod = DrvBkModeCmdE[meas_mode.name]
        #Change mode to voltage or current and range all in one
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                    port= self.__port,
                                    payload= _ScpiCmds.CHANGE_MODE.value + mode_cod.value))
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                    port= self.__port,
                                    payload=":"+mode_cod.value+meas_range.value))
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                    port= self.__port,
                                    payload= _ScpiCmds.READ_MODE.value))
        self.read_buffer()


    def get_data(self) -> DrvBkDataC:
        '''Read the device measures.
        Args:
            - None.
        Returns:
            - (DrvBkDataC): Returns the device measures.
        '''
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port= self.__port,
                                payload= _ScpiCmds.READ_DATA.value))
        self.read_buffer()
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port= self.__port,
                                payload= _ScpiCmds.READ_MODE.value))
        self.read_buffer()
        return self.last_data

    def get_properties(self) -> DrvBkPropertiesC:
        '''Read the device properties.
        Args:
            - None.
        Returns:
            - (DrvBkPropertiesC): Returns the device properties.
        '''
        self.read_buffer()
        return self.properties

    def close(self) -> None:
        '''Close communication with the device.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        self.read_buffer()
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                    port= self.__port))
        self.__tx_chan.close()
        self.read_buffer()
        self.__rx_chan.close()
