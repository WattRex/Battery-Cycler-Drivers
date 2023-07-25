#!/usr/bin/python3
"""
This module will manage CAN messages and channels
in order to configure channels and send/received messages.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import os
import sys

#######################         GENERIC IMPORTS          #######################
import time

#######################       THIRD PARTY IMPORTS        #######################
import threading
import pandas as pd

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path

from sys_abs.sys_shd import SysShdChanC
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################
from drv.drv_can import DrvCanNodeC
from drv.drv_epc import DrvEpcDeviceC, DrvEpcLimitE, DrvEpcModeE
#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

if __name__ == '__main__':
    can_queue = SysShdChanC(100000000)
    can_queue.delete_until_last()
    # Flag to know if the can is working
    _working_can = threading.Event()
    _working_can.set()
    #Create the thread for CAN
    can = DrvCanNodeC(can_queue, _working_can)
    can.start()
    path = os.path.join(os.getcwd(),'drv','drv_epc','example')
    # files = [f for f in os.listdir(path) if f.endswith('.txt')]
    # for file in files:
    #     os.open(file)
    # Create the epc device object
    epc1 = DrvEpcDeviceC(dev_id=0x3, device_handler=SysShdChanC(500), tx_can_queue=can_queue)
    # Enable the reception of can messages
    epc1.open(addr= 0x030, mask= 0x7F0)
    epc1_data = pd.DataFrame(columns=['Time', 'LS_Volt','LS_Curr','LS_Power',
                             'HS_Volt', 'Temp_body', 'Temp_anod', 'Temp_amb'])
    # epc1.set_periodic(elect_en = True, elect_period = 50)
    i=0
    j = 0
    while 1:

        elec_meas = list(epc1.get_elec_meas(periodic_flag=False).values())
        temp_meas = list(epc1.get_temp_meas(periodic_flag=False).values())
        if epc1.get_data().mode is DrvEpcModeE.IDLE:
            if j == 0:
                epc1.set_cc_mode(1000, DrvEpcLimitE.TIME, 3000)
                j = 1
            else:
                epc1.set_wait_mode(limit_type= DrvEpcLimitE.TIME, limit_ref=3000)
                j = 0

        #save measures in pandas
        epc1_data.loc[len(epc1_data)] = [i]+elec_meas+temp_meas

        if i %120 == 0:
            epc1_data.to_csv(os.path.join(path,'epc1_data.csv'),index=False)

        time.sleep(0.1)
        i+=1
