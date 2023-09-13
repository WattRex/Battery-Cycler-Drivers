#!/usr/bin/python3
'''
Execute a SQLAlchemy database on the given database .

Raises:
    err: Error while connecting with DB.
    ConnectionError: Max db connection resets reached. Connection with db may have been lost.
'''
#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################
from typing import Any

#######################       THIRD PARTY IMPORTS        #######################
# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_config_tool import sys_conf_read_config_params
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
from .drv_db_types import DrvDbTypeE

#######################              ENUMS               #######################


#######################             CLASSES              #######################
class DrvDbSqlEngineC:
    '''
    Classmethod to create a SqlAlchemy engine.
    '''

    __MAX_RESETS = 2

    def __init__(self, db_type : DrvDbTypeE, config_file):
        '''
        Create an connector to the MySQL or SQLite database server

        Args:
            config_file (str, optional): path to the configuration file. \
        '''
        try:
            self.config_file = config_file
            # read connection parameters
            params = sys_conf_read_config_params(filename=config_file, section='database')
            # create engine
            if db_type == DrvDbTypeE.CACHE_DB and params['engine'] == DrvDbTypeE.CACHE_DB.value:
                url = 'mysql+mysqlconnector://'
            elif db_type == DrvDbTypeE.MASTER_DB and params['engine'] == DrvDbTypeE.CACHE_DB.value:
                url = 'mysql+mysqlconnector://'
            else:
                raise ConnectionError("Data base type or engine not supported")

            url += params['user'] + ':' + params['password'] + '@' \
                    + params['host'] + ':' + str(params['port']) + '/' + params['database']
            self.engine: Engine = create_engine(url=url, echo=False, future=True)
            self.session : Session = Session(bind=self.engine, future=True)
            self.session.begin()
            self.n_resets = 0

        except Exception as err:
            log.error(msg="Error on DB Session creation. Please check DB credentials and params")
            log.error(msg=err)
            raise err


    def commit_changes(self) -> None:
        '''
        Perform a commit againt the used database. If any error occurs, a
        rollback is performed.

        Raises:
            err: Throw an exception if any error occurs during commit transaction.
        '''
        try:
            self.session.commit()
        except Exception as err:
            log.critical(err)
            log.critical("Error while commiting change to DB. Performing rollback...")
            self.session.rollback()


    def close_connection(self) -> None:
        '''
        Close the connection with the database.
        '''
        self.commit_changes()
        self.session.close()


    def __reset_engine(self) -> None:
        '''
        Create a new engine and initialize it
        '''
        params: dict[str, Any] = sys_conf_read_config_params(#pylint: disable=unsubscriptable-object
            filename=self.config_file, section='database')

        url = 'mysql+mysqlconnector://' + params['user'] + ':'\
            + params['password'] + '@' + params['host'] + ':'\
            + str(params['port']) + '/' + params['database']
        self.engine = create_engine(url, echo=False, future=True)
        self.session = Session(self.engine, future=True)
        self.session.begin()


    def reset(self) -> None:
        '''
        Resets the connection to the database .

        Raises:
            ConnectionError: Max db connection resets reached. Connection \
                                  with db may have been lost.
        '''
        if self.n_resets <= self.__MAX_RESETS:
            self.__reset_engine()
            self.n_resets += 1
        else:
            raise ConnectionError("Max db connection resets reached. Connection \
                                  with db may have been lost.")


#######################            FUNCTIONS             #######################
