#!/usr/bin/python3
'''
Example of use of the driver for SCPI devices.
'''

#######################        MANDATORY IMPORTS         #######################
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from serial import EIGHTBITS, PARITY_ODD, STOPBITS_ONE, Serial
from time import sleep, time

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
from drv_scpi.src.scpi_sniffer import *

#######################              ENUMS               #######################

#######################              CLASSES             #######################
def main() -> None:
    source_conf_scpi = DrvScpiSerialConfC(port = '/dev/ttyACM0',
                                          separator = '\n',
                                          baudrate = 9600,
                                          bytesize = EIGHTBITS,
                                          parity = PARITY_ODD,
                                          stopbits = STOPBITS_ONE ,
                                          timeout = 1, #0.00003,
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

    msg4 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                           port = '/dev/ttyACM0',
                           payload = 'MEASure:VOLTage?')

    msg5 = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                           port = '/dev/ttyACM0')


    scpi_queue = SysShdIpcChanC(name= 'cola_SCPI') #TODO: Tengo que poner este nombre de la cola? igual que en el driver?


    for msg in [msg1, msg2, msg3, msg4, msg5]:
        scpi_queue.send_data(msg)
        sleep(0.1)


def prueba_rapida() -> None:
    print('COMIENZA')
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
    msg3 = 'MEASure:VOLTage?'
    msg4 = 'VOLTage 8.00'

    serial.write(bytes(msg_on.encode("utf-8")))
    print('Write ON')

    sleep(5)
    serial.write(bytes(msg_off.encode("utf-8")))
    print('Write OFF')



if __name__ == '__main__':
    PRUEBA_RAPIDA = False
    if PRUEBA_RAPIDA:
        prueba_rapida()
    else:
        main()


# print('COMIENZA 2')
# s = 0.01
# init = time()
# serial.write(bytes(msg3.encode("utf-8")))
# print(f"Escribir: {time() - init}")
# print(f"MSG: {serial.readline()}")
# print(f"MSG: {serial.readline()}")
# print(f"MSG: {serial.readline()}")
# print(f"MSG: {serial.readline()}")
# print(f"MSG: {serial.readline()}")
# print(f"Tiempo: {time() - init}")

# def decode_numbers(self, data: str) -> float:
#     """Decode bytes to integers.



#     # source.send_msg('SYSTem:LOCK: ON')
#     # source.send_msg('SYSTem:LOCK: OFF')
#     # source.send_and_read('MEASure:VOLTage?')
#     log.info(f"{source.read_device_info()}")
