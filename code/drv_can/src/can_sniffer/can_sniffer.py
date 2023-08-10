#!/usr/bin/python3
"""
This module will manage CAN messages and channels
in order to configure channels and send/received messages.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
import threading
from typing import Any, Iterable, Callable, Mapping
from enum import Enum


#######################       THIRD PARTY IMPORTS        #######################
from can import ThreadSafeBus, Message, CanOperationError
from system_shared_tool import SysShdChanC
import system_logger_tool as sys_log

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
if __name__ == '__main__':
    cycler_logger = sys_log.SysLogLoggerC()
log = sys_log.sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################


#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################


#######################             CLASSES              #######################

_TIMEOUT_SEND_MSG : float = 0.2
_TIMEOUT_RX_MSG : float = 0.02
_MAX_DLC_SIZE : int = 8

class DrvCanCmdTypeE(Enum):
    """
    Type of command for the CAN
    """
    MESSAGE = 0
    ADD_FILTER = 1
    REMOVE_FILTER = 2

class DrvCanMessageC:
    """The class to create messages correctly to be send by can .
    """
    def __init__(self, addr : int, size : int, data : int | bytearray) -> None:
        '''
        Initialize a CAN message.

        Args:
            addr (int): CAN datafrane addres.
            size (int): Message payload size on bytes.
            data (int): Can message payload.

        Raises:
            BytesWarning: Throw an exception if the payload size of message is too long (size > 8).
        '''
        self.addr = addr
        self.dlc = size
        if self.dlc > _MAX_DLC_SIZE:
            log.error(f"Message payload size on bytes (size = {self.dlc}) \
                      is higher than {_MAX_DLC_SIZE}")
            raise BytesWarning("To many element for a CAN message")
        if isinstance(data,int):
            self.data = data.to_bytes(size, byteorder='little', signed = True)
        else:
            self.data = data

class DrvCanFilterC():
    """This class is used to create objects that
    works as messages to make write or erase filters in can .
    """
    def __init__(self, addr : int, mask : int, chan):
        if 0 <= addr <= 0x7FF:
            self.addr = addr
        else:
            log.error("Wrong value for address, value must be between 0-0x7ff")
            raise ValueError

        if 0 <= mask <= 0x7FF:
            self.mask = mask
        else:
            log.error("Wrong value for mask, value must be between 0 and 0x7ff")
            raise ValueError

        if isinstance(chan, SysShdChanC):
            self.chan = chan
        else:
            log.error("Wrong type for channel, must be a SysShdChanC object")
            raise ValueError
    def match(self, id_can: int) -> bool:
        """Checks if the id_can matches with the selected filter.

        Args:
            id_can (int): [complete id of the message received by can]
        """
        aux = False
        if (id_can & self.mask) == (self.addr & self.mask):
            aux = True
        return aux

class DrvCanCmdDataC():
    """
    Returns a function that can be called when the command is not available .
    """
    def __init__(self, data_type: DrvCanCmdTypeE, payload: DrvCanMessageC|DrvCanFilterC):
        self.data_type = data_type
        self.payload = payload

class DrvCanParamsC:
    """
    Class that contains the can parameters in order to create the thread correctly
    """
    def __init__(self, target: Callable[..., object] | None = ...,
        name: str | None = ..., args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = ..., *, daemon: bool | None = ...):
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.daemon = daemon

class DrvCanNodeC(threading.Thread):
    """Returns a removable version of the DRv command .

    Args:
        threading ([type]): [description]
    """

    def __init__(self, tx_buffer: SysShdChanC,
        working_flag : threading.Event, can_params: DrvCanParamsC =
        DrvCanParamsC()) -> None:
        '''
        Initialize the thread node used to received messages from CAN network.

        Args:
            chanPlak (SysShdChanC): Chan used to store messages received from plaks.
            chanEPC (SysShdChanC): Chan used to store messages received from EPCs.
        '''

        super().__init__(group = None, target = can_params.target, name = can_params.name,
                         args = can_params.args, kwargs = can_params.kwargs,
                         daemon = can_params.daemon)
        self.working_flag = working_flag
        # cmd_can_down = 'sudo ip link set down can0'
        self.__can_bus : ThreadSafeBus = ThreadSafeBus(interface='socketcan',
                                channel='can0', bitrate=125000,
                                receive_own_messages=False, fd=True)
        self.__can_bus.flush_tx_buffer()

        self.tx_buffer: SysShdChanC = tx_buffer

        self.__active_filter = []


    def __parse_msg(self, message: DrvCanMessageC) -> None:
        '''
        Check if the received message matches any of the active filter, in case it matches will
        add that message to the specific queue of the filter

        Args:
            message (DrvCanMessageC): Message received from CAN
        '''
        #Search if the message id match any active filter
        # if true, add the message to that queue
        for act_filter in self.__active_filter:
            if act_filter.match(message.addr):
                act_filter.chan.send_data(message)
                break

    def __apply_filter(self, add_filter : DrvCanFilterC) -> None:
        '''Created a shared object and added it to the active filter list

        Args:
            data_frame (DrvCanFilterC): Filter to apply.
        '''
        self.__active_filter.append(add_filter)
        log.debug("Filter added correctly")

    def __remove_filter(self, del_filter : DrvCanFilterC) -> None:
        '''Delete a shared object from the active filter list

        Args:
            del_filter (DrvCanFilterC): Filter to remove.
        '''
        self.__active_filter.remove(del_filter)
        log.debug("Filter removed correctly")

    def __send_message(self, data : DrvCanMessageC) -> None:
        '''Send a CAN message

        Args:
            data (DrvCanMessageC): Messsage to send.

        Raises:
            err (CanOperationError): Raised when error with CAN connection occurred
        '''
        msg = Message(arbitration_id=data.addr, is_extended_id=False,
                    dlc=data.dlc, data=bytes(data.data))
        try:
            self.__can_bus.send(msg, timeout=_TIMEOUT_SEND_MSG)
            log.debug("Message correctly send")
        except CanOperationError as err:
            log.error(err)
            raise err
        # log.debug(f"CAN Message sent: \tarbitration_id :
        # {msg.arbitration_id:04X} \tdlc : {msg.dlc} \tdata :
        # 0x{data_frame.data}, 0x{data_frame.data.hex()}")

    def __apply_command(self, command : DrvCanCmdDataC) -> None:
        '''Apply a command to the CAN drv of the device.

        Args:
            command (DrvCanCmdDataC): Data to process, does not know if its for the channel or
            a message to a device

        Raises:
            err (CanOperationError): Raised when error with CAN connection occurred
        '''
        #Check which type of command has been received and matchs the payload type
        if (command.data_type == DrvCanCmdTypeE.MESSAGE
            and isinstance(command.payload,DrvCanMessageC)):
            self.__send_message(command.payload)
        elif (command.data_type == DrvCanCmdTypeE.ADD_FILTER
            and isinstance(command.payload,DrvCanFilterC)):
            log.info(f"Adding new filter with id {hex(command.payload.addr)} "+
                        f"and mask {hex(command.payload.mask)}")
            self.__apply_filter(command.payload)
        elif (command.data_type == DrvCanCmdTypeE.REMOVE_FILTER
            and isinstance(command.payload,DrvCanFilterC)):
            log.info(f"Removing filter with id {hex(command.payload.addr)} "+
                        f"and mask {hex(command.payload.mask)}")
            self.__remove_filter(command.payload)
        else:
            log.error("Can`t apply command. \
                      Error in command format, check command type and payload type")


    def stop(self) -> None:
        """
        Stop the CAN thread .
        """
        log.critical("Stopping CAN thread.")
        self.__can_bus.shutdown()
        self.working_flag.clear()

    def run(self) -> None:
        '''
        Main method executed by the CAN thread. It receive data from EPCs and PLAKs
        and store it on the corresponding chan.
        '''
        log.info("Start running process")
        while self.working_flag.isSet():
            try:
                if not self.tx_buffer.is_empty():
                    # Ignore warning as receive_data return an object,
                    # which in this case must be of type DrvCanCmdDataC
                    command : DrvCanCmdDataC = self.tx_buffer.receive_data() # type: ignore
                    log.debug(f"Command to apply: {command.data_type.name}")
                    self.__apply_command(command)
                msg : Message = self.__can_bus.recv(timeout=_TIMEOUT_RX_MSG)
                if isinstance(msg,Message):
                    if (0x000 <= msg.arbitration_id <= 0x7FF
                        and not msg.is_error_frame):
                        self.__parse_msg(DrvCanMessageC(msg.arbitration_id,msg.dlc,msg.data))
                    else:
                        log.error(f"Message receive can`t be parsed, id: {hex(msg.arbitration_id)}"+
                                  f" and frame: {msg.is_error_frame}")
            except Exception as err:
                log.error(f"Error while sending CAN message\n{err}")
        log.critical("Stop can working")
        self.stop()
#######################            FUNCTIONS             #######################
