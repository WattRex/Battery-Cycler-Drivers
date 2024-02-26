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
from wattrex_driver_bk import DrvBkDeviceC, DrvBkModeE
#######################              ENUMS               #######################


#######################             CLASSES              #######################
def main():
    '''
    Example usage of drv_ea with a source_ea device.
    '''
    ea_scpi_conf = DrvScpiSerialConfC(port = '/dev/ttyACM0', separator='\n',
                                      baudrate=38200, timeout=1, write_timeout=1)
    bk_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/bk/BK_0001', separator='\n',
                                      baudrate=38200, timeout=1, write_timeout=1)

    source = DrvEaDeviceC(config = ea_scpi_conf)
    bk = DrvBkDeviceC(config= bk_scpi_conf)
    try:
        log.info(f"Source properties: {source.properties.__dict__}")
        log.info(f"BK properties: {bk.properties.__dict__}")
        bk.set_mode(meas_mode= DrvBkModeE.VOLT_DC)
        source.set_cc_mode(curr_ref = 10, voltage_limit = 3000)
        bk.read_buffer()
        for _ in range(10):
            #Obtain data
            init = time.time()
            data = source.get_data()
            log.info((f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n"
                    f"Mode: {data.mode}\tStatus: {data.status}"))
            data = bk.get_data()
            log.warning((f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n"
                    f"Mode: {data.mode}\tStatus: {data.status}"))
            log.critical(f"Time elapsed: {time.time() - init}")
            time.sleep(2)
        source.disable()
        init = time.time()
        while source.last_data.mode != DrvBasePwrModeE.WAIT:
            source.read_buffer()
            bk.read_buffer()
            time.sleep(1)
        log.info(f"Time elapsed to disable output: {time.time() - init}")
        source.set_cv_mode(volt_ref = 5000, current_limit = 250)
        for _ in range(10):
            #Obtain data
            init = time.time()
            data = source.get_data()
            log.info((f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n"
                    f"Mode: {data.mode}\tStatus: {data.status}"))
            data = bk.get_data()
            log.warning((f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n"
                    f"Mode: {data.mode}\tStatus: {data.status}"))
            log.critical(f"Time elapsed: {time.time() - init}")
            time.sleep(2)
        source.disable()
        init = time.time()
        while source.last_data.mode != DrvBasePwrModeE.WAIT:
            source.read_buffer()
            bk.read_buffer()
            time.sleep(1)
        log.info(f"Time elapsed to disable output: {time.time() - init}")
        source.close()
        bk.close()
        log.info('End of example of drv ea and bk')
    except (KeyboardInterrupt, AttributeError, Exception) as err:
        source.close()
        bk.close()
        log.error(f'End of example of drv ea and bk with error: {err}')
        sys.exit(0)

if __name__ == '__main__':
    main()
