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
DEFAULT_MAX_HS_VOLT             = 14100     # Max high side voltage the epc has as hardware limits
DEFAULT_MIN_HS_VOLT             = 5300      # Min high side voltage the epc has as hardware limits
DEFAULT_MAX_LS_VOLT             = 5100      # Max low side voltage the epc has as hardware limits
DEFAULT_MIN_LS_VOLT             = 400       # Min low side voltage the epc has as hardware limits
DEFAULT_MAX_LS_CURR             = 15500     # Max low side current the epc has as hardware limits
DEFAULT_MIN_LS_CURR             = -15500    # Min low side current the epc has as hardware limits
DEFAULT_MAX_LS_PWR              = 800       # Max low side power the epc has as hardware limits
DEFAULT_MIN_LS_PWR              = -800      # Min low side power the epc has as hardware limits
DEFAULT_MAX_TEMP                = 700       # Max temperature the epc has as hardware limits
DEFAULT_MIN_TEMP                = -200      # Min temperature the epc has as hardware limits
DEFAULT_MAX_MSG : int           = 100 # Max number of allowed message per chan
DEFAULT_MAX_MESSAGE_SIZE : int  = 150 # Size of message sent through IPC message queue
DEFAULT_TX_CHAN : str           = 'TX_CAN' # Name of the TX channel in CAN
DEFAULT_RX_CHAN: str            = 'RX_CAN_EPC'  #Name of the RX channel for epc
DEFAULT_MAX_READS: int          = 3000 # Max number of reads to get data


CONSTANTS_NAMES = ('DEFAULT_MAX_HS_VOLT', 'DEFAULT_MIN_HS_VOLT',
                   'DEFAULT_MAX_LS_VOLT', 'DEFAULT_MIN_LS_VOLT',
                   'DEFAULT_MAX_LS_CURR', 'DEFAULT_MIN_LS_CURR',
                   'DEFAULT_MAX_LS_PWR', 'DEFAULT_MIN_LS_PWR',
                   'DEFAULT_MAX_TEMP', 'DEFAULT_MIN_TEMP',
                   'DEFAULT_MAX_MSG', 'DEFAULT_MAX_MESSAGE_SIZE',
                   'DEFAULT_TX_CHAN', 'DEFAULT_RX_CHAN',
                   'DEFAULT_MAX_READS')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
