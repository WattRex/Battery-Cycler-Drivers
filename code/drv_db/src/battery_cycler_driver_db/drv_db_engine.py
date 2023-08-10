#!/usr/bin/python3
'''
Execute a SQLAlchemy database on the given database .

Raises:
    err: Error while connecting with DB.
    ConnectionError: Max db connection resets reached. Connection with db may have been lost.
'''
#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from mysql.connector.errors import Error

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_config_tool import sys_conf_read_config_params

from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################


#######################              ENUMS               #######################


#######################             CLASSES              #######################
class DrvDbSqlEngineC:
    '''
    Classmethod to create a SqlAlchemy engine.
    '''

    __MAX_RESETS = 2

    def __init__(self, config_file='../config/.cred.yaml'):
        '''
        Create an connector to the MySQL database server

        Args:
            config_file (str, optional): path to the configuration file. \
                Defaults to '../config/.cred.yaml'.
        '''
        try:
            self.config_file = config_file
            # read connection parameters
            params = sys_conf_read_config_params(filename=config_file, section='database')

            url = 'mysql+mysqlconnector://' + params['user'] + ':' + params['password'] + '@' \
                + params['host'] + ':' + str(params['port']) + '/' + params['database']
            self.engine = create_engine(url, echo=False, future=True)
            self.session : Session = Session(self.engine, future=True)
            self.session.begin()
            self.n_resets = 0

        except Error as err:
            log.error(err)
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
        params = sys_conf_read_config_params(filename=self.config_file, section='database')
        url = 'mysql+mysqlconnector://' + params['user'] + ':' + params['password'] + '@' \
            + params['host'] + ':' + str(params['port']) + '/' + params['database']
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
