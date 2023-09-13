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
from sqlalchemy import Column, DateTime, ForeignKey, ForeignKeyConstraint, \
                        Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMINT, SMALLINT
from sqlalchemy.ext.declarative import declarative_base

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_types import DrvDbExpStatusE
from .drv_db_dao_base import DrvDbBaseExperimentC, DrvDbBaseGenericMeasureC,\
    DrvDbBaseExtendedMeasureC, DrvDbBaseStatusC

#######################              ENUMS               #######################


#######################             CLASSES              #######################
Base = declarative_base()
metadata = Base.metadata

class DrvDbExperimentC(DrvDbBaseExperimentC):
    '''
    Class method to create a simplified model of database Experiment table.
    '''
    __tablename__: str = 'Experiment'
    __table_args__ = {'extend_existing': True}

    CSID = Column(MEDIUMINT(unsigned=True), nullable=False)
    BatID = Column(MEDIUMINT(unsigned=True), nullable=False)
    ProfID = Column(MEDIUMINT(unsigned=True), nullable=False)

class DrvDbGenericMeasureC(DrvDbBaseGenericMeasureC):
    '''
    Class method to create a model of cache database GenericMeasures table.
    '''
    __tablename__ = 'GenericMeasures'
    __table_args__ = {'extend_existing': True}

    InstrID = Column(MEDIUMINT(unsigned=True), nullable=False)

class DrvDbExtendedMeasureC(DrvDbBaseExtendedMeasureC):
    '''
    Class method to create a model of cache database ExtendedMeasures table.
    '''
    __tablename__ = 'ExtendedMeasures'
    __table_args__ = {'extend_existing': True}

    MeasType = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)

class DrvDbStatusC(DrvDbBaseStatusC):
    '''
    Class method to create a base model of database Status table.
    '''
    __tablename__ = 'Status'
    __table_args__ = {'extend_existing': True}

    DevID = Column(MEDIUMINT(unsigned=True), nullable=False)
