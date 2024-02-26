#!/usr/bin/python3

'''
Example to bk precision.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
from serial import Serial, PARITY_ODD
#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC(file_log_levels= 'code/log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiSerialConfC

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_bk/')

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def main():
    ea_scpi_conf = DrvScpiSerialConfC(port = '/dev/ttyACM0', separator='\n', baudrate=9600,
                                            timeout=1, write_timeout=1, parity= PARITY_ODD)
    ea_serial: Serial = Serial(port                  = ea_scpi_conf.port,
                                baudrate           = ea_scpi_conf.baudrate,
                                bytesize           = ea_scpi_conf.bytesize,
                                parity             = ea_scpi_conf.parity,
                                stopbits           = ea_scpi_conf.stopbits,
                                timeout            = ea_scpi_conf.timeout,
                                write_timeout      = ea_scpi_conf.write_timeout,
                                inter_byte_timeout = ea_scpi_conf.inter_byte_timeout,
                                xonxoff=True, rtscts=False, dsrdtr=False)
    try:
        #Create driver
        input("Press Enter to lock source...")
        ea_serial.write(b':SYSTem:LOCK: ON\n')
        ea_serial.write(b"OUTPut?\n")
        # time.sleep(2)
        ea_serial.write(b":SYST:ERR?\n")
        log.info(ea_serial.readlines())
        ea_serial.write(b'*IDN?\n')
        # time.sleep(2)
        log.info(ea_serial.readlines())
        input("Press Enter to set output...")
        ea_serial.write(b":CURRent 0.5;:Voltage 7;:OUTPut ON\n")
        # time.sleep(2)
        ea_serial.write(b":SYST:ERR?\n")
        log.info(ea_serial.readlines())
        ea_serial.write(b"MEASure:ARRay?\n")
        # time.sleep(2)
        ea_serial.write(b":SYST:ERR?\n")
        log.info(ea_serial.readlines())
        ea_serial.write(b"SYSTem:NOMinal:CURRent?\n")
        ea_serial.write(b"SYSTem:NOMinal:VOLTage?\n")
        ea_serial.write(b"SYSTem:NOMinal:POWer?\n")
        ea_serial.write(b"OUTPut?\n")
        # time.sleep(2)
        ea_serial.write(b":SYST:ERR?\n")
        log.info(ea_serial.readlines())
        sys.exit(0)
    except KeyboardInterrupt:
        log.info('SCPI node stopped')
    except Exception as e:
        log.error(f"Error creating handler: {e}")
    finally:
        ea_serial.write(b":OUTPut OFF\n")
        ea_serial.write(b":SYSTem:LOCK: OFF\n")
        ea_serial.close()
        sys.exit()

if __name__ == '__main__':
    main()
