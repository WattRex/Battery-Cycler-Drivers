#!/usr/bin/python3

'''
Example to bk precision.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
import time
from threading import Event
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
from scpi_sniffer import DrvScpiSerialConfC, DrvScpiNodeC, DrvScpiHandlerC

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_bk/')
from src.wattrex_driver_bk.drv_bk import DrvBkModeE, DrvBkDeviceC, DrvBkRangeE

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def set_source(current:float, voltage: float, serial: Serial):
    serial.write(f":CURRent {current};:Voltage {voltage};:OUTPut ON\n".encode())
    time.sleep(2)
    serial.write(b":SYST:ERR?\n")
    log.info(serial.readlines())
def disable_source(serial: Serial):
    serial.write(b":OUTP OFF\n")
    log.info(serial.readlines())



def main():
    # working_flag = Event()
    # working_flag.set()
    # scpi = DrvScpiNodeC(working_flag=working_flag, cycle_period=500)
    bk_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/bk/BK_0001', separator='\n',
                                      baudrate=38200, timeout=1, write_timeout=1)
    ea_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/source/EA_2963640425', separator='\n',
                                      baudrate=9600, timeout=1, write_timeout=1, parity= PARITY_ODD)
    ea_serial: Serial = Serial(port                 = ea_scpi_conf.port,
                            baudrate                = ea_scpi_conf.baudrate,
                            bytesize                = ea_scpi_conf.bytesize,
                            parity                  = ea_scpi_conf.parity,
                            stopbits                = ea_scpi_conf.stopbits,
                            timeout                 = ea_scpi_conf.timeout,
                            write_timeout           = ea_scpi_conf.write_timeout,
                            inter_byte_timeout      = ea_scpi_conf.inter_byte_timeout,
                            xonxoff= True, rtscts= False, dsrdtr= False)
    log.info(ea_serial.is_open)
    set_source(0.1, 4.0, ea_serial)
    drv = DrvBkDeviceC(config= bk_scpi_conf)
    try:
        "Main function"
        # input("Press Enter to start...")
        disable_source(ea_serial)
        init = time.time()

        #Set properties
        drv.set_mode(DrvBkModeE.CURR_DC, DrvBkRangeE.AUTO)
        time.sleep(2)
        try:
            while drv.last_data.mode != DrvBkModeE.CURR_DC:
                log.info("Waiting to set mode to CURR_AUTO")
                drv.read_buffer()
                time.sleep(2)
            log.info("Mode set correctly to CURR_AUTO")
            drv.set_mode(meas_mode = DrvBkModeE.VOLT_DC, meas_range= DrvBkRangeE.AUTO)
            while drv.last_data.mode != DrvBkModeE.VOLT_DC:
                log.info("Waiting to set mode to VOLT_AUTO")
                drv.read_buffer()
                time.sleep(2)
        except KeyboardInterrupt:
            drv.close()
            time.sleep(3)
            sys.exit(1)
        # input("Press Enter to set source...")
        log.info("Mode set correctly to VOLT_AUTO")
        set_source(0.1, 4.0, ea_serial)
        for _ in range(10):
            #Obtain data
            init = time.time()
            data = drv.get_data()
            log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
            log.info(f"Time elapsed: {time.time() - init}")
            time.sleep(1)
        if data.voltage < 4000:
            log.error("Voltage not set correctly")

        #Obtain properties
        properties = drv.get_properties()
        log.info("Properties: ")
        log.info(f"Voltage: {properties.max_volt_limit}\tCurrent: {properties.max_current_limit}\t\
                Power: {properties.max_power_limit}\n\
                Model: {properties.model}\tSerial number: {properties.serial_number}")
        log.info(f"Time elapsed: {time.time() - init}")
    except (KeyboardInterrupt, AttributeError, Exception):
        disable_source(ea_serial)
        drv.close()
        time.sleep(2)
        # working_flag.clear()
    finally:
        disable_source(ea_serial)
        drv.close()
        log.info(f'SCPI node stopped')
        sys.exit(0)
    # working_flag.clear()
    log.info('SCPI node stopped')
    time.sleep(2)


if __name__ == '__main__':
    main()
