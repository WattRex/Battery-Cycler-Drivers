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
from wattrex_driver_ea import DrvEaDeviceC
from wattrex_driver_bk import DrvBkDeviceC
# from wattrex_driver_rs import DrvRsDeviceC

#######################              ENUMS               #######################
__SERIAL_PORT = '/dev/wattrex/loads/RS_79E047AE41D5'


#######################             CLASSES              #######################
def main():
    '''
    Example usage of drv_rs with a load rs device.
    '''
    ea_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/source/EA_2963640425', separator='\n',
                                      baudrate=38200, timeout=1, write_timeout=1)
    bk_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/bk/BK_0001', separator='\n',
                                      baudrate=38200, timeout=1, write_timeout=1)
    load_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,separator='\n',
                                    baudrate=115200, timeout=1, write_timeout=1, parity= PARITY_ODD)
    try:
        load_rs = DrvRsDeviceC(config = load_conf_scpi)
    except ConnectionError as error:
        load_rs.close()
        # source.close()
        log.error(f"Error: {error}")
        sys.exit(0)
    data = load_rs.get_data()
    time.sleep(1)
    log.info(f"Properties: {load_rs.properties.model}")
    data = load_rs.get_data()
    log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
    try:
        source = DrvEaDeviceC(config = ea_scpi_conf)
    except ConnectionError as error:
        load_rs.close()
        source.close()
        log.error(f"Error: {error}")
        sys.exit(0)
    data = source.get_data()
    time.sleep(1)
    log.warning(f"Source properties: {source.properties.__dict__}")
    data = source.get_data()
    log.warning(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
    try:
        bk = DrvBkDeviceC(config= bk_scpi_conf)
    except ConnectionError as error:
        source.close()
        load_rs.close()
        bk.close()
        log.error(f"Error: {error}")
        sys.exit(0)
    data = bk.get_data()
    time.sleep(1)
    log.error(f"BK properties: {bk.properties.__dict__}")
    data = bk.get_data()
    log.error(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                    Mode: {data.mode}\tStatus: {data.status}")
    try:
        log.info("Disabled")
        input("Press Enter to continue...")
        source.set_cc_mode(curr_ref = 200, voltage_limit = 5000)
        load_rs.set_cc_mode(curr_ref = 200)
        for _ in range(10):
            for device in [load_rs, source, bk]:
                #Obtain data
                init = time.time()
                data = device.get_data()
                log.info(f"Voltage: {data.voltage}\tCurrent: {data.current}\tPower: {data.power}\n\
                        Mode: {data.mode}\tStatus: {data.status}")
                log.info(f"Time elapsed: {time.time() - init}")
                data = device.get_data()
                if time.time() - init< 1:
                    time.sleep(1-(time.time()-init))
        source.disable()
        load_rs.disable()
        load_rs.close()
        source.close()
        bk.close()
        log.info('End of example of scpi devices')
    except (KeyboardInterrupt, AttributeError, Exception) as err:
        load_rs.close()
        source.close()
        bk.close()
        log.info(f"End of example of drv rs with error: {err}")
        sys.exit(0)

if __name__ == '__main__':
    main()
