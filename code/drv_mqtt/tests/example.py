#!/usr/bin/python3
'''
Create a base class used to register devices status.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
#######################         GENERIC IMPORTS          #######################
from time import sleep
#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

from ..src.wattrex_driver_mqtt.drv_mqtt import DrvMqttDriverC #pylint: disable= relative-beyond-top-level

#### Example for bfr ####
def error(data):
    """Log an error message

    Args:
        data ([type]): [description]
    """
    log.critical(f"Error callback: {data}")

def mode(data):
    """Enable mode .

    Args:
        data ([type]): [description]
    """
    log.error(f"Mode callback: {data}")

def refs(data):
    """Refs the refs callback .

    Args:
        data ([type]): [description]
    """
    log.critical(f"Refs callback: {data}")

def main():
    """This function is called when the driver is started.
    It is called when the event loop is started .
    """
    driver = DrvMqttDriverC(error)
    try:
        pwr_ref = 'ctrl/pwr_ref'
        mode_topic = 'ctrl/mode'
        driver.subscribe(mode_topic, mode)
        driver.subscribe(pwr_ref, refs)
        driver.publish(mode_topic, 'NORMAL')

        iteration = -1
        while iteration < 100:
            print(' [*] Waiting for messages. To exit press CTRL+C')
            driver.publish(pwr_ref, str(iteration))
            driver.process_data()
            sleep(1)
            iteration+=1
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        driver.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0) # pylint: disable=protected-access

if __name__ == '__main__':
    main()
