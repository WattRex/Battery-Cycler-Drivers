#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
Driver for SCPI devices.
"""

#######################        MANDATORY IMPORTS         #######################
import sys, os
sys.path.append(os.getcwd())  #get absolute path

#######################      LOGGING CONFIGURATION       #######################
# from sys_abs.sys_log import SysLogLoggerC, sys_log_logger_get_module_logger

# if __name__ == '__main__':
#     cycler_logger = SysLogLoggerC('./sys_abs/sys_log/loggingConfig.conf')
# log = sys_log_logger_get_module_logger(__name__, config_by_module_filename="./log_config.yaml")

#######################         GENERIC IMPORTS          #######################
from enum import Enum

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################
from drv_pwr import *

#######################          PROJECT IMPORTS         #######################


#######################              ENUMS               #######################

#######################             CLASSES              #######################


def main():
    pwr = DrvPwrStatusC(0, DrvPwrStatusE.OK)
    # print(pwr)

    pwr2 = DrvPwrStatusC(0, DrvPwrStatusE.OK)

    print(pwr == pwr2)

if __name__ == '__main__':
    main()