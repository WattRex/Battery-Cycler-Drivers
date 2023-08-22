#!/usr/bin/python3

# -*- coding: utf-8 -*-

"""
Example of use of the driver for SCPI devices.
"""

#######################        MANDATORY IMPORTS         #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
import sys
sys.path.append("..")

from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
if __name__ == "__main__":
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################
#######################          MODULE IMPORTS          #######################
from src.wattrex_driver_pwr.drv_pwr import DrvPwrStatusC, DrvPwrStatusE

#######################          PROJECT IMPORTS         #######################


#######################              ENUMS               #######################

#######################              CLASSES             #######################

def test():
    '''
    Test function.
    '''
    pwr = DrvPwrStatusC(DrvPwrStatusE.OK)
    # print(pwr)

    pwr2 = DrvPwrStatusC(DrvPwrStatusE.OK)

    print(pwr == pwr2)

if __name__ == '__main__':
    test()
