 #!/usr/bin/python3
'''
Example of use of drv flow.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
import os
from sys import path
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, Serial
from time import sleep
from signal import signal, SIGINT
from threading import Event
#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

from system_shared_tool import SysShdIpcChanC

#######################          PROJECT IMPORTS         #######################
path.append(os.getcwd())
from drv_scpi.src.scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC,\
    DrvScpiCmdTypeE, DrvScpiNodeC, TX_NAME_CHAN, SCPI_MAX_MSG, SCPI_MAX_MESSAGE_SIZE

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
__SERIAL_PORT = '/dev/ttyACM0'
__RX_CHAN_NAME = 'rx_scpi_flow'

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

    rx_chan = SysShdIpcChanC(name=__RX_CHAN_NAME, max_msg=SCPI_MAX_MSG,\
                             max_message_size= SCPI_MAX_MESSAGE_SIZE)

    cmd = DrvScpiCmdDataC(DrvScpiCmdTypeE.ADD_DEV, port=__SERIAL_PORT,\
                payload = flow_conf_scpi, rx_chan_name=__RX_CHAN_NAME)
    global tx_chan
    tx_chan.send_data(cmd)

    REQ_MEAS = ':MEASure:FLOW?'
    cmd_req_meas = DrvScpiCmdDataC(DrvScpiCmdTypeE.WRITE_READ, port=__SERIAL_PORT, payload=REQ_MEAS)
    global working_flag
    while working_flag.isSet():
        tx_chan.send_data(cmd_req_meas)
        sleep(0.1)
        recv = False
        while not recv:
            if not rx_chan.is_empty():
                resp = rx_chan.receive_data(timeout = 1.0)
                log.info(f"Meas received: {resp}, {resp.payload}")
                recv = True

def quick_test() -> None:
    "Quick test to check the conectivity with the device."
    serial = Serial(port = '/dev/ttyACM0',
                    baudrate = 9600,
                    bytesize = EIGHTBITS,
                    parity = PARITY_NONE,
                    stopbits = STOPBITS_ONE,
                    timeout = 1, #0.00003,
                    write_timeout = 1, #0.003,
                    inter_byte_timeout  = 1)

    READ_INFO = 'IDN*?'
    GET_MEAS  = ':MEASure:FLOW?'

    read_info_send = (READ_INFO + '\n').encode()
    read_meas_send = (GET_MEAS + '\n').encode()
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

    # while 1:
    #     read = serial.readline()
    #     log.info(f"Read: {read}")

    # sleep(1)
    # serial.write(bytes(GET_MEAS.encode("utf-8")))
    # meas = serial.readline()
    # print(meas)
    # data_dec = meas.decode("utf-8")
    # log.info(f"Meas: {data_dec}")

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
    global tx_chan
    cls_msg = DrvScpiCmdDataC(DrvScpiCmdTypeE.DEL_DEV, port=__SERIAL_PORT)
    global working_flag
    working_flag.clear()
    tx_chan.send_data(cls_msg)



if __name__ == '__main__':
    tx_chan = SysShdIpcChanC(name = TX_NAME_CHAN, max_msg= SCPI_MAX_MSG,\
                                max_message_size= SCPI_MAX_MESSAGE_SIZE)
    working_flag = Event()
    working_flag.set()
    signal(SIGINT, signal_handler)
    example_with_flowmeter()
    # quick_test()
