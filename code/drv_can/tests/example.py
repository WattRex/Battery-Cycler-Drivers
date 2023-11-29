#!/usr/bin/python3
"""
This is an example of use of the can module.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
#######################         GENERIC IMPORTS          #######################
from threading import Event
import time
#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger, SysLogLoggerC, Logger

#######################       LOGGER CONFIGURATION       #######################
cycler_logger = SysLogLoggerC(file_log_levels='code/log_config.yaml')
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_can/')
from system_shared_tool import SysShdIpcChanC
from src.can_sniffer import DrvCanCmdDataC, DrvCanCmdTypeE, DrvCanFilterC, DrvCanNodeC,\
                            DrvCanMessageC

#######################            FUNCTIONS             #######################
def translate(msg_epc: DrvCanMessageC):
    """Translate a DRV CAN message to a string, limited use for the epc tower power.

    Args:
        msg_epc (DrvCanMessageC): [description]
    """
    info_id = msg_epc.addr & 0x00F
    binary_string = [f"{bin(int(x))[2:]}" for x in msg_epc.payload]
    if info_id == 0xA:
        log.info(f"Device ID: {int(binary_string[0][2:])}")
        log.info(f"Device fw version: {msg_epc.payload[6:11]}")
        log.info(f"Device hw version: {msg_epc.payload[11:]}")
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
        log.info(f"LS Current: {int(binary_string[3]+binary_string[2],2)}")
        log.info(f"HS Voltage: {int(binary_string[5]+binary_string[4],2)}")
    elif info_id == 0xD:
        log.info(f"Body T: {int(binary_string[1]+binary_string[0],2)}")
        log.info(f"Anode T: {int(binary_string[3]+binary_string[2],2)}")
        log.info(f"Amb T: {int(binary_string[5]+binary_string[4],2)}")

if __name__ == '__main__':
    # Flag to know if the can is working
    _working_can = Event()
    _working_can.set()
    #Create the thread for CAN
    can = DrvCanNodeC(working_flag=_working_can)
    try:
        can.start()
        #Example of messages
        msg1 = DrvCanMessageC(addr = 0x030,
                              size = 8, payload= 0x00000b803e80020) # Change to wait mode
        msg2 = DrvCanMessageC(addr = 0x037,
                              size = 6, payload= 0x1900190000) # Change periodic every 10ms
        msg3 = DrvCanMessageC(addr = 0x030,
                              size = 8, payload= 0x13E003E80015) # CC 1A limV 5.1V
        filter_cmd = DrvCanFilterC(addr=0x030, mask= 0x7F0, chan_name= 'RX_CAN_0X3')
        # In order to apply the messages should be wrap
        # in the DrvCanCmdDataC to know which type is it
        cmd = DrvCanCmdDataC(data_type= DrvCanCmdTypeE.ADD_FILTER, payload= filter_cmd)
        can_queue = SysShdIpcChanC(name= 'TX_CAN')
        time.sleep(1)
        can_queue.send_data(cmd)
        for i in range(0,6):
            filter_cmd = DrvCanFilterC(addr=(i<<4), mask= 0x7F0, chan_name= f'RX_CAN_0X{i}')
            #In order to apply the messages should be wrap in the DrvCanCmdDataC,
            # to know which type is it
            cmd = DrvCanCmdDataC(data_type= DrvCanCmdTypeE.ADD_FILTER, payload= filter_cmd)
            can_queue.send_data(cmd)
        filter_cmd = DrvCanFilterC(addr=0x030, mask= 0x7F0, chan_name= 'RX_CAN_0X3')
        cmd = DrvCanCmdDataC(data_type= DrvCanCmdTypeE.ADD_FILTER, payload= filter_cmd)
        can_queue.send_data(cmd)
        filter_cmd = DrvCanFilterC(addr=0x020, mask= 0x7F0, chan_name= 'RX_CAN_0X2')
        cmd = DrvCanCmdDataC(data_type= DrvCanCmdTypeE.REMOVE_FILTER, payload= filter_cmd)
        can_queue.send_data(cmd)
        filter_cmd = DrvCanFilterC(addr=0x020, mask= 0x7F0, chan_name= 'RX_CAN_0X2')
        cmd = DrvCanCmdDataC(data_type= DrvCanCmdTypeE.REMOVE_FILTER, payload= filter_cmd)
        can_queue.send_data(cmd)
        time.sleep(2)
        rx_queue= SysShdIpcChanC(name='RX_CAN_0X3')
        can_queue.send_data(DrvCanCmdDataC(DrvCanCmdTypeE.MESSAGE, msg1))
        log.debug('Msg1 a cola enviado')
        can_queue.send_data(DrvCanCmdDataC(DrvCanCmdTypeE.MESSAGE, msg2))
        log.debug('Msg2 a cola enviado')
        i = 0
        while 1:
            time.sleep(0.2)
            if not rx_queue.is_empty():
                msg_rcv = rx_queue.receive_data()
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
    except KeyboardInterrupt:
        _working_can.clear()
        can_queue.terminate()
        rx_queue.terminate()
        can.join()
        log.info('closing everything')
        sys.exit(0)
