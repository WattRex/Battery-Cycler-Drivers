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

#######################         GENERIC IMPORTS          #######################
from datetime import datetime
from pytz import timezone

#######################       THIRD PARTY IMPORTS        #######################
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
class _ConstantsC():
    TO_MILIS = 1000
    TO_DECIS = 100

class _ManageEpcC():
    def __init__(self, can_id: int, txt: str, tx_queue: SysShdChanC) -> None:
        self.epc= DrvEpcDeviceC(can_id, SysShdChanC(500), tx_queue)
        self.df_epc = pd.DataFrame(columns=['Time','Mode', 'Ref[m/dU]', 'Limit', 'Limit_ref[m/dU]',
                            'LS_Volt[mV]','LS_Curr[mA]','LS_Power[dW]',
                             'HS_Volt[mV]', 'Temp_body[dºC]', 'Temp_anod[dºC]', 'Temp_amb[dºC]'])
        if len(txt)!=0:
            self.file = open(os.path.join(path,txt+'.txt'), 'r', encoding="utf-8")
        else:
            self.file = None
        self.last_mode : DrvEpcModeE = DrvEpcModeE.WAIT
#######################            FUNCTIONS             #######################
def apply_txt_cmd(command: str, epc_device: DrvEpcDeviceC):
    """Applies the text command to the device .

    Args:
        command (str): [description]
        epc (DrvEpcDeviceC): [description]
    """
    limits = {'TIME': 0, 'VOLTAGE': 1, 'CURRENT': 2, 'POWER': 3}
    command_list = command.replace(' ','').split(',')
    if 'WAIT' in command:
        epc_device.set_wait_mode(DrvEpcLimitE.TIME,
                                int(float(command_list[-1])*_ConstantsC.TO_MILIS))
    else:
        ref = float(command_list[1])
        limit = DrvEpcLimitE(limits.get(command_list[2]))
        limit_ref = float(command_list[3])
        if limit == DrvEpcLimitE.POWER:
            limit_ref = int(limit_ref*_ConstantsC.TO_DECIS)
        else:
            limit_ref = int(limit_ref*_ConstantsC.TO_MILIS)
        if 'CC' in command:
            epc_device.set_cc_mode(int(ref*_ConstantsC.TO_MILIS), limit, limit_ref)
        elif 'CV' in command:
            epc_device.set_cv_mode(int(ref*_ConstantsC.TO_MILIS), limit, limit_ref)
        elif 'CP' in command:
            epc_device.set_cp_mode(int(ref*_ConstantsC.TO_DECIS), limit, limit_ref)



if __name__ == '__main__':
    can_queue = SysShdChanC(100000000)
    can_queue.delete_until_last()
    # Flag to know if the can is working
    _working_can = threading.Event()
    _working_can.set()
    #Create the thread for CAN
    can = DrvCanNodeC(can_queue, _working_can)

    path = os.path.join(os.getcwd(),'drv','drv_epc','example')
    n_dev = input("Introduce the can_id of "+
                    "the devices separated by commas: ").replace(' ','').split(',')
    log.info('Not devices introduced')
    if len(n_dev)>0:
        n_dev = [int(x,16) for x in n_dev if 'x' in x]+[int(x) for x in n_dev if 'x' not in x]
    n_txt = input("Introduce the name of files, must follow same order as device "+
                    " and not end in .txt: ").replace(' ','').split(',')
    if len(n_dev)!= len(n_txt):
        log.error('Number of devices and files does not match')

    can.start()
    if len(n_txt) != 0 and len(n_dev)!= len(n_txt):
        list_dev = [_ManageEpcC(dev,txt,can_queue) for dev,txt in zip(n_dev,n_txt)]
        for epc_dev in list_dev:
            log.info(f"Device can id: {hex(epc_dev.epc.get_properties().can_id)}")
            epc_dev.epc.open()
        while len(list_dev)>0:
            time.sleep(0.100)
            for epc_dev in list_dev:
                elec_meas = list(epc_dev.epc.get_elec_meas(periodic_flag=False).values())
                temp_meas = list(epc_dev.epc.get_temp_meas(periodic_flag=False).values())

                data = epc_dev.epc.get_data(update=True)
                epc_dev.df_epc.loc[len(epc_dev.df_epc)] = [datetime.now().astimezone(
                    timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]]+\
                    [data.mode.name, data.ref, data.lim_mode.name, data.lim_ref]+elec_meas+temp_meas
                if data.mode is DrvEpcModeE.IDLE and epc_dev.last_mode is not DrvEpcModeE.IDLE:
                    cmd = epc_dev.file.readline()
                    if not cmd :
                        epc_dev.df_epc.to_csv(os.path.join(path,
                                f'epc{hex(epc_dev.epc.get_properties().can_id)}_data.csv'),
                                index=False)
                        epc_dev.file.close()
                        list_dev.remove(epc_dev)
                    else:
                        apply_txt_cmd(cmd, epc_dev.epc)
                if epc_dev.last_mode != data.mode:
                    epc_dev.last_mode = data.mode
    else:
        epc_dev = _ManageEpcC(n_dev[0],'',can_queue)
        epc_dev.epc.open()
        i=0
        j = 0
        while 1:

            elec_meas = list(epc_dev.epc.get_elec_meas(periodic_flag=False).values())
            temp_meas = list(epc_dev.epc.get_temp_meas(periodic_flag=False).values())
            data = epc_dev.epc.get_data(update=True)
            #save measures in pandas
            epc_dev.df_epc.loc[len(epc_dev.df_epc)] = [datetime.now().astimezone(
                    timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]]+\
                 [data.mode.name, data.ref, data.lim_mode.name, data.lim_ref]+elec_meas+temp_meas
            
            if data.mode is DrvEpcModeE.IDLE and epc_dev.last_mode is not DrvEpcModeE.IDLE:
                if j == 0:
                    epc_dev.epc.set_cc_mode(1000, DrvEpcLimitE.TIME, 3000)
                    j = 1
                else:
                    epc_dev.epc.set_wait_mode(limit_type= DrvEpcLimitE.TIME, limit_ref=3000)
                    j = 0


            if i %120 == 0:
                epc_dev.df_epc.to_csv(os.path.join(path,
                        f'epc{hex(epc_dev.epc.get_properties().can_id)}_data.csv'), index=False)

            time.sleep(0.1)
            i+=1
    print("fin")
