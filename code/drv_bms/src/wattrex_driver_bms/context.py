#!/usr/bin/python3
'''
This module manages the constants variables.
Those variables are used in the scripts inside the module and can be modified
in a config yaml file specified in the environment variable with name declared
in system_config_tool.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from typing import List
#######################         GENERIC IMPORTS          #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          PROJECT IMPORTS         #######################
from system_config_tool import sys_conf_update_config_params

#######################          MODULE IMPORTS          #######################

######################             CONSTANTS              ######################
# For further information check out README.md
DEFAULT_MAX_MSG : int = 100 # Max number of allowed message per chan
DEFAULT_MAX_MESSAGE_SIZE : int = 120 # Size of message sent through IPC message queue
DEFAULT_TX_CHAN : str = 'TX_CAN' # Name of the TX channel in CAN
DEFAULT_RX_CHAN: str = 'RX_CAN_BMS'  #Name of the RX channel
DEFAULT_MEASURE_NAMES: List = ['vcell1', 'vcell2', 'vcell3', 'vcell4', 'vcell5', 'vcell6', 'vcell7',
                     'vcell8', 'vcell9', 'vcell10', 'vcell11', 'vcell12', 'vstack',
                     'temp1', 'temp2', 'temp3', 'temp4', 'pres1', 'pres2'] #Allowed measure names
DEFAULT_TIMEOUT_RESPONSE: int = 30 # Expected time to get answer


CONSTANTS_NAMES = ('DEFAULT_MAX_MSG', 'DEFAULT_MAX_MESSAGE_SIZE',
                'DEFAULT_TX_CHAN', 'DEFAULT_RX_CHAN',
                'DEFAULT_MEASURE_NAMES', 'DEFAULT_TIMEOUT_RESPONSE')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
