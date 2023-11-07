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
from datetime import datetime
from pytz import timezone

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
class _ConstantsC():
    TO_MILIS = 1000
    TO_DECIS = 100
    HEADER = ['Time','Mode', 'Ref[m/dU]', 'Limit', 'Limit_ref[m/dU]',
            'LS_Volt[mV]','LS_Curr[mA]','LS_Power[dW]',
            'HS_Volt[mV]', 'Temp_body[dºC]', 'Temp_anod[dºC]', 'Temp_amb[dºC]']

class _ManageEpcC():
    def __init__(self, can_id: int, txt: str) -> None:
        self.epc= DrvEpcDeviceC(can_id)

        self.df_epc = open(os.path.join(path, #pylint: disable= consider-using-with
                    f'epc{hex(epc_dev.epc.get_properties().can_id)}_data.csv'), 'a', 
                    encoding="utf-8")
        if len(txt)!=0:
            self.file = open( # pylint: disable= consider-using-with
                os.path.join(path,txt+'.txt'), 'r', encoding="utf-8")
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

    # Flag to know if the can is working
    _working_can = threading.Event()
    _working_can.set()
    #Create the thread for CAN
    try:
        can = DrvCanNodeC(tx_buffer_size = 150, working_flag = _working_can)
        can.start()

        path = os.path.join(os.getcwd(),'example')
        if not os.path.exists(path):
            os.mkdir(path)
        n_dev = input("Introduce the can_id of "+
                        "the devices separated by commas: ").replace(' ','').split(',')
        if len(n_dev)>0:
            n_dev = [int(x,16) for x in n_dev if 'x' in x]+[int(x) for x in n_dev if 'x' not in x]
        n_txt = input("Introduce the name of files, must follow same order as device "+
                        " and not end in .txt: ").replace(' ','').split(',')
        if len(n_dev)!= len(n_txt) or n_txt[0] == '':
            log.error('Number of devices and files does not match')

        if n_txt[0] != '' and len(n_dev) == len(n_txt):
            list_dev = [_ManageEpcC(int(dev),txt) for dev,txt in zip(n_dev,n_txt)]
            for epc_dev in list_dev:
                log.info(f"Device can id: {hex(epc_dev.epc.get_properties().can_id)}")
                epc_dev.epc.open()
            while len(list_dev)>0:
                time.sleep(0.100)
                for epc_dev in list_dev:
                    elec_meas = epc_dev.epc.get_elec_meas(periodic_flag=False)
                    temp_meas = epc_dev.epc.get_temp_meas(periodic_flag=False)

                    data = epc_dev.epc.get_data(update=True)
                    timestamp = datetime.now().astimezone(timezone(
                        'Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    epc_dev.df_epc.write((f"{timestamp},"
                        f",{data.mode.name},{data.ref},{data.lim_mode.name},{data.lim_ref},"\
                        f"{elec_meas.ls_current},{elec_meas.ls_current},{elec_meas.ls_power},"
                        f"{elec_meas.hs_voltage},{temp_meas.temp_body},{temp_meas.temp_anod},"
                        f"{temp_meas.temp_amb}"))
                    if data.mode is DrvEpcModeE.IDLE and epc_dev.last_mode is not DrvEpcModeE.IDLE:
                        cmd = epc_dev.file.readline()
                        if not cmd :
                            epc_dev.df_epc.to_csv(os.path.join(path,
                                    f'epc{hex(epc_dev.epc.get_properties().can_id)}_data.csv'),
                                    index=False)
                            epc_dev.file.close()
                            epc_dev.df_epc.close()
                            list_dev.remove(epc_dev)
                        else:
                            apply_txt_cmd(cmd, epc_dev.epc)
                    if epc_dev.last_mode != data.mode:
                        epc_dev.last_mode = data.mode
        else:
            epc_dev = _ManageEpcC(int(n_dev[0]),'')
            epc_dev.epc.open()
            epc_dev.epc.get_properties(update=True)
            epc_dev.epc.set_periodic(False, 1000, True, 100, True, 100)
            i=0
            j = 0
            while 1:

                elec_meas = epc_dev.epc.get_elec_meas(periodic_flag=False)
                temp_meas = epc_dev.epc.get_temp_meas(periodic_flag=False)
                data = epc_dev.epc.get_data(update=True)
                #save measures in pandas
                timestamp = datetime.now().astimezone(timezone(
                        'Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                epc_dev.df_epc.write((f"{timestamp},"
                        f",{data.mode.name},{data.ref},{data.lim_mode.name},{data.lim_ref},"\
                        f"{elec_meas.ls_current},{elec_meas.ls_current},{elec_meas.ls_power},"
                        f"{elec_meas.hs_voltage},{temp_meas.temp_body},{temp_meas.temp_anod},"
                        f"{temp_meas.temp_amb}"))

                if data.mode is DrvEpcModeE.IDLE and epc_dev.last_mode is not DrvEpcModeE.IDLE:
                    if j == 0:
                        epc_dev.epc.set_cc_mode(1000, DrvEpcLimitE.TIME, 3000)
                        j = 1
                    else:
                        epc_dev.epc.set_wait_mode(limit_ref=3000)
                        j = 0

                if epc_dev.last_mode != data.mode:
                    epc_dev.last_mode = data.mode

                if i %120 == 0:
                    epc_dev.df_epc.close()

                time.sleep(0.01)
                i+=1
        print("fin")
    except Exception:
        # If there has been any problem, the posix queues might not close properly and have to be
        # deleted manually with the following command in linux
        run(args="rm -r /dev/mqueue/*", shell =True, stdout=PIPE, stderr=PIPE, check=False)
