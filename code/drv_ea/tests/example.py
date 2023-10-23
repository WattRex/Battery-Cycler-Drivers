#!/usr/bin/python3
'''
Example to ea power supply.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
import time

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import *
from serial import PARITY_ODD, EIGHTBITS, STOPBITS_ONE, Serial

#######################          MODULE IMPORTS          #######################
from drv_ea.src.wattrex_driver_ea import *
# from wattrex_driver_ea import DrvEaDeviceC

#######################              ENUMS               #######################
__SERIAL_PORT = '/dev/ttyACM0'
__RX_CHAN_NAME = 'rx_scpi_source'
__SCPI_MAX_MSG = 300          # messages per queue
__SCPI_MAX_MESSAGE_SIZE = 400 # bytes per msg

#######################             CLASSES              #######################
def main():
    '''
    Example usage of drv_ea with a source_ea device.
    '''
    source_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,
                                          separator = '\n',
                                          baudrate = 9600,
                                          bytesize = EIGHTBITS,
                                          parity = PARITY_ODD,
                                          stopbits = STOPBITS_ONE ,
                                          timeout = 0.1,
                                          write_timeout = None,
                                          inter_byte_timeout  = None)

    source = DrvEaDeviceC(config = source_conf_scpi, rx_chan_name = __RX_CHAN_NAME)
    log.info(f"properties: {source.properties.model}")
    source.set_cc_mode(curr_ref = 2, voltage_limit = 20000)
    init = time.time()

    while (time.time() - init) < 5:
        data = source.get_data()
        log.info(f"Mode: {data.mode} - Voltage: {data.voltage} - Current: {data.current}")

    source.set_cv_mode(volt_ref = 10000, current_limit = 500)
    init = time.time()
    while (time.time() - init) < 5:
        data = source.get_data()
        log.info(f"Mode: {data.mode} - Voltage: {data.voltage} - Current: {data.current}")
    source.close()


def raw_example_ea_source():
    '''
    Quick test to check the conectivity with the device.
    '''
    serial = Serial(port = '/dev/ttyACM0',
                    baudrate = 9600,
                    bytesize = EIGHTBITS,
                    parity = PARITY_ODD,
                    stopbits = STOPBITS_ONE,
                    timeout = 1, #0.1
                    write_timeout = 1,
                    inter_byte_timeout  = 1)
    READ_INFO = 'IDN*?'
    GET_MEAS  = 'MEASure:ARRay?'
    CURR_NOM  = 'SYSTem:NOMinal:CURRent?'
    VOLT_NOM  = 'SYSTem:NOMinal:VOLTage?'
    POWER = 'SYSTem:NOMinal:POWer?'
    LOCK = 'SYSTem:LOCK:OWNer?'
    LOCK_ON = 'SYSTem:LOCK: ON'
    LOCK_OFF = 'SYSTem:LOCK: OFF'
    OUTPUT_ON = 'OUTPut: ON'
    OUTPUT_OFF = 'OUTPut: OFF'

    read_info_send = (READ_INFO + '\n').encode()
    read_meas_send = (GET_MEAS + '\n').encode()
    empty_msg = bytes(('\n').encode())


    serial.write((LOCK_ON + '\n').encode())
    read = serial.readline()

    ON = False
    if ON:
        serial.write((OUTPUT_ON + '\n').encode())


    msg = 'STAT:OPERation:CONDition?'

    time.sleep(1)
    serial.write((msg + '\n').encode())
    read = serial.readline()
    read_dec = read.decode("utf-8")
    log.info(f"Read: {read} - Dec: {read_dec}")

    '''
    0 = Output off
    256 = CV
    512 = CC
    '''


    # response = serial.write((LOCK_OFF + '\n').encode())
    # log.info (f"Response: {response}")
    # read = serial.readline()
    # log.info(f"Read: {read}")

    # response = serial.write((LOCK + '\n').encode())
    # log.info (f"Response: {response}")
    # read = serial.readline()
    # log.info(f"Read: {read}")


    # serial.write((OUTPUT_ON + '\n').encode())
    # read = serial.readline()
    # log.info(f"Read: {read}")

    # serial.write((GET_MEAS + '\n').encode())
    # read = serial.readline()
    # log.info(f"Read: {read}")




    # serial.write(empty_msg)
    # read = serial.readline()
    # read = serial.readline()

    # serial.write(bytes(read_info_send))
    # read = serial.readline()
    # log.info(f"Read: {read}")


    # serial.write(bytes(read_meas_send))
    # read = serial.readline()
    # log.info(f"Read: {read}")



if __name__ == '__main__':
    main()
    # raw_example_ea_source()
