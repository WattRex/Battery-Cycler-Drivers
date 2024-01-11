#!/usr/bin/python3
'''
This module manages the constants variables.
Those variables are used in the scripts inside the module and can be modified
in a config yaml file specified in the environment variable with name declared
in system_config_tool.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
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

DEFAULT_TIMEOUT_SEND_MSG: float = 0.1
DEFAULT_TIMEOUT_RX_MSG: float   = 0.02
DEFAULT_NODE_PERIOD: int        = 40
DEFAULT_NODE_NAME: str          = 'SCPI'

DEFAULT_CHAN_NUM_MSG : int      = 200 # Max number of allowed message per chan
DEFAULT_MAX_MSG_SIZE : int      = 350 # Size of message sent through IPC message queue
DEFAULT_TX_CHAN : str           = 'TX_SCPI' # Name of the TX channel in CAN
DEFAULT_RX_CHAN: str            = 'RX_SCPI_'  #Name of the RX channel for epc
DEFAULT_NUM_ATTEMPTS: int          = 10 # Max number of reads to get data


CONSTANTS_NAMES = ('DEFAULT_TIMEOUT_SEND_MSG', 'DEFAULT_TIMEOUT_RX_MSG', 'DEFAULT_NODE_PERIOD',
                   'DEFAULT_NODE_NAME', 'DEFAULT_CHAN_NUM_MSG', 'DEFAULT_MAX_MSG_SIZE',
                   'DEFAULT_TX_CHAN', 'DEFAULT_RX_CHAN', 'DEFAULT_NUM_ATTEMPTS')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
