#!/usr/bin/python3
"""
This module will manage CAN messages and channels
in order to configure channels and send/received messages.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import os
import sys
import threading
import time
from subprocess import run, PIPE

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path

from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC(file_log_levels= '../log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################
from can_sniffer import DrvCanNodeC
from src.wattrex_driver_epc import DrvEpcDeviceC, DrvEpcLimitE, DrvEpcModeE
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

#######################            FUNCTIONS             #######################

if __name__ == '__main__':

    # Flag to know if the can is working
    _working_can = threading.Event()
    _working_can.set()
    #Create the thread for CAN
    try:
        can = DrvCanNodeC(tx_buffer_size = 150, working_flag = _working_can)
        can.start()

        n_dev = input("Introduce the can_id of "+
                        "the device: ")
        can_id = int(n_dev,16) if 'x' in n_dev else int(n_dev)
        epc= DrvEpcDeviceC(can_id)
        last_mode = DrvEpcModeE.IDLE
        log.info(f"epc dev : {epc.__dict__}")
        epc.open()
        log.info(f"Device can id: {hex(epc.get_properties().can_id)}")
        epc.get_properties(update=True)
        epc.set_periodic(False, 1000, True, 100, True, 100)
        i=0
        j = 0
        while 1:

            elec_meas = epc.get_elec_meas(periodic_flag=False)
            temp_meas = epc.get_temp_meas(periodic_flag=False)
            data = epc.get_data(update=True)

            if data.mode is DrvEpcModeE.IDLE and last_mode is not DrvEpcModeE.IDLE:
                if j == 0:
                    epc.set_cc_mode(1000, DrvEpcLimitE.TIME, 3000)
                    j = 1
                else:
                    epc.set_wait_mode(limit_ref=3000)
                    j = 0

            if last_mode != data.mode:
                last_mode = data.mode

            time.sleep(0.01)
            i+=1
        print("fin")
    except Exception as err:
        print(err)
        # If there has been any problem, the posix queues might not close properly and have to be
        # deleted manually with the following command in linux
        run(args="rm -r /dev/mqueue/*", shell =True, stdout=PIPE, stderr=PIPE, check=False)
