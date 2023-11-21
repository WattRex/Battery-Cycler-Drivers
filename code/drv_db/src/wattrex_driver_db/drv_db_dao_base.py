#!/usr/bin/python3
'''
Create a ORM model of the defined database.

This document's base structure is generated automaticly using sqlacodegen extracting data from DB.\
Attributes in this script does not follow PEP8 snake_case naming convention.

sqlacodegen mysql+mysqlconnector://user:password@ip:port/db_name --outfile drv_db_dao.py
'''
#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
from sqlalchemy import Column, DateTime, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import MEDIUMINT
from sqlalchemy.orm import declarative_base

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_dao_cache import DrvDbCacheExperimentC

#######################              ENUMS               #######################


#######################             CLASSES              #######################
Base = declarative_base()
metadata = Base.metadata

class DrvDbAlarmC(Base):
    '''
    Class method to create a base model of database Alarm table.
    '''
    __tablename__ = 'Alarm'
    __table_args__ = (ForeignKeyConstraint(['ExpID'], [DrvDbCacheExperimentC.ExpID]),)

    ExpID = Column(primary_key=True, nullable=False)
    AlarmID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Code = Column(MEDIUMINT(unsigned=True), nullable=False)
    Value = Column(MEDIUMINT(), nullable=False)
