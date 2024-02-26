#!/usr/bin/python3

'''
Example to bk precision.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
import time
from serial import PARITY_ODD
#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC(file_log_levels= 'code/log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

from system_shared_tool import SysShdIpcChanC
#######################          PROJECT IMPORTS         #######################
from scpi_sniffer import DrvScpiSerialConfC, DrvScpiHandlerC

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_bk/')
from src.wattrex_driver_bk import DrvBkModeE
from wattrex_driver_base import DrvBaseStatusE

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def exp_number(str_msg):
    response = None
    if all([var.isnumeric() for var in str_msg.split('e')]):
        msg_sci = str_msg.split('e')
        if len(msg_sci) == 2:
            response = float(msg_sci[0]) * 10 ** int(msg_sci[1])
        else:
            response = float(msg_sci[0])
    return response

# def translate_msg(msg):
#     if isinstance(msg, list):
#         for data in msg:
#             if len(data) >0 and not str(data).startswith(":"):
#                 data = exp_number(data) if exp_number(data) is not None else data
#                 if isinstance(data, str):
#                     if 'volt' in data:
#                         if 'ac' in data:
#                             data = DrvBkModeE.VOLT_AC
#                         else:
#                             data = DrvBkModeE.VOLT_DC
#                     elif 'curr' in data:
#                         if 'ac' in data:
#                             data = DrvBkModeE.CURR_AC
#                         else:
#                             data = DrvBkModeE.CURR_DC
#                     elif len(data.split(',')) == 3:
#                         data = data.split(',')
#                         log.info(f"Serial number: {data[-1]}")
#                         log.info(f"Model: {data[0]}")
#                     log.info(f"Response: {data}")
#                 else:
#                     log.info(f"Value read: {data}")
#     elif isinstance(msg, str):
#         if len(data) >0 and not str(data).startswith(":"):
#             data = exp_number(msg) if exp_number(msg) is not None else msg
#             log.info(f"Response: {data}")

#             # Check if data is a number
def translate_msg(msg):
    for data in msg:
        if len(data) >0 and not str(data).startswith(":"):
            data = exp_number(data) if exp_number(data) is not None else data
            if isinstance(data, str):
                if 'volt' in data:
                    if 'ac' in data:
                        data = DrvBkModeE.VOLT_AC
                    else:
                        data = DrvBkModeE.VOLT_DC
                elif 'curr' in data:
                    if 'ac' in data:
                        data = DrvBkModeE.CURR_AC
                    else:
                        data = DrvBkModeE.CURR_DC
                elif 'NO ERROR' in data:
                    data = data
                elif 'ERROR' in data:
                    data = DrvBaseStatusE.COMM_ERROR
                elif len(data.split(',')) == 3:
                    data = data.split(',')
                    log.info(f"Serial number: {data[-1]}")
                    log.info(f"Model: {data[0]}")
                log.info(f"Response: {data}")
            else:
                log.info(f"Value read: {data}")

def read_msg(chan:SysShdIpcChanC):
    msg = chan.receive_data_unblocking()
    while msg is not None:
        if msg is not None:
            translate_msg(msg.payload)
        msg = chan.receive_data_unblocking()

def main():
    "Main function"

    # Create driver
    bk_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/bk/BK_0001', separator='\n',
                                        baudrate=38200, timeout=1, write_timeout=1)
    ea_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/source/EA_2963640425', separator='\n',
                                    baudrate=9600, timeout=1, write_timeout=1, parity= PARITY_ODD)
    rx_chan = SysShdIpcChanC(name = "bk_rx", max_message_size= 300)
    ea_chan = SysShdIpcChanC(name = "ea_rx", max_message_size= 300)
    try:
        bk_handler = DrvScpiHandlerC(serial_conf=bk_scpi_conf, rx_chan_name= "bk_rx")
        # ea_handler = DrvScpiHandlerC(serial_conf=ea_scpi_conf, rx_chan_name= "ea_rx")
        input("Press Enter to continue...")
        bk_handler.send(':FUNC:CURR:DC:RANGE:AUTO ON')
        time.sleep(2)
        bk_handler.read()
        bk_handler.send(":SYST:ERR?")
        time.sleep(2)
        bk_handler.read()
        time.sleep(2)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(msg= ":VOLT:DC:NPLC 0.1")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(':FUNC?;*IDN?')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(':FUNC?')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(':FUNC CURR:DC;:CURR:DC:RANGE:AUTO ON')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(':FETCh?')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(':FUNC VOLT:DC;:VOLT:DC:RANGE:AUTO ON')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to continue...")
        bk_handler.send(':FETCh?')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        time.sleep(2)
        bk_handler.send(":SYST:ERR?")
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        input("Press Enter to lock source...")
        ea_handler.send(':SYSTem:LOCK: ON')
        ea_handler.read()
        time.sleep(1)
        ea_handler.read()
        time.sleep(2)
        ea_handler.send(":SYST:ERR?")
        ea_handler.read()
        time.sleep(1)
        ea_handler.read()
        read_msg(ea_chan)
        input("Press Enter to set output...")
        ea_handler.send(":CURRent 0.5;:Voltage 7;:OUTPut ON")
        ea_handler.read()
        time.sleep(1)
        ea_handler.read()
        time.sleep(2)
        ea_handler.send(":SYST:ERR?")
        ea_handler.read()
        time.sleep(1)
        ea_handler.read()
        read_msg(ea_chan)
        bk_handler.send(':FETCh?')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        ea_handler.send(":OUTP OFF")
        ea_handler.read()
        time.sleep(1)
        ea_handler.read()
        read_msg(ea_chan)
        bk_handler.send(':FETCh?')
        bk_handler.read()
        time.sleep(1)
        bk_handler.read()
        read_msg(rx_chan)
        sys.exit(0)
    except KeyboardInterrupt:
        rx_chan.terminate()
        ea_chan.terminate()
        log.info('SCPI node stopped')
        sys.exit(0)
    except Exception as e:
        rx_chan.terminate()
        ea_chan.terminate()
        log.error(f"Error creating handler: {e}")
        sys.exit(1)
    finally:
        rx_chan.terminate()
        ea_chan.terminate()
        sys.exit()


if __name__ == '__main__':
    main()
