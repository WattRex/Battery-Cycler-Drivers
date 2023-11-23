 #!/usr/bin/python3
'''
Example of use of drv flow.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
import os
import sys
from threading import Event
from time import sleep
from signal import signal, SIGINT
from serial import EIGHTBITS, PARITY_NONE, PARITY_ODD, STOPBITS_ONE, Serial
#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

from system_shared_tool import SysShdIpcChanC

#######################          PROJECT IMPORTS         #######################
sys.path.append(os.getcwd())
from drv_scpi.src.scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC, DrvScpiCmdTypeE

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

__SERIAL_PORT = '/dev/ttyACM0'
__RX_CHAN_NAME = 'rx_scpi_device' #'rx_scpi_flow'
__FLOW_MAX_MSG = 100
__FLOW_MSG_SIZE = 250
__SOURCE_MAX_MSG = 100
__SOURCE_MSG_SIZE = 250
__TX_NAME_CHAN = 'TX_SCPI'

def example_with_flowmeter():
    '''
    Example of raw usage of drv_scpi with a flowmeter device.
    '''
    flow_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,
                                        separator = '\n',
                                        baudrate = 19200,
                                        bytesize = EIGHTBITS,
                                        parity = PARITY_NONE,
                                        stopbits = STOPBITS_ONE ,
                                        timeout = 2, #0.00003,
                                        write_timeout = None,
                                        inter_byte_timeout  = None)

    rx_chan = SysShdIpcChanC(name=__RX_CHAN_NAME, max_msg=__FLOW_MAX_MSG,
                             max_message_size= __FLOW_MSG_SIZE)

    cmd = DrvScpiCmdDataC(DrvScpiCmdTypeE.ADD_DEV, port=__SERIAL_PORT,\
                payload = flow_conf_scpi, rx_chan_name=__RX_CHAN_NAME)
    tx_chan.send_data(cmd)

    req_meas = ':MEASure:FLOW?'
    cmd_req_meas = DrvScpiCmdDataC(DrvScpiCmdTypeE.WRITE_READ, port=__SERIAL_PORT, payload=req_meas)
    while working_flag.is_set():
        tx_chan.send_data(cmd_req_meas)
        sleep(0.1)
        recv = False
        while not recv:
            if not rx_chan.is_empty():
                resp = rx_chan.receive_data(timeout = 1.0)
                log.info(f"Meas received: {resp}, {resp.payload}")
                recv = True


def example_with_source_ea():
    '''
    Example of raw usage of drv_scpi with a source_ea device.
    '''
    source_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,
                                          separator = '\n',
                                          baudrate = 9600,
                                          bytesize = EIGHTBITS,
                                          parity = PARITY_ODD,
                                          stopbits = STOPBITS_ONE ,
                                          timeout = 2,
                                          write_timeout = None,
                                          inter_byte_timeout  = None)

    msg1 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV, port = __SERIAL_PORT,\
                           payload = source_conf_scpi, rx_chan_name=__RX_CHAN_NAME)

    msg2 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, port = __SERIAL_PORT, \
                           payload = 'SYSTem:LOCK: ON')

    msg3 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, port = __SERIAL_PORT, \
                           payload = 'OUTPut: ON')

    msg4 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ, port = __SERIAL_PORT, \
                           payload = 'MEASure:VOLTage?')
    msg5 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE, port = __SERIAL_PORT, \
                           payload = 'OUTPut: OFF')

    for msg in [msg1, msg2, msg3, msg4, msg5]:
        tx_chan.send_data(msg)
        sleep(0.1)

    recv = False
    while (working_flag.is_set() and not recv):
        sleep(0.1)
        if not rx_chan.is_empty():
            resp = rx_chan.receive_data(timeout = 1.0)
            log.info(f"Meas received: {resp}, {resp.payload}")
            recv = True

    msg6 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV, port = __SERIAL_PORT)
    tx_chan.send_data(msg6)

def raw_example_flow() -> None:
    '''
    Quick test to check the conectivity with the device.
    '''
    serial = Serial(port = '/dev/ttyACM0',
                    baudrate = 9600,
                    bytesize = EIGHTBITS,
                    parity = PARITY_NONE,
                    stopbits = STOPBITS_ONE,
                    timeout = 1, #0.00003,
                    write_timeout = 1, #0.003,
                    inter_byte_timeout  = 1)

    read_info = 'IDN*?'
    get_meas  = ':MEASure:FLOW?'

    read_info_send = (read_info + '\n').encode()
    read_meas_send = (get_meas + '\n').encode()
    empty_msg = bytes(('\n').encode())

    serial.write(empty_msg)
    serial.write(empty_msg)
    read = serial.readline()
    read = serial.readline()

    serial.write(bytes(read_info_send))
    read = serial.readline()
    log.info(f"Read: {read}")


    serial.write(bytes(read_meas_send))
    read = serial.readline()
    log.info(f"Read: {read}")


def signal_handler(sig, frame) -> None: # pylint: disable=unused-argument
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
    cls_msg = DrvScpiCmdDataC(DrvScpiCmdTypeE.DEL_DEV, port=__SERIAL_PORT)
    working_flag.clear()
    tx_chan.send_data(cls_msg)
    rx_chan.terminate()
    tx_chan.terminate()
    sys.exit(0)


if __name__ == '__main__':
    tx_chan = SysShdIpcChanC(name = __TX_NAME_CHAN)
    rx_chan = SysShdIpcChanC(name=__RX_CHAN_NAME, max_msg=__SOURCE_MAX_MSG,
                             max_message_size= __SOURCE_MSG_SIZE)
    working_flag = Event()
    working_flag.set()
    signal(SIGINT, signal_handler)
    # example_with_flowmeter()
    example_with_source_ea()
    # raw_example_flow()
