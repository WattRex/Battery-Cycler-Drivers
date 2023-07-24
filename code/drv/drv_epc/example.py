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
from typing import Any, Iterable, Callable, Mapping
from enum import Enum

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path

from sys_abs.sys_shd import SysShdChanC
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          MODULE IMPORTS          #######################


#######################          PROJECT IMPORTS         #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

if __name__ == '__main__':
    print("Hola")
