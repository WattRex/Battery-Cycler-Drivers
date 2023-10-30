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

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
log = sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from can_sniffer import DrvCanCmdTypeE, DrvCanCmdDataC, DrvCanFilterC, DrvCanMessageC
from wattrex_driver_base import DrvBaseStatusE, DrvBaseStatusC

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
_MAX_MSG = 100
_MAX_MESSAGE_SIZE = 400
_TX_CHAN = 'TX_CAN'
_MEASURE_NAMES = ['vcell1', 'vcell2', 'vcell3', 'vcell4', 'vcell5', 'vcell6', 'vcell7', 'vcell8',
                    'vcell9', 'vcell10', 'vcell11', 'vcell12', 'vstack', 'temp1', 'temp2', 'temp3',
                    'temp4', 'pres1', 'pres2']

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
class DrvBmsDataC():
    '''
    Class method to create a DRVDB model of database BMS.
    '''
    def __init__(self, list_measures: list) -> None:
        log.info(f"Writting data: {list_measures}")
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

#     def __str__(self) -> str:
#                 '''
#         Returns:
#             - None.
#         Raises:
#             - None.
#         '''

# TODO: improve comment and add info of bms used


class DrvBmsDeviceC:
    "Principal class of BMS"
    def __init__(self, rx_chan_name: str = 'RX_CAN_BMS', dev_id: int) -> None:

        self.dev_id: int = (int(0x100) | dev_id) & 0x7FF
        log.info(f"Device ID: {self.dev_id: 03x}")
        self.__data = DrvBmsDataC([])
        self.__data.status = DrvBaseStatusC(DrvBaseStatusE.OK)
        self.__tx_chan = SysShdIpcChanC(name = _TX_CHAN)
        self.__rx_chan_name = rx_chan_name + '_' + str(f'{self.dev_id & 0x00F:02x}')
        self.__rx_chan = SysShdIpcChanC(name = self.__rx_chan_name,
                                      max_msg = _MAX_MSG,
                                      max_message_size = _MAX_MESSAGE_SIZE)

        filter = DrvCanFilterC(addr=self.dev_id, mask=0x7FF, chan_name=self.__rx_chan_name)
        add_msg = DrvCanCmdDataC(data_type = DrvCanCmdTypeE.ADD_FILTER,
                                payload = filter)
        self.__tx_chan.send_data(add_msg)
        self.status: DrvBaseStatusC = DrvBaseStatusC(DrvBaseStatusE.OK)
        self.__reset_raw_data()


    def get_data(self) -> DrvBmsDataC:
        """Read data from the server .

        Returns:
            DrvBmsDataC: [description]
        """
        while not self.__rx_chan.is_empty():
            raw_data: DrvCanMessageC = self.__rx_chan.receive_data_unblocking()
            self._defragment(raw_data.payload)
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
                # log.debug(f"Frag {self.dev_id} - [{frag_idx}/{n_frags}]")

                # Prepare for new fragment reception
                self.__next_idx_frag += 1
                # Parse all received data
                if frag_idx == n_frags-1:
                    if len(self.__raw_data) % 2 != 0:
                        log.error(f"Error on communication with BMS: Not received all fragment")
                        self.__data.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
                        self.__reset_raw_data()
                    else:
                        # Iterate self.__raw_data every 2 elements and combine them into one int
                        new_data = []
                        for i in range(0, len(self.__raw_data), 2):
                            new_elem = self.__raw_data[i+1] << 8 | self.__raw_data[i]
                            new_data.append(new_elem)

                        self.__data = DrvBmsDataC(new_data)
                        # add __str__ function
                        log.info(f"Data received from BMS: {self.__data.__dict__}")
                        self.__reset_raw_data()


    def close(self) -> None:
        ''' Close the serial port.'''
        del_msg = DrvCanCmdDataC(data_type = DrvCanCmdTypeE.REMOVE_FILTER,
                                payload = DrvCanFilterC(addr=self.dev_id, mask=0x7FF,
                                                        chan_name=self.__rx_chan_name))
        self.__tx_chan.send_data(del_msg)
        self.__rx_chan.terminate()
