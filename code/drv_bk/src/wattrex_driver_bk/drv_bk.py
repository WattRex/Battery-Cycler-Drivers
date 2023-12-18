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
                      DEFAULT_TIME_BETWEEN_ATTEMPTS)

#######################              ENUMS               #######################
_MILI_UNITS = 1000
_MAX_PWR = DEFAULT_MAX_VOLT * DEFAULT_MAX_CURR #W

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

class _ScpiCmds(Enum):
    INIT_DEV_SPEED = 'VOLT:DC:NPLC '+ _DrvBkIntegrationRateE.MEDIUM.value
    READ_INFO = ':IDN*?'
    CHANGE_MODE = 'FUNC '

#######################             CLASSES              #######################
class DrvBkPropertiesC(DrvBasePwrPropertiesC):
    "Properties of bk device"
    def __init__(self, model: str|None = None, serial_number: str|None = None,
                 MAX_VOLT: int = 0, MAX_CURR: int = 0,
                 MAX_PWR: int = 0) -> None:
        super().__init__(model, serial_number, MAX_VOLT, MAX_CURR, MAX_PWR)


class DrvBkDataC(DrvBasePwrDataC):
    "Data class of bk device"
    def __init__(self, mode: DrvBkModeE, status: DrvBaseStatusC,
                 voltage: int, current: int, power: int) -> None:
        super().__init__(status = status, mode = mode, voltage = voltage,
                         current = current, power = power)


class DrvBkDeviceC(DrvBasePwrDeviceC):
    "Principal class of bk device"
    def __init__(self, config: DrvScpiSerialConfC) -> None:
        super().__init__()
        self.__tx_chan = SysShdIpcChanC(name = DEFAULT_TX_CHAN)
        self.__rx_chan = SysShdIpcChanC(name = DEFAULT_RX_CHAN+'_'+config.port,
                                        max_msg= DEFAULT_MAX_MSG,
                                        max_message_size= DEFAULT_MAX_MESSAGE_SIZE)
        self.__port = config.port
        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                  port = config.port,
                                  payload = config,
                                  rx_chan_name = DEFAULT_RX_CHAN+'_'+config.port)
        self.__rx_chan.delete_until_last()
        self.__tx_chan.send_data(add_msg)
        self.last_data: DrvBkDataC = DrvBkDataC(mode = DrvBkModeE.VOLT_AUTO,
                                                     status = DrvBaseStatusC(DrvBaseStatusE.OK),
                                                     voltage = 0, current = 0, power = 0)

        self.properties: DrvBkPropertiesC = DrvBkPropertiesC(model= None,
                                                            serial_number= None,
                                                            MAX_VOLT= 0, MAX_CURR= 0, MAX_PWR= 0)
        self.__initialize_control()
        self.__read_device_properties()

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
            if 'ERROR' not in msg.payload[0]:
                if 'IDN' in msg.payload[0]:
                    info = msg.payload[0].split(',')
                    model = info[0]
                    serial_number = info[-1]
                    self.properties = DrvBkPropertiesC(model = model, serial_number = serial_number,
                                                         MAX_VOLT = DEFAULT_MAX_VOLT * _MILI_UNITS,
                                                         MAX_CURR = DEFAULT_MAX_CURR * _MILI_UNITS,
                                                         MAX_PWR = _MAX_PWR * _MILI_UNITS)
                elif 'FETC' in msg.payload[0]:
                    response: list = findall(r"-?\d*\.?\d+", msg.payload[0])
                    if len(response) < 2:
                        response = float(response[0])
                    else:
                        response = float(response[0]) * 10 ** int(response[1])
                    response = int(response * _MILI_UNITS)
                    status = DrvBaseStatusC(DrvBaseStatusE.OK)

                    if self.last_data.mode.value.split(':')[0] == 'VOLT':
                        voltage = response
                    elif self.last_data.mode.value.split(':')[0] == 'CURR':
                        current = response
                    self.last_data = DrvBkDataC(mode = self.last_data.mode, status = status,
                                                    voltage = voltage, current = current, power = 0)
                else:
                    log.error(f'Unknown message received: {msg.payload[0]}')
            else:
                log.error(msg.payload[0])
        else:
            log.error('Unknown message type received')

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
                        payload= _ScpiCmds.INIT_DEV_SPEED)
        self.__tx_chan.send_data(msg)
        time_init = time()
        while (time()-time_init) < DEFAULT_MAX_WAIT_TIME:
            sleep(DEFAULT_TIME_BETWEEN_ATTEMPTS)
            self.__parse_msg()
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
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, port= self.__port,
                        payload= DrvBkModeE.VOLT_AUTO.value)
        self.__tx_chan.send_data(msg)

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
                        payload= _ScpiCmds.READ_INFO)
        self.__tx_chan.send_data(msg)
        info: DrvScpiCmdDataC = self.__rx_chan.receive_data()
        if hasattr(info, 'payload'):
            info = info.payload.split(',')
            model = info[0]
            serial_number = info[-1]
        else:
            model = None
            serial_number = None
        self.properties = DrvBkPropertiesC(model = model, serial_number = serial_number,
                                             MAX_VOLT = DEFAULT_MAX_VOLT * _MILI_UNITS,
                                             MAX_CURR = DEFAULT_MAX_CURR * _MILI_UNITS,
                                             MAX_PWR = _MAX_PWR * _MILI_UNITS)


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
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                    port= self.__port, payload= _ScpiCmds.CHANGE_MODE + mode_cod))
        #Change range of the mode
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                    port= self.__port,payload= meas_mode.value))
        self.last_data.mode = meas_mode


    def get_data(self) -> DrvBkDataC:
        '''Read the device measures.
        Args:
            - None.
        Returns:
            - (DrvBkDataC): Returns the device measures.
        Raises:
            - None
        '''
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                    port= self.__port, payload= 'FETC?'))
        return self.last_data
        # current = 0
        # voltage = 0
        # status = DrvBaseStatusE(DrvBaseStatusE.COMM_ERROR)
        # #Read measure
        # self.device_handler.send_and_read('FETC?')
        # response = self.device_handler.receive_msg()[0]
        # if response != '':
        #     response = self.device_handler.decode_numbers(response)
        #     response = int(response * _MILI_UNITS)
        #     status = DrvBaseStatusE(DrvBaseStatusE.OK)

        #     if self.last_data.mode.value.split(':')[0] == 'VOLT':
        #         voltage = response
        #     elif self.last_data.mode.value.split(':')[0] == 'CURR':
        #         current = response
        # else:
        #     status = DrvBaseStatusE(DrvBaseStatusE.COMM_ERROR)

        # self.last_data = DrvBkDataC(mode = self.last_data.mode, status = status,
        #                                 voltage = voltage, current = current, power = 0)
        # return self.last_data


    def get_properties(self) -> DrvBkPropertiesC:
        '''Read the device properties.
        Args:
            - None.
        Returns:
            - (DrvBkPropertiesC): Returns the device properties.
        Raises:
            - None.
        '''
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
        self.__tx_chan.send_data(DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                    port= self.__port))
        self.__tx_chan.close()
        self.__rx_chan.close()
