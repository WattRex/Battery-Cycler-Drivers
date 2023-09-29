#!/usr/bin/python3
'''
Example of use of the driver for SCPI devices.
'''

#######################        MANDATORY IMPORTS         #######################
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from time import sleep
from serial import EIGHTBITS, PARITY_ODD, STOPBITS_ONE, Serial

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)
from system_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
from drv_scpi.src.scpi_sniffer import DrvScpiCmdDataC, DrvScpiCmdTypeE, DrvScpiSerialConfC # pylint: disable=wrong-import-position

#######################              ENUMS               #######################

#######################              CLASSES             #######################
def main() -> None:
    "Principal function to example the driver."
    source_conf_scpi = DrvScpiSerialConfC(port = '/dev/ttyACM0',
                                          separator = '\n',
                                          baudrate = 9600,
                                          bytesize = EIGHTBITS,
                                          parity = PARITY_ODD,
                                          stopbits = STOPBITS_ONE ,
                                          timeout = 0.5, #0.00003,
                                          write_timeout = 0.003,
                                          inter_byte_timeout  = 1)

    msg1 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                            port = '/dev/ttyACM0',
                            payload = source_conf_scpi)

    msg2 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                           port = '/dev/ttyACM0',
                           payload = 'SYSTem:LOCK: ON')

    msg3 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE,
                           port = '/dev/ttyACM0',
                           payload = 'OUTPut: ON')

    # msg4 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
    #                        port = '/dev/ttyACM0',
    #                        payload = 'MEASure:VOLTage?')

    msg5 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                           port = '/dev/ttyACM0')


    scpi_queue = SysShdIpcChanC(name= 'tx_scpi')


    for msg in [msg1, msg2, msg3, msg5]:
        scpi_queue.send_data(msg)
        sleep(0.1)


def quick_test() -> None:
    "Quick test to check the conectivity with the device."
    serial = Serial(port = '/dev/ttyACM0',
                    baudrate = 9600,
                    bytesize = EIGHTBITS,
                    parity = PARITY_ODD,
                    stopbits = STOPBITS_ONE,
                    timeout = 1, #0.00003,
                    write_timeout = 0.003
                    )

    msg_on = 'OUTPut: ON'
    msg_off = 'OUTPut: OFF'

    serial.write(bytes(msg_on.encode("utf-8")))
    print('Write ON')

    sleep(5)
    serial.write(bytes(msg_off.encode("utf-8")))
    print('Write OFF')



if __name__ == '__main__':
    PRUEBA_RAPIDA = False
    if PRUEBA_RAPIDA:
        quick_test()
    else:
        main()
