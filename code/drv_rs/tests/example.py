#!/usr/bin/python3
'''
Example to ea power supply.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os

#######################         GENERIC IMPORTS          #######################
import time

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
sys.path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels= 'code/log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiSerialConfC
from serial import PARITY_ODD

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_rs/')
from src.wattrex_driver_rs import DrvRsDeviceC
# from wattrex_driver_rs import DrvRsDeviceC

#######################              ENUMS               #######################
__SERIAL_PORT = '/dev/wattrex/loads/RS_79E047AE41D5'


#######################             CLASSES              #######################
def main():
    '''
    Example usage of drv_rs with a load rs device.
    '''
    load_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,separator='\n',
                                    baudrate=115200, timeout=1, write_timeout=1, parity= PARITY_ODD)


    load_rs = DrvRsDeviceC(config = load_conf_scpi)
    try:
        data = load_rs.get_data()
        input("Press Enter to continue...")
        log.info(f"Properties: {load_rs.properties.model}")
        data = load_rs.get_data()
        log.warning((f"Mode: {data.mode} - Voltage: {data.voltage} - Current: {data.current} "
                     f"- Power: {data.power}"))
        time.sleep(3)
        load_rs.set_cc_mode(curr_ref = 200)
        for _ in range(10):
            #Obtain data
            init = time.time()
            data = load_rs.get_data()
            log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
            log.info(f"Time elapsed: {time.time() - init}")
            if time.time() - init< 1:
                time.sleep(1-(time.time()-init))
        load_rs.disable()
        log.info("Disabled")
        input("Press Enter to continue...")
        load_rs.set_cv_mode(volt_ref = 3900)
        for _ in range(10):
            #Obtain data
            init = time.time()
            data = load_rs.get_data()
            log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
            log.info(f"Time elapsed: {time.time() - init}")
            if time.time() - init< 1:
                time.sleep(1-(time.time()-init))
        load_rs.close()
        log.info('End of example of drv rs')
    except (KeyboardInterrupt, AttributeError, Exception) as err:
        load_rs.close()
        log.info(f"End of example of drv rs with error: {err}")
        sys.exit(0)

if __name__ == '__main__':
    main()
