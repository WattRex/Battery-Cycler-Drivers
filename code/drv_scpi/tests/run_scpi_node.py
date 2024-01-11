#!/usr/bin/python3
'''
This is an example of use of the SCPI module.

'''
# COMMANDS TO RUN BEFORE EXECUTING THIS SCRIPT:
# rm /dev/mqueue/*
# sudo sh -c 'echo 400 > /proc/sys/fs/mqueue/msg_max'
# sudo sh -c 'echo 450 > /proc/sys/fs/mqueue/msgsize_max'


#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from threading import Event

#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
path.append(os.getcwd())
from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          MODULE IMPORTS          #######################
# path.append(os.getcwd()+'/code/')
from drv_scpi.src.scpi_sniffer import DrvScpiNodeC # pylint: disable=wrong-import-position
# from scpi_sniffer import DrvScpiNodeC # pylint: disable=wrong-import-position

#######################            FUNCTIONS             #######################
if __name__ == '__main__':
    # Flag to know if the SCPI is working
    _working_scpi = Event()
    _working_scpi.set()
    #Create the thread for SCPI
    scpi_node = DrvScpiNodeC(working_flag = _working_scpi)
    scpi_node.run()
