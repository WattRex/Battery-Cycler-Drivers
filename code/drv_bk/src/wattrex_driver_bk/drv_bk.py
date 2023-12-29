#!/usr/bin/python3
'''
Driver of multimeter.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from re import findall
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
    ## TODO: Cambiar todas los valores de los modos a los correctos

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
    ## TODO: Cambiar todas los valores de los modos a los correctos

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
    def __init__(self, model: str|None = None, serial_number: str|None = None,
                 MAX_VOLT: int = 0, MAX_CURR: int = 0,
                 MAX_PWR: int = 0) -> None:
        super().__init__(model, serial_number, MAX_VOLT, MAX_CURR, MAX_PWR)


class DrvBkDataC(DrvBasePwrDataC):
    "Data class of bk device"
    def __init__(self, mode: DrvBkModeE, range: DrvBkRangeE, status: DrvBaseStatusC,
                 voltage: int, current: int, power: int) -> None:
        self.range: DrvBkRangeE = range
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
        self.last_data: DrvBkDataC = DrvBkDataC(mode = DrvBkModeE.VOLT_DC, range= DrvBkRangeE.AUTO,
                                                     status = DrvBaseStatusC(DrvBaseStatusE.OK),
                                                     voltage = 0, current = 0, power = 0)

        self.properties: DrvBkPropertiesC = DrvBkPropertiesC(model= None,
                                                            serial_number= None,
                                                            MAX_VOLT= 0, MAX_CURR= 0, MAX_PWR= 0)
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

    def __exp_number(self,str_msg) -> int|None:
        """
        Converts a string representation of a number in scientific notation to an integer.
        
        Args:
            str_msg (str): The string representation of the number in scientific notation.
        
        Returns:
            int|None: The converted integer value if successful, None otherwise.
        """
        response = None
        if all([var.isnumeric() for var in str_msg.split('e')]):
            msg_sci = str_msg.split('e')
            if len(msg_sci) == 2:
                response = float(msg_sci[0]) * 10 ** int(msg_sci[1])
            else:
                response = float(msg_sci[0])
        return int(response*_MILI_UNITS)

    def __parse_msg(self) -> None:
        '''Parse the message received from the device.
        Args:
            - msg (DrvScpiCmdDataC): Message received from the device.
        Returns:
            - None.
        Raises:
            - None.
        '''
        msg: DrvScpiCmdDataC = self.__rx_chan.receive_data_unblocking()
        if msg is not None and msg.data_type == DrvScpiCmdTypeE.RESP:
            log.critical(f"Message received: {msg.payload}")
            for data in msg.payload:
                if len(data) >0 and not str(data).startswith(":"):
                    data = self.__exp_number(data) if self.__exp_number(data) is not None else data
                    if isinstance(data, str):
                        if 'volt' in data:
                            if 'ac' in data:
                                self.last_data.mode = DrvBkModeE.VOLT_AC
                            else:
                                self.last_data.mode = DrvBkModeE.VOLT_DC
                        elif 'curr' in data:
                            if 'ac' in data:
                                self.last_data.mode = DrvBkModeE.CURR_AC
                            else:
                                self.last_data.mode = DrvBkModeE.CURR_DC
                        elif 'NO ERROR' in data:
                            self.last_data.status = DrvBaseStatusE.OK
                        elif 'ERROR' in data:
                            self.last_data.status = DrvBaseStatusE.COMM_ERROR
                        elif len(data.split(',')) == 3:
                            data = data.split(',')
                            self.properties = DrvBkPropertiesC(model = data[0],
                                            serial_number = data[1],
                                            MAX_VOLT = DEFAULT_MAX_VOLT * _MILI_UNITS,
                                            MAX_CURR = DEFAULT_MAX_CURR * _MILI_UNITS,
                                            MAX_PWR = _MAX_PWR * _MILI_UNITS)
                            log.info(f"Serial number: {data[-1]}")
                            log.info(f"Model: {data[0]}")
                        log.info(f"Response: {data}")
                    else:
                        if self.last_data.mode in (DrvBkModeE.VOLT_DC, DrvBkModeE.VOLT_AC):
                            self.last_data.voltage = data
                        else:
                            self.last_data.current = data
                        log.info(f"Value read: {data}")
            # if 'ERROR' not in msg.payload[0]:
            #     if all([var.isnumeric() for var in msg.payload[0].split('e')]):
            #         msg_sci = msg.payload[0].split('e')
            #         if len(msg_sci) == 2:
            #             response = float(msg_sci[0]) * 10 ** int(msg_sci[1])
            #         else:
            #             response = float(msg_sci[0])
            #         if self.last_data.mode in (DrvBkModeE.VOLT_DC, DrvBkModeE.VOLT_AC):
            #             self.last_data.voltage = int(response * _MILI_UNITS)
            #         else:
            #             self.last_data.current = int(response * _MILI_UNITS)
            #     if _ScpiCmds.READ_INFO.value in msg.payload[0]:
            #         info = msg.payload[1].split(',')
            #         model = info[0]
            #         serial_number = info[-1]
            #         self.properties = DrvBkPropertiesC(model = model,
            #                                          serial_number = serial_number,
            #                                          MAX_VOLT = DEFAULT_MAX_VOLT * _MILI_UNITS,
            #                                          MAX_CURR = DEFAULT_MAX_CURR * _MILI_UNITS,
            #                                          MAX_PWR = _MAX_PWR * _MILI_UNITS)
        #         if _ScpiCmds.READ_DATA.value in msg.payload[0]:
        #             response: list = findall(r"-?\d*\.?\d+", msg.payload[0])
        #             if len(response) < 2:
        #                 response = float(response[0])
        #             else:
        #                 response = float(response[0]) * 10 ** int(response[1])
        #             response = int(response * _MILI_UNITS)
        #             status = DrvBaseStatusC(DrvBaseStatusE.OK)

        #             if self.last_data.mode.value.split(':')[0] == 'VOLT':
        #                 voltage = response
        #             elif self.last_data.mode.value.split(':')[0] == 'CURR':
        #                 current = response
        #             self.last_data = DrvBkDataC(mode = self.last_data.mode, status = status,
        #                                             voltage = voltage, current = current, power = 0)
        #         if _ScpiCmds.READ_MODE.value in msg.payload[0]:
        #             mode_loc= msg.payload[0].replace("b'",
        #                     "").replace("\\n'","").split(";").index(_ScpiCmds.READ_MODE.value) + 1
        #             if "volt:dc" in msg.payload[mode_loc]:
        #                 self.last_data.mode = DrvBkModeE.VOLT_DC
        #             elif "curr:dc" in msg.payload[mode_loc]:
        #                 self.last_data.mode = DrvBkModeE.CURR_DC
        #             elif "volt:ac" in msg.payload[mode_loc]:
        #                 self.last_data.mode = DrvBkModeE.VOLT_AC
        #             elif "curr:ac" in msg.payload[mode_loc]:
        #                 self.last_data.mode = DrvBkModeE.CURR_AC
        #             log.info(f"Mode set to: {self.last_data.mode}")
        #         if _ScpiCmds.INIT_DEV_SPEED.value in msg.payload[0]:
        #             log.info(f"Device speed set to: {msg.payload[0].split(' ')[-1]}")
        #     else:
        #         log.error(msg.payload[0])
        elif msg is None:
            pass
        else:
            log.error(f'Unknown message type received: {msg.__dict__}')

    def __initialize_control(self) -> None:
        '''Initialize the device control.
        Args:
            - None.
        Returns:    
            - None.
        Raises:
            - None.
        '''
        exception = True
        #Initialize device speed
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port= self.__port,
                        payload= _ScpiCmds.INIT_DEV_SPEED.value)
        self.__tx_chan.send_data(msg)
        time_init = time()
        while (time()-time_init) < DEFAULT_MAX_WAIT_TIME:
            sleep(DEFAULT_TIME_BETWEEN_ATTEMPTS)
            self.read_buffer()
        #     if not self.__rx_chan.is_empty():
        #         command_rec : DrvScpiCmdDataC = self.__rx_chan.receive_data()
        #         msg_rcv = command_rec.payload[0]
        #         if len(msg_rcv) > 0 and ('ERROR' not in msg_rcv) and ('IDN' in msg_rcv):
        #             exception = False
        #         else:
        #             self.__tx_chan.send_data(msg)
        # self.__rx_chan.delete_until_last()
        # if exception:
        #     raise ConnectionError("Device not found")
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
        # info = self.device_handler.read_device_info()
        # info = info[1].split()
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port= self.__port,
                        payload= _ScpiCmds.READ_INFO.value)
        self.__tx_chan.send_data(msg)
        self.read_buffer()
        if self.properties.model is None:
            raise ConnectionError("Device not found")


    def set_mode(self, meas_mode: DrvBkModeE, range: DrvBkRangeE = DrvBkRangeE.AUTO) -> None:
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
                                    payload=":"+mode_cod.value+range.value))
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
                                payload= _ScpiCmds.READ_DATA.value+";"+_ScpiCmds.READ_MODE.value))
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
