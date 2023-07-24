#!/usr/bin/python3
"""
    This module works to have a configuration, mainly for the logger.
"""
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
import yaml

sys.path.append(os.getcwd())  #get absolute path
#######################      LOGGING CONFIGURATION       #######################
#Not available in this file because it is imported in the logger file
#######################          MODULE IMPORTS          #######################


#######################          PROJECT IMPORTS         #######################


#######################              ENUMS               #######################


#######################             CLASSES              #######################
class SysConfSectionNotFoundErrorC(Exception):
    """Handle exception thrown in SysConf sectionNotFoundC .

    Args:
        Exception ([type]): [description]
    """
    def __init__(self, message) -> None:
        '''
        Exception raised for errors when a section is not found in the file.

        Args:
            - message (str): explanation of the error
        '''
        super().__init__(message)


#######################            FUNCTIONS             #######################
def sys_conf_read_config_params(filename:str = 'config.yaml',
                            section: str|None = None) -> dict:
    '''
    Reads config parameters from a config file.

    Args:
        - filename (str, optional): Path to the file used to read the configuration.
        Defaults to 'config.yaml'.
        - section (str, optional): Section to be parsed from the configuration file.

    Raises:
        - SYS_CONF_Section_Not_Found_Error_c: Throw an exception if the section is
        not found in the file or the file does not exists.

    Returns:
        - data (dict): Dictionary with the configuration section read.
    '''
    data = {}
    with open(filename, 'r', encoding= 'utf-8') as file:
        data = yaml.safe_load(file)
    if section is not None:
        if section not in data:
            raise SysConfSectionNotFoundErrorC( \
                f"Section {section} not found in the {filename} file")
        else:
            data = data[section]
    return data

def sys_conf_get_argv_password() -> str:
    '''
    Get the password from the sys.argv if a -p or --password argument
    followed by the password was given in the python command.
    Examples: \n
    `python3 main.py -p s3cr3tp4ssw0rd`\n
    `python3 main.py --password s3cr3tp4ssw0rd`

    Returns:
        - password (str): Returns the password given as argument in the python
        command or "" (empty str) if no argument was given.
    '''
    password = ''
    if len(sys.argv) > 1:
        if '-p' in sys.argv:
            list_index = sys.argv.index('-p')
            password = sys.argv[list_index + 1]
        elif '--password' in sys.argv:
            list_index = sys.argv.index('--password')
            password = sys.argv[list_index + 1]
    return password
