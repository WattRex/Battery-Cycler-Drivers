#!/usr/bin/python3
'''
Driver of bms.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from enum import Enum
#######################       THIRD PARTY IMPORTS        #######################
from datetime import datetime, timedelta
#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
log = sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position
from system_config_tool import sys_conf_read_config_params
#######################          PROJECT IMPORTS         #######################
from can_sniffer import DrvCanCmdTypeE, DrvCanCmdDataC, DrvCanFilterC, DrvCanMessageC
from wattrex_driver_base import DrvBaseStatusE, DrvBaseStatusC

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
_MAX_MSG = 100
_MAX_MESSAGE_SIZE = 400
_TX_CHAN = 'TX_CAN'
_RX_CHAN = 'RX_CAN_BMS'
_MEASURE_NAMES = ['vcell1', 'vcell2', 'vcell3', 'vcell4', 'vcell5', 'vcell6', 'vcell7', 'vcell8',
                    'vcell9', 'vcell10', 'vcell11', 'vcell12', 'vstack', 'temp1', 'temp2', 'temp3',
                    'temp4', 'pres1', 'pres2']
_TIMEOUT_RESPONSE = 30

class _BmsStatusE(Enum):
    "Modes of the device"
    ERROR_NONE = 0x00
    ERROR_HW = 0x01
    ERROR_COMM = 0x02
    ERROR_V_STACKS = 0x04
    ERROR_LEAKAGE = 0x08
    ERROR_TEMP = 0x10
    ERROR_PRES = 0x20

#######################             CLASSES              #######################
class DrvBmsDataC(): #pylint: disable=too-many-instance-attributes
    '''
    Class method to create a DRVDB model of database BMS.
    '''
    def __init__(self, list_measures: list) -> None:
        log.debug(f"Writting data: {list_measures}")
        self.__status = DrvBaseStatusC(DrvBaseStatusE.OK)
        self.vcell1: int = 0
        self.vcell2: int = 0
        self.vcell3: int = 0
        self.vcell4: int = 0
        self.vcell5: int = 0
        self.vcell6: int = 0
        self.vcell7: int = 0
        self.vcell8: int = 0
        self.vcell9: int = 0
        self.vcell10: int = 0
        self.vcell11: int = 0
        self.vcell12: int = 0
        # self.vcell13: int = 0
        # self.vcell14: int = 0
        # self.vcell15: int = 0
        # self.vcell16: int = 0
        # self.vcell17: int = 0
        # self.vcell18: int = 0
        # self.vcell19: int = 0
        # self.vcell20: int = 0
        # self.vcell21: int = 0
        # self.vcell22: int = 0
        # self.vcell23: int = 0
        # self.vcell24: int = 0
        # self.vcell25: int = 0
        self.vstack: int = 0
        self.temp1: int = 0
        self.temp2: int = 0
        self.temp3: int = 0
        self.temp4: int = 0
        # self.temp5: int = 0
        # self.temp6: int = 0
        self.pres1: int = 0
        self.pres2: int = 0

        if len(list_measures) == len(_MEASURE_NAMES):
            self.status: DrvBaseStatusC = DrvBaseStatusC(DrvBaseStatusE.OK)
            for count, value in enumerate(_MEASURE_NAMES):
                setattr(self, value, list_measures[count])
        elif len(list_measures) == 0:
            pass
        else:
            log.error(f"The number of measures is not correct: {len(list_measures)}")

    @property
    def status(self) -> DrvBaseStatusC:
        """Property to get the attribute status
        """
        return self.__status

    @status.setter
    def status(self, new_status : DrvBaseStatusC | DrvBaseStatusE) -> None:
        """Setter for the status attribute

        Args:
            new_status (DrvBaseStatusC): [description]
        """
        if isinstance(new_status, DrvBaseStatusC):
            self.__status = new_status
        elif isinstance(new_status, DrvBaseStatusE):
            self.__status = DrvBaseStatusC(new_status)

    def __str__(self) -> str:
        """
        Returns a string representation of the BMS data.

        The string contains the voltage and temperature measurements of the BMS,
        as well as its status.

        Returns:
            str: A string representation of the BMS data.
        """
        return (f"vcell1: {self.vcell1} vcell2: {self.vcell2}\n"
                f"vcell3: {self.vcell3} vcell4: {self.vcell4}\n"
                f"vcell5: {self.vcell5} vcell6: {self.vcell6}\n"
                f"vcell7: {self.vcell7} vcell8: {self.vcell8}\n"
                f"vcell9: {self.vcell9} vcell10: {self.vcell10}\n"
                f"vcell11: {self.vcell11} vcell12: {self.vcell12}\n"
                f"vstack: {self.vstack}\n"
                f"temp1: {self.temp1} temp2: {self.temp2}\n"
                f"temp3: {self.temp3} temp4: {self.temp4}\n"
                f"pres1: {self.pres1} pres2: {self.pres2}\n"
                f"status: {self.status}")


class DrvBmsDeviceC: #pylint: disable=too-many-instance-attributes
    "Principal class of BMS"
    def __init__(self, dev_id: int, can_id: int, rx_chan_name: str|None = None,
                 config_file: str|None = None) -> None:
        """Constructor of the class."""
        if config_file is not None:
            config = sys_conf_read_config_params(config_file, section= 'bms')
            for param in config:
                if param == 'RX_CHANNEL':
                    global _RX_CHAN # pylint: disable=global-statement
                    _RX_CHAN = config[param]
                elif param == 'TX_CHANNEL':
                    global _TX_CHAN # pylint: disable=global-statement
                    _TX_CHAN = config[param]
                elif param == 'MAX_MSG':
                    global _MAX_MSG # pylint: disable=global-statement
                    _MAX_MSG = config[param]
                elif param == 'MAX_MESSAGE_SIZE':
                    global _MAX_MESSAGE_SIZE # pylint: disable=global-statement
                    _MAX_MESSAGE_SIZE = config[param]
                elif param == 'TIMEOUT_RESPONSE':
                    global _TIMEOUT_RESPONSE # pylint: disable=global-statement
                    _TIMEOUT_RESPONSE = config[param]
                else:
                    log.error(f"Parameter {param} not found in config file")
        self.dev_id= dev_id
        self.__can_id: int = (int(0x100) | can_id) & 0x7FF
        log.info(f"Device ID: {self.dev_id: 03x}")
        self.__data = DrvBmsDataC([])
        self.__data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        self.__tx_chan = SysShdIpcChanC(name = _TX_CHAN)
        if rx_chan_name is None:
            rx_chan_name = _RX_CHAN
        self.__rx_chan_name = rx_chan_name + '_' + str(f'{self.__can_id & 0x00F:02x}')
        self.__rx_chan = SysShdIpcChanC(name = self.__rx_chan_name,
                                      max_msg = _MAX_MSG,
                                      max_message_size = _MAX_MESSAGE_SIZE)
        filter_bms = DrvCanFilterC(addr=self.__can_id, mask=0x7FF, chan_name=self.__rx_chan_name)
        add_msg = DrvCanCmdDataC(data_type = DrvCanCmdTypeE.ADD_FILTER,
                                payload = filter_bms)
        self.__tx_chan.send_data(add_msg)
        self.status: DrvBaseStatusC = DrvBaseStatusC(DrvBaseStatusE.OK)
        self.__last_recv_ts: datetime = datetime.now()
        self.__reset_raw_data()


    def get_data(self) -> DrvBmsDataC:
        """Read data from the server .

        Returns:
            DrvBmsDataC: [description]
        """
        while not self.__rx_chan.is_empty():
            raw_data: DrvCanMessageC = self.__rx_chan.receive_data_unblocking()
            self._defragment(raw_data.payload)
        # Check if message receive between expected time
        if self.__last_recv_ts + timedelta(seconds=_TIMEOUT_RESPONSE) < datetime.now():
            if self.__data.status == DrvBaseStatusC(DrvBaseStatusE.OK):
                self.__data.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
            log.error(f"Timeout on communication with BMS: {self.__data.status}")
            self.__reset_raw_data()
            self.__last_recv_ts = datetime.now()
        return self.__data

    def __reset_raw_data(self) -> None:
        """Reset the raw data to the initial value .
        """
        self.__raw_data = []
        self.__next_idx_frag = 0


    def _defragment(self, data) -> None:
        '''
        Defragment the message received from BMS with dev_id. When all fragments has 
        been received and defragmented, the resulting message is parsed and stored
        into the local data.

        Args:
            id (int): Identificator of the sender bms.
            data ([type]): Data to be defragmented.
        '''
        # Prase ids and frags
        frag_idx = 0xF & data[0]
        n_frags = data[0] >> 4

        # ---------------------------------------------------------------------

        # Deframnet error code
        if frag_idx == 0 and n_frags == 1 and str(data[1:]).startswith("ERROR"):
            recv_status = _BmsStatusE(int(data[7]))
            if recv_status == _BmsStatusE.ERROR_COMM:
                self.__data.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
            log.warning(f"Error fragment received on BMS: {self.__data.status}")

        # Normal parse, parse normal message
        else:
            if self.__next_idx_frag != frag_idx:
                log.error((f"ERROR on [0x{self.dev_id:03x}] - Not received all fragment. "
                           f"Expected frag: {self.__next_idx_frag}. Recv frag: {frag_idx}"))
                self.__data.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
                self.__reset_raw_data()
            else:
                self.__raw_data.extend(data[1:])

                # Prepare for new fragment reception
                self.__next_idx_frag += 1
                # Parse all received data
                if frag_idx == n_frags-1:
                    if len(self.__raw_data) % 2 != 0:
                        log.error("Error on communication with BMS: Not received all fragment")
                        self.__data.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
                        self.__reset_raw_data()
                    else:
                        # Iterate self.__raw_data every 2 elements and combine them into one int
                        new_data = []
                        for i in range(0, len(self.__raw_data), 2):
                            new_elem = self.__raw_data[i+1] << 8 | self.__raw_data[i]
                            new_data.append(new_elem)

                        self.__data = DrvBmsDataC(new_data)
                        ## RESET TIMEOUT
                        self.__last_recv_ts = datetime.now()
                        self.__data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
                        log.info(f"Data received from BMS: {str(self.__data)}")
                        self.__reset_raw_data()


    def close(self) -> None:
        ''' Close the serial port.'''
        del_msg = DrvCanCmdDataC(data_type = DrvCanCmdTypeE.REMOVE_FILTER,
                                payload = DrvCanFilterC(addr=self.dev_id, mask=0x7FF,
                                                        chan_name=self.__rx_chan_name))
        self.__tx_chan.send_data(del_msg)
        self.__rx_chan.terminate()
