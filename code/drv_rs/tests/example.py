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
from serial import PARITY_ODD, EIGHTBITS, STOPBITS_ONE

#######################          MODULE IMPORTS          #######################
from drv_rs.src.wattrex_driver_rs import *
# from wattrex_driver_rs import DrvRsDeviceC

#######################              ENUMS               #######################
__SERIAL_PORT = '/dev/ttyACM0'
__RX_CHAN_NAME = 'rx_scpi_load'
__SCPI_MAX_MSG = 300          # messages per queue
__SCPI_MAX_MESSAGE_SIZE = 400 # bytes per msg


#######################             CLASSES              #######################
def main():
    '''
    Example usage of drv_rs with a load rs device.
    '''
    source_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,
                                          separator = '\n',
                                          baudrate = 115200,
                                          bytesize = EIGHTBITS,
                                          parity = PARITY_ODD,
                                          stopbits = STOPBITS_ONE,
                                          timeout = 0.5,
                                          write_timeout = None,
                                          inter_byte_timeout  = None)


    load_rs = DrvRsDeviceC(config = source_conf_scpi, rx_chan_name = __RX_CHAN_NAME)
    log.info(f"Properties: {load_rs.properties.model}")
    load_rs.set_cv_mode(volt_ref = 20000)
    data = load_rs.get_data()
    log.warning(f"Mode: {data.mode} - Voltage: {data.voltage} - Current: {data.current}")
    time.sleep(3)
    load_rs.set_cc_mode(curr_ref = 1000)
    data = load_rs.get_data()
    log.warning(f"Mode: {data.mode} - Voltage: {data.voltage} - Current: {data.current}")
    load_rs.close()

if __name__ == '__main__':
    main()
