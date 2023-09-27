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
from .drv_scpi_cmd import DrvScpiCmdDataC, DrvScpiCmdTypeE, DrvScpiSerialConfC

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class DrvScpiNodeC:
    "Returns a removable version of the DRV command."
    def __init__(self, working_flag: Event, tx_scpi_long: int):
        self.__used_dev: Dict(str, DrvScpiHandlerC) = {}
        self.working_flag: Event = working_flag
        max_message_size = 300 #TODO: averiguar el numero al final, con el máximo mensaje que le envío
        self.tx_scpi: SysShdIpcChanC = SysShdIpcChanC(name = "cola_SCPI", max_msg= max_message_size, max_message_size= tx_scpi_long)


    def __apply_command(self, cmd: DrvScpiCmdDataC) -> None:
        '''TODO: Poner titulo.
        Args:
            - cmd (DrvScpiCmdDataC): Message to apply.
        Returns:
            - None.
        Raises:
            - None.
        '''
        # Add device
        if cmd.data_type == DrvScpiCmdTypeE.ADD_DEV:
            log.info("Adding device...")
            if cmd.port in self.__used_dev:
                log.error("Device already exist")
            else:
                if isinstance(cmd.payload, DrvScpiSerialConfC):
                    self.__used_dev[cmd.port] = DrvScpiHandlerC(serial_conf = cmd.payload)
                    log.info("Device added")
                else:
                    log.error("The device could not be added")

        # Delete device
        elif cmd.data_type == DrvScpiCmdTypeE.DEL_DEV:
            log.info("Deleting device...")
            if cmd.port in self.__used_dev:
                del self.__used_dev[cmd.port]
                log.info("Device deleted")
            else:
                log.error("The device could not be deleted")

        # Write or Write and read
        elif cmd.data_type == DrvScpiCmdTypeE.WRITE or cmd.data_type == DrvScpiCmdTypeE.WRITE_READ:
            if cmd.port in self.__used_dev:
                if isinstance(cmd.payload, str):
                    handler: DrvScpiHandlerC  = self.__used_dev[cmd.port]
                    handler.send(cmd.payload)
                    if cmd.data_type == DrvScpiCmdTypeE.WRITE_READ:
                        handler.wait_4_response = True
                else:
                    log.error("Message not valid")
            else:
                log.error("First add device")

        # Error
        else:
            log.error("Can`t apply command")


    def __receive_response(self) -> None:
        '''TODO: Poner titulo.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        for __, handler in self.__used_dev.items():
            handler: DrvScpiHandlerC
            if handler.wait_4_response:
                handler.read()


    def process_iteration(self) -> None:
        ''' Read the chan.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        try:
            if not self.tx_scpi.is_empty():
                # Ignore warning as receive_data return an object,
                # which in this case must be of type DrvScpiCmdDataC
                command : DrvScpiCmdDataC = self.tx_scpi.receive_data() # type: ignore
                log.critical(f"COMANDO:\n{command.__dict__}\n")
                log.info(f"Command to apply: {command.data_type.name}") # pylint: disable=logging-fstring-interpolation
                self.__apply_command(command)
                self.__receive_response()
            else:
                log.info("Queue is empty")
        except ValueError as err:
            log.error(f"Error while applying/removing filter with error {err}") # pylint: disable=logging-fstring-interpolation
        except Exception: # pylint: disable=broad-except
            log.error("Error in SCPI thread")
            self.working_flag.clear()








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
