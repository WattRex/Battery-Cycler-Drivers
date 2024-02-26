#!/usr/bin/python3

'''
Example to bk precision.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
from time import sleep, time
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
    rs_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/loads/RS_79E047AE41D5', separator='\n',
                                    baudrate=115200, timeout=1, write_timeout=1, parity= PARITY_ODD)
    rs_serial: Serial = Serial(port                  = rs_scpi_conf.port,
                                baudrate           = rs_scpi_conf.baudrate,
                                bytesize           = rs_scpi_conf.bytesize,
                                parity             = rs_scpi_conf.parity,
                                stopbits           = rs_scpi_conf.stopbits,
                                timeout            = rs_scpi_conf.timeout,
                                write_timeout      = rs_scpi_conf.write_timeout,
                                inter_byte_timeout = rs_scpi_conf.inter_byte_timeout,
                                xonxoff=True, rtscts=False, dsrdtr=False)
    try:
        #Create driver
        input("Press Enter to get load info...")
        init_time = time()
        rs_serial.write(b'*IDN?\n :SYST:BAUD?\n :FUNC?\n :SYST:LOCK ON\n ')
        log.info(rs_serial.readlines())
        log.info(f"Time to get load info: {time() - init_time}")
        input("Press Enter to get max values...")
        init_time = time()
        rs_serial.write(b":CURR:UPP?\n:CURR:LOW?\n:VOLT:UPP?\n :VOLT:LOW?\n:POW:UPP?\n:POW:LOW?\n")
        msg = rs_serial.readlines()
        log.info(f"Time to get curr info: {time() - init_time}")
        log.info(f"Curr limits: {msg[:2]}")
        log.info(f"Volt limits: {msg[2:4]}")
        log.info(f"Pow limits: {msg[4:]}")
        input("Press Enter to set CV mode with max current to 1A...")
        rs_serial.write(b":CURR MAX 1A\n:VOLT 11.5V\n:INP ON\n")
        input("Press Enter to set CC mode...")
        # time.sleep(2)
        rs_serial.write(b":CURR 0.02A\n")
        rs_serial.write(b":INP ON\n")
        sleep(0.5)
        rs_serial.write(b":MEAS:CURR?\n")
        log.info(rs_serial.readlines())
    except KeyboardInterrupt:
        log.info('Example stopped')
    except Exception as e:
        log.error(f"Error in example: {e}")
    finally:
        rs_serial.write(b":INP OFF\n")
        rs_serial.close()
        sys.exit()

if __name__ == '__main__':
    main()
