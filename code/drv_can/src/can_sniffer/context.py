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
DEFAULT_CHAN_NUM_MSG : int = 200 # Max number of allowed message per chan
DEFAULT_MAX_MSG_SIZE : int = 250 # Size of message sent through IPC message queue
DEFAULT_TIMEOUT_SEND_MSG : float = 0.2 # s # Timeout for sending a message
DEFAULT_TIMEOUT_RX_MSG: float = 0.02 # s # Timeout for receiving a message
DEFAULT_NODE_PERIOD: int = 200 # ms # Period of the node
DEFAULT_NODE_NAME: str = 'CAN_SNIFFER' # Name of the node
DEFAULT_TX_NAME: str = 'TX_CAN' # Name of the TX channel
DEFAULT_IFACE_NAME: str = 'socketcan' # Name of the CAN interface
DEFAULT_IFACE_CHAN_NAME: str = 'can0' # Name of the CAN interface channel

CONSTANTS_NAMES = ('DEFAULT_CHAN_NUM_MSG', 'DEFAULT_MAX_MSG_SIZE',
                'DEFAULT_TIMEOUT_SEND_MSG', 'DEFAULT_TIMEOUT_RX_MSG',
                'DEFAULT_NODE_PERIOD', 'DEFAULT_NODE_NAME', 'DEFAULT_TX_NAME',
                'DEFAULT_IFACE_NAME', 'DEFAULT_IFACE_CHAN_NAME')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
