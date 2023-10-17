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
    Example usage of drv_scpi with a source_ea device.
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
    log.info(f"properties: {source.properties}")
    source.set_cc_mode(curr_ref = 2, voltage_limit = 20000)
    init = time.time()

    while (time.time() - init) < 5:
        log.info(f"Meas: {source.get_data()}")

    source.set_cv_mode(volt_ref = 10000, current_limit = 500)
    init = time.time()
    while (time.time() - init) < 5:
        log.info(f"Meas: {source.get_data()}")
    source.close()


if __name__ == '__main__':
    main()
