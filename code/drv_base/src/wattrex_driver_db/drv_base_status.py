#!/usr/bin/python3
'''
Create a ORM model of the defined database.

This document's base structure is generated automaticly using sqlacodegen extracting data from DB.\
Attributes in this script does not follow PEP8 snake_case naming convention.

sqlacodegen mysql+mysqlconnector://user:password@ip:port/db_name --outfile drv_db_dao.py
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from enum import Enum
#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################
class DrvBaseStatusE(Enum):
    '''Status of the driver power.
    '''
    COMM_ERROR = -1
    OK = 0
    INTERNAL_ERROR = 1

#######################             CLASSES              #######################
class DrvBaseStatusC:
    '''Handles status of the driver power.
    '''
    def __init__(self, error: int|DrvBaseStatusE) -> None:
        if isinstance(error, DrvBaseStatusE):
            self.__status = error
            self.__error_code = error.value
        else:
            self.__error_code = error
            if error > 0:
                self.__status = DrvBaseStatusE.INTERNAL_ERROR
            else:
                self.__status = DrvBaseStatusE(error)

    def __str__(self) -> str:
        result = f"Error code: {self.__error_code} \t Status: {self.__status}"
        return result

    def __eq__(self, cmp_obj: Enum) -> bool:
        return self.__status == cmp_obj

    @property
    def error_code(self) -> int:
        '''The error code associated with this request .
        Args:
            - None
        Returns:
            - (int): The error code associated with this request.
        Raises:
            - None
        '''
        return self.__error_code

    @property
    def value(self) -> int:
        ''' Value of status.
        Args:
            - None
        Returns:
            - (int): Value of status.
        Raises:
            - None
        '''
        return self.__status.value

    @property
    def name(self) -> str:
        ''' Name of status.
        Args:
            - None
        Returns:
            - (int): name of status.
        Raises:
            - None
        '''
        return self.__status.name
