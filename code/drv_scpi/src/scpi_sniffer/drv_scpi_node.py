#!/usr/bin/python3
'''
This module will manage SCPI messages and channels
in order to configure channels and send/received messages.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from typing import Dict

#######################       THIRD PARTY IMPORTS        #######################
from threading import Event

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log
if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from system_shared_tool import SysShdChanC

#######################          MODULE IMPORTS          #######################
from .drv_scpi_iface import DrvScpiHandlerC
from .drv_scpi_cmd import DrvScpiCmdDataC

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class DrvScpiNodeC:
    "Returns a removable version of the DRV command."
    def __init__(self, working_flag: Event, tx_scpi: SysShdIpcChanC):
        self.__used_dev: Dict(str, DrvScpiHandlerC) = {}
        self.working_flag: Event = working_flag
        self.tx_scpi: SysShdIpcChanC = tx_scpi


    def __apply_command(self, cmd: DrvScpiCmdDataC) -> None:
        '''TODO: Poner titulo.
        Args:
            - cmd (DrvScpiCmdDataC): [description]
        Returns:
            - None
        Raises:
            - None
        '''
        pass


    def __receive_command(self) -> None:
        '''TODO: Poner titulo.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''
        pass


    def run(self) -> None:
        ''' Run the process.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''


    def stop(self) -> None:
        ''' Stop the process.
        Args:
            - None
        Returns:
            - None
        Raises:
            - None
        '''









    # CODIGO VIEJO || BORRAR
    # class DrvScpiNodeC:
    #     '''Returns a removable version of the DRV command.
    #     '''
    #     def __init__(self, tx_buffer: SysShdChanC, working_flag: Event):
    #         self.__used_dev: dict = {}
    #         self.working_flag: Event = working_flag
    #         self.tx_buffer: SysShdChanC = tx_buffer


    #     def __apply_command(self, cmd: DrvScpiCmdDataC):
    #         '''TODO: Poner titulo.
    #         Args:
    #             cmd (DrvScpiCmdDataC): [description]
    #         Returns:
    #             - None
    #         Raises:
    #             - None
    #         '''
    #         #Add device
    #         if cmd.payload is DrvScpiHandlerC:
    #             if cmd.data_type is DrvScipiCmdTypeE.ADD_DEV:
    #                 if self.__used_dev.get(cmd.port) is None:
    #                     self.__used_dev[cmd.port] = cmd.payload
    #                 else:
    #                     log.error("The port is already configured")
    #             else:
    #                 log.error("Can`t apply command. \
    #                         Error in command format, check command type and payload type")

    #         #Send or receive data
    #         elif cmd.payload is str:
    #             message: str = cmd.payload # type: ignore
    #             scpi: DrvScpiHandlerC = self.__used_dev[cmd.port]
    #             if cmd.data_type is DrvScipiCmdTypeE.READ:
    #                 scpi.receive_msg()
    #             elif cmd.data_type is DrvScipiCmdTypeE.WRITE:
    #                 scpi.send_msg(message)
    #             elif cmd.data_type is DrvScipiCmdTypeE.WRITE_READ:
    #                 scpi.send_and_read(message)
    #             else:
    #                 log.error("Can`t apply command. \
    #                         Error in command format, check command type and payload type")


    #     def run(self) -> None:
    #         '''TODO: Poner titulo.
    #         Args:
    #             - None
    #         Returns:
    #             - None
    #         Raises:
    #             - None
    #         '''
    #         log.critical("Start running process")
    #         while self.working_flag.isSet():
    #             try:
    #                 #Tx es salida, transmision. TODO: Falta recibir
    #                 if not self.tx_buffer.is_empty():
    #                     command : DrvScpiCmdDataC = self.tx_buffer.receive_data() # type: ignore
    #                     self.__apply_command(command)
    #             except Exception as err:
    #                 log.error(f"Error while receiving CAN message\n{err}")
    #         self.stop()


    #     def stop(self) -> None:
    #         '''TODO: Poner titulo.
    #         Args:
    #             - None
    #         Returns:
    #             - None
    #         Raises:
    #             - None
    #         '''
    #         log.critical("Stopping SCPI thread.")
    #         self.working_flag.clear()
