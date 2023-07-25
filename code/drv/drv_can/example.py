#!/usr/bin/python3
"""
This is an example of use of the can module.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import os
import sys

#######################         GENERIC IMPORTS          #######################
import threading
import time
#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path
from sys_abs.sys_shd import SysShdChanC
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################
from drv.drv_can import DrvCanCmdDataC, DrvCanCmdTypeE, DrvCanFilterC, DrvCanNodeC, DrvCanMessageC

#######################            FUNCTIONS             #######################
def translate(msg_epc: DrvCanMessageC):
    """Translate a DRV CAN message to a string, limited use for the epc tower power.

    Args:
        msg_epc (DrvCanMessageC): [description]
    """
    info_id = msg_epc.addr & 0x00F
    binary_string = [f"{bin(int(x))[2:]}" for x in msg_epc.data]
    if info_id == 0xA:
        log.info(f"Device ID: {int(binary_string[0][2:])}")
        log.info(f"Device fw version: {msg_epc.data[6:11]}")
        log.info(f"Device hw version: {msg_epc.data[11:]}")
    elif info_id == 0xB:
        if int(binary_string[0][7]) == 1:
            log.info("HS voltage error")
        if int(binary_string[0][6]) == 1:
            log.info("LS voltage error")
        if int(binary_string[0][5]) == 1:
            log.info("LS current error")
        if int(binary_string[0][4]) == 1:
            log.info("Communication error")
        if int(binary_string[0][3]) == 1:
            log.info("Temperature error")
        if int(binary_string[0][2]) == 1:
            log.info("Internal error")
        log.info(f"Last rised error: {hex(int(binary_string[2]+binary_string[1]))}")
    elif info_id == 0xC:
        log.info(f"LS Voltage: {int(binary_string[1]+binary_string[0],2)}")
        log.info(f"HS Voltage: {int(binary_string[5]+binary_string[4],2)}")



if __name__ == '__main__':
    #Create a CAN queue where the comands to apply will be send
    can_queue = SysShdChanC(100000000)
    can_queue.delete_until_last()
    # Flag to know if the can is working
    _working_can = threading.Event()
    _working_can.set()
    #Create the thread for CAN
    can = DrvCanNodeC(can_queue, _working_can)
    can.start()
    #Example of messages
    msg1 = DrvCanMessageC(addr = 0x030, size = 8, data= 0x00000b803e80020) # Change to wait mode
    msg2 = DrvCanMessageC(addr = 0x037, size = 6, data= 0xc900c90000) # Change periodic every 1s
    msg3 = DrvCanMessageC(addr = 0x030, size = 8, data= 0x13E003E80015) # CC 1A limV 5.1V
    filter_cmd = DrvCanFilterC(addr=0x030, mask= 0x7F0, chan=SysShdChanC(5000))
    #In order to apply the messages should be wrap in the DrvCanCmdDataC to know which type is it
    cmd = DrvCanCmdDataC(data_type= DrvCanCmdTypeE.ADD_FILTER, payload= filter_cmd)
    can_queue.send_data(cmd)
    can_queue.send_data(DrvCanCmdDataC(DrvCanCmdTypeE.MESSAGE, msg1))
    log.debug('Msg1 a cola enviado')
    can_queue.send_data(DrvCanCmdDataC(DrvCanCmdTypeE.MESSAGE, msg2))
    log.debug('Msg2 a cola enviado')
    i = 0
    while 1:
        time.sleep(0.2)
        if not filter_cmd.chan.is_empty():
            msg_rcv = filter_cmd.chan.get()
            translate(msg_rcv)
            # log.debug(f"Message read from epc: id {hex(msg_rcv.addr)}"+
            #             f"/n {msg_rcv.data}")
        i = i+1
        #Every 20s will change from wait to CC 1A limV 5.1V and viceversa
        if i==100:
            can_queue.send_data(DrvCanCmdDataC(DrvCanCmdTypeE.MESSAGE, msg3))
            # log.debug('Msg3 a cola enviado')
        elif i == 200:
            i=0
            #Chante to wait mode
            can_queue.send_data(DrvCanCmdDataC(DrvCanCmdTypeE.MESSAGE, msg1))
            # log.debug('Msg1 a cola enviado')
