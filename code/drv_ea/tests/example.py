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

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_ea/')
from src.wattrex_driver_ea.drv_ea import DrvEaDeviceC
from wattrex_driver_base import DrvBasePwrModeE

#######################              ENUMS               #######################


#######################             CLASSES              #######################
def main():
    '''
    Example usage of drv_ea with a source_ea device.
    '''
    ea_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/source/EA_2963640425', separator='\n', baudrate=38400,
                                            timeout=1, write_timeout=1)

    source = DrvEaDeviceC(config = ea_scpi_conf)

    try:
        log.info(f"properties: {source.properties.__dict__}")
        source.set_cc_mode(curr_ref = 1000, voltage_limit = 3000)

        for _ in range(10):
            #Obtain data
            init = time.time()
            data = source.get_data()
            log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
            log.info(f"Time elapsed: {time.time() - init}")
            time.sleep(1.5)
        source.disable()
        init = time.time()
        while source.last_data.mode != DrvBasePwrModeE.DISABLE:
            source.read_buffer()
            time.sleep(1)
        log.info(f"Time elapsed to disable output: {time.time() - init}")
        source.set_cv_mode(volt_ref = 5000, current_limit = 500)
        for _ in range(10):
            #Obtain data
            init = time.time()
            data = source.get_data()
            log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
            log.info(f"Time elapsed: {time.time() - init}")
            time.sleep(1.5)
        source.disable()
        init = time.time()
        while source.last_data.mode != DrvBasePwrModeE.DISABLE:
            source.read_buffer()
            time.sleep(1)
        log.info(f"Time elapsed to disable output: {time.time() - init}")
        source.close()
        log.info('End of example of drv ea')
    except (KeyboardInterrupt, AttributeError, Exception) as err:
        source.close()
        log.info(f"End of example of drv ea with error: {err}")
        sys.exit(0)

if __name__ == '__main__':
    main()
