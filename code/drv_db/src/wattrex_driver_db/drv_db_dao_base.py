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
from sqlalchemy import Column, DateTime, ForeignKey, String, Enum, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMINT, SMALLINT
from sqlalchemy.ext.declarative import declarative_base

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_types import DrvDbExpStatusE, DrvDbEquipStatusE

#######################              ENUMS               #######################


#######################             CLASSES              #######################
Base = declarative_base()
metadata = Base.metadata

class DrvDbBaseExperimentC(Base):
    '''
    Class method to create a simplified model of database GenericMeasures table.
    '''
    __tablename__ = 'Experiment'

    ExpID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Description = Column(String(250), nullable=False)
    DateCreation = Column(DateTime, nullable=False)
    DateBegin = Column(DateTime, nullable=True)
    DateFinish = Column(DateTime, nullable=True)
    Status = Column(Enum(*DrvDbExpStatusE.get_all_values()), nullable=False)

class DrvDbBaseGenericMeasureC(Base):
    '''
    Class method to create a simplified model of database GenericMeasures table.
    '''
    __tablename__ = 'GenericMeasures'
    __table_args__ = (ForeignKeyConstraint(['ExpID'], [DrvDbBaseExperimentC.ExpID]),)

    ExpID = Column(ForeignKey(DrvDbBaseExperimentC.ExpID), primary_key=True, nullable=False)
    MeasID = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Voltage = Column(MEDIUMINT(), nullable=False)
    Current = Column(MEDIUMINT(), nullable=False)
    Power = Column(INTEGER())

class DrvDbBaseExtendedMeasureC(Base):
    '''
    Class method to create a base model of database ExtendedMeasures table.
    '''
    __tablename__ = 'ExtendedMeasures'
    __table_args__ = (ForeignKeyConstraint(['ExpID'], [DrvDbBaseGenericMeasureC.ExpID]),
                      ForeignKeyConstraint(['MeasID'], [DrvDbBaseGenericMeasureC.MeasID]),)

    ExpID = Column(ForeignKey(DrvDbBaseGenericMeasureC.ExpID), primary_key= True, nullable=False)
    MeasID = Column(ForeignKey(DrvDbBaseGenericMeasureC.MeasID), primary_key= True, nullable=False)
    Value = Column(MEDIUMINT(), nullable=False)

class DrvDbAlarmC(Base):
    '''
    Class method to create a base model of database Alarm table.
    '''
    __tablename__ = 'Alarm'
    __table_args__ = (ForeignKeyConstraint(['ExpID'], [DrvDbBaseExperimentC.ExpID]),)

    ExpID = Column(ForeignKey(DrvDbBaseExperimentC.ExpID), primary_key=True, nullable=False)
    AlarmID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Code = Column(MEDIUMINT(unsigned=True), nullable=False)
    Value = Column(MEDIUMINT(), nullable=False)

class DrvDbBaseStatusC(Base):
    '''
    Class method to create a base model of database Status table.
    '''
    __tablename__ = 'Status'
    __table_args__ = (ForeignKeyConstraint(['ExpID'], [DrvDbBaseExperimentC.ExpID]),)

    StatusID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    ExpID = Column(ForeignKey(DrvDbBaseExperimentC.ExpID), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Status = Column(Enum(*DrvDbEquipStatusE.get_all_values()), nullable=False)
    ErrorCode = Column(SMALLINT(unsigned=True), nullable=False)
