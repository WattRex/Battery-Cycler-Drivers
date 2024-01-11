#!/usr/bin/python3
'''
This module will manage SCPI messages and channels
in order to configure channels and send/received messages.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from typing import Dict
from signal import signal, SIGINT

#######################       THIRD PARTY IMPORTS        #######################
from threading import Event

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import system_logger_tool as sys_log
if __name__ == "__main__":
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdNodeC, SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
from .drv_scpi_iface import DrvScpiHandlerC # pylint: disable=wrong-import-position
from .drv_scpi_cmd import DrvScpiCmdDataC, DrvScpiCmdTypeE # pylint: disable=wrong-import-position

#######################              ENUMS               #######################

######################             CONSTANTS              ######################
from .context import (DEFAULT_CHAN_NUM_MSG, DEFAULT_MAX_MSG_SIZE, DEFAULT_TX_CHAN,
                      DEFAULT_NODE_NAME, DEFAULT_NODE_PERIOD)

#######################             CLASSES              #######################
class DrvScpiNodeC(SysShdNodeC):
    "Returns a removable version of the DRV command."
    def __init__(self, working_flag: Event, cycle_period: int= DEFAULT_NODE_PERIOD,
                 name: str = DEFAULT_NODE_NAME):
        '''
        Args:
            - working_flag (Event): Flag to know if the SCPI is working.
            - cycle_period (int): Period of the cycle in miliunits.
        Raises:
            - None.
        '''
        self.__used_dev: Dict(str, DrvScpiHandlerC) = {}
        self.tx_scpi: SysShdIpcChanC = SysShdIpcChanC(name = DEFAULT_TX_CHAN,
                                                      max_msg= DEFAULT_CHAN_NUM_MSG,
                                                      max_message_size= DEFAULT_MAX_MSG_SIZE)
        self.tx_scpi.delete_until_last()
        super().__init__(name = name, cycle_period = cycle_period,\
                        working_flag = working_flag)
        signal(SIGINT, self.signal_handler)


    def __apply_command(self, cmd: DrvScpiCmdDataC) -> None:
        '''Apply the command received from the SCPI channel.
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
            if cmd.port in self.__used_dev.keys(): #pylint: disable= consider-iterating-dictionary
                log.warning("Device already exist")
            else:
                self.__used_dev[cmd.port] = DrvScpiHandlerC(serial_conf = cmd.payload,
                                rx_chan_name = cmd.rx_chan_name)
                log.info("Device added")
            log.info(f"List of devices added: {self.__used_dev.keys()}")

        # Delete device
        elif cmd.data_type == DrvScpiCmdTypeE.DEL_DEV:
            dev_handler: DrvScpiHandlerC = self.__used_dev[cmd.port]
            dev_handler.close()
            del self.__used_dev[cmd.port]
            log.info("Device deleted")

        # Write or Write and read
        elif cmd.data_type in (DrvScpiCmdTypeE.WRITE, DrvScpiCmdTypeE.WRITE_READ):
            handler: DrvScpiHandlerC  = self.__used_dev[cmd.port]
            handler.send(cmd.payload)
            if cmd.data_type == DrvScpiCmdTypeE.WRITE_READ:
                handler.wait_4_response = True

        # Error
        else:
            log.error("Message not valid")


    def __receive_response(self) -> None:
        '''Read the devices that are waiting to send a message.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        for handler in self.__used_dev.values():
            handler: DrvScpiHandlerC
            handler.read()
            # if handler.wait_4_response:
            #     handler.read()
            #     handler.read()

    def process_iteration(self) -> None:
        ''' Read the chan.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        if not self.tx_scpi.is_empty():
            command : DrvScpiCmdDataC = self.tx_scpi.receive_data() # type: ignore
            if (command.data_type is DrvScpiCmdTypeE.ADD_DEV) or (command.port in self.__used_dev):
                log.info((f"Port: {command.port.split('/')[-1]}. "+
                        f"Command to apply: {command.data_type.name}"))
                self.__apply_command(command)
            else:
                log.error("First add device.")
        self.__receive_response()


    def stop(self) -> None:
        '''Stop the SCPI node.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''
        log.info("Stopping SCPI node...")
        for device in self.__used_dev.values():
            device.close()
        self.working_flag.clear()
        self.__used_dev.clear()
        self.tx_scpi.terminate()
        log.info("SCPI node stopped")


    def sync_shd_data(self) -> None:
        '''Synchronize the shared data.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - None.
        '''


    def signal_handler(self, sig, frame) -> None: # pylint: disable=unused-argument
        '''Detect control-c and stop the SCPI node.
        Args:
            - sig.
            - frame
        Returns:
            - None.
        Raises:
            - None.
        '''
        log.info("control-c detected. Stopping SCPI node...")
        self.stop()
