#!/usr/bin/python3
"""
This module will manage CAN messages and channels
in order to configure channels and send/received messages.
"""
#######################        MANDATORY IMPORTS         #######################
import sys
if sys.version_info < (3, 8):
    from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from threading import Thread, Event
from typing import Any, Iterable, Callable, Mapping
from enum import Enum
from can import ThreadSafeBus, Message, CanOperationError

#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger, SysLogLoggerC, Logger

#######################       LOGGER CONFIGURATION       #######################
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='../log_config.yaml')
log: Logger = sys_log_logger_get_module_logger(__name__)

from system_shared_tool import SysShdIpcChanC
#######################          MODULE IMPORTS          #######################


#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################


#######################             CLASSES              #######################
_MAX_MESSAGE_SIZE: int = 250
_TIMEOUT_SEND_MSG : float = 0.2
_TIMEOUT_RX_MSG : float = 0.02
_MAX_DLC_SIZE : int = 8
_MIN_ID          = 0x000     # As the last 4 bits will identify the messages are reserved
_MAX_ID          = 0x7FF     # In standard mode the can id max value is 0x7FF
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
            self.data = data.to_bytes(size, byteorder='little', signed = False)
        else:
            self.data = data

class DrvCanFilterC():
    """This class is used to create objects that
    works as messages to make write or erase filters in can .
    """
    def __init__(self, addr : int, mask : int, chan_name: str):
        if _MIN_ID <= addr <= _MAX_ID:
            self.addr = addr
        else:
            log.error("Wrong value for address, value must be between 0-0x7ff")
            raise ValueError("Wrong value for address, value must be between 0-0x7ff")

        if _MIN_ID <= mask <= _MAX_ID:
            self.mask = mask
        else:
            log.error("Wrong value for mask, value must be between 0 and 0x7ff")
            raise ValueError("Wrong value for mask, value must be between 0 and 0x7ff")

        self.chan_name = chan_name
        self.chan: SysShdIpcChanC|None = None

    def open_chan(self):
        """Open the channel to use for communication with Posix .
        """
        self.chan: SysShdIpcChanC = SysShdIpcChanC(name= self.chan_name, max_message_size= 150)

    def close_chan(self):
        """Closes the communication channel .
        """
        self.chan.terminate()

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

class DrvCanNodeC(Thread):
    """Returns a removable version of the DRv command .

    Args:
        threading ([type]): [description]
    """

    def __init__(self, tx_buffer_size: int,
        working_flag : Event, can_params: DrvCanParamsC =
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

        self.tx_buffer: SysShdIpcChanC = SysShdIpcChanC(name='TX_CAN',
                                            max_msg = int(tx_buffer_size),
                                            max_message_size= _MAX_MESSAGE_SIZE)

        self.__active_filter: list = []

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
        already_in = False
        for act_filter in self.__active_filter:
            if act_filter.addr == add_filter.addr and act_filter.mask == add_filter.mask:
                already_in = True
                if act_filter.chan_name == add_filter.chan_name:
                    log.warning("Filter already added")
                else:
                    log.error("Filter already added with different channel name")
                    raise ValueError("Filter already added with different channel name")
        if not already_in:
            log.info(f"Adding new filter with id {hex(add_filter.addr)} "+
            f"and mask {hex(add_filter.mask)}")
            add_filter.open_chan()
            self.__active_filter.append(add_filter)
            log.debug("Filter added correctly")

    def __remove_filter(self, del_filter : DrvCanFilterC) -> None:
        '''Delete a shared object from the active filter list

        Args:
            del_filter (DrvCanFilterC): Filter to remove.
        '''
        already_out = True
        filter_pos=0
        for act_filter in self.__active_filter:
            if act_filter.addr == del_filter.addr and act_filter.mask == del_filter.mask:
                already_out = False
                if act_filter.chan_name == del_filter.chan_name:
                    log.info(f"Removing filter with id {hex(del_filter.addr)} "+
                        f"and mask {hex(del_filter.mask)}")
                    filter_chn: DrvCanFilterC = self.__active_filter.pop(filter_pos)
                    filter_chn.close_chan()
                    log.debug("Filter removed correctly")
                else:
                    log.error("Filter in with different channel name")
                    raise ValueError("Filter already added with different channel name")
            else:
                filter_pos += 1
        if already_out:
            log.warning("Filter already removed")

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
            self.__apply_filter(command.payload)
        elif (command.data_type == DrvCanCmdTypeE.REMOVE_FILTER
            and isinstance(command.payload,DrvCanFilterC)):
            self.__remove_filter(command.payload)
        else:
            log.error("Can`t apply command. \
                      Error in command format, check command type and payload type")


    def stop(self) -> None:
        """
        Stop the CAN thread .
        """
        log.critical("Stopping CAN thread.")
        for filters in self.__active_filter:
            filters.close_chan()
        self.working_flag.clear()
        self.tx_buffer.terminate()
        self.__can_bus.shutdown()

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
                                  f" and error in frame is: {msg.is_error_frame}")
            except CanOperationError as err:
                log.error(f"Error while sending CAN message\n{err}")
            except ValueError as err:
                log.error(f"Error while applying/removing filter with error {err}")
            except Exception:
                log.error("Error in can thread")
                self.working_flag.clear()
        log.critical("Stop can working")
        self.stop()
#######################            FUNCTIONS             #######################
