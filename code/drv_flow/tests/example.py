 #!/usr/bin/python3
'''
Example of use of drv flow.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
import os
import sys

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
#from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
#if __name__ == '__main__':
#    cycler_logger = SysLogLoggerC()
#log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################
sys.path.append(os.getcwd()+'/code/')
from drv_flow.src.wattrex_driver_flow import DrvFlowWriter

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################

if __name__ == '__main__':
    node = DrvFlowWriter(serial_port='/dev/ttyACM0', data_file='data.csv')
    node.run()
