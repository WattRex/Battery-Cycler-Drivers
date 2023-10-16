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
    source.set_cc_mode(curr_ref = 2, voltage_limit = 20, channel = 1)
    init = time.time()

    while (time.time() - init) < 5:
        log.info(f"Meas: {source.get_meas_chan_one()}")

    source.set_cv_mode(volt_ref = 1000, current_limit = 500, channel = 1)
    init = time.time()
    while (time.time() - init) < 5:
        log.info(f"Meas: {source.get_meas_chan_one()}")
    source.close()


# def old():
#     "Main function"
#     init = time.time()

#     #Create driver
#     scpi = DrvScpiHandlerC(port = '/dev/ttyACM0', separator = '\n', timeout = 0.8,
#                            write_timeout = 0.8, parity = PARITY_ODD, baudrate = 9600)
#     drv = DrvEaDeviceC(handler = scpi)

#     #Set properties
#     if '2384' in drv.get_properties().model :
#         drv.set_cv_mode(volt_ref = 12000, current_limit = 500, channel = 2)
#     drv.set_cv_mode(volt_ref = 1000, current_limit = 500, channel = 1)
#     time.sleep(4)

#     #Obtain data
#     log.info(f"Actual voltage: {drv.get_data().voltage}")
#     if '2384' in drv.get_properties().model :
#         log.info(f"Actual voltage out2: {drv.get_data(2).voltage}")

#     #Disable output
#     drv.disable()
#     if '2384' in drv.get_properties().model :
#         drv.disable(2)
#     #Obtain properties
#     properties = drv.get_properties()
#     log.info(f"Max curr: {properties.max_current_limit}\tMax volt: {properties.max_volt_limit}\t\
#              Max pwr: {properties.max_power_limit}\n\
#              Model: {properties.model}\tSerial number: {properties.serial_number}")

#     #Close driver
#     drv.close()

#     log.info(f"Time elapsed: {time.time() - init - 4}")


if __name__ == '__main__':
    main()
