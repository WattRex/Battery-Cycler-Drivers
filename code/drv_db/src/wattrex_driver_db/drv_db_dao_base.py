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
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr

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

class DrvDbBaseExperimentC:
    '''
    Class method to create a simplified model of database GenericMeasures table.
    '''
    ExpID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Description = Column(String(250), nullable=False)
    DateCreation = Column(DateTime, nullable=False)
    DateBegin = Column(DateTime, nullable=True)
    DateFinish = Column(DateTime, nullable=True)
    Status = Column(Enum(*DrvDbExpStatusE.get_all_values()), nullable=False)

class DrvDbBaseGenericMeasureC:
    '''
    Class method to create a simplified model of database GenericMeasures table.
    '''
    MeasID = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Voltage = Column(MEDIUMINT(), nullable=False)
    Current = Column(MEDIUMINT(), nullable=False)
    Power = Column(INTEGER())

    @declared_attr
    def ExpID(cls): # pylint: disable=no-self-argument, invalid-name
        '''
        Returns the foreign key column for the experiment ID.

        :return: The foreign key column for the experiment ID.
        :rtype: Column
        '''
        log.debug("EXPID DrvDbBaseGenericMeasureC")
        return Column(ForeignKey(DrvDbBaseExperimentC.ExpID), primary_key=True, nullable=False)

class DrvDbBaseExtendedMeasureC:
    '''
    Class method to create a base model of database ExtendedMeasures table.
    '''
    Value = Column(MEDIUMINT(), nullable=False)

    @declared_attr
    def ExpID(cls): # pylint: disable=no-self-argument, invalid-name
        '''
        Returns the foreign key column for the experiment ID.

        :return: The foreign key column for the experiment ID.
        :rtype: Column
        '''
        log.debug("EXPID DrvDbBaseExtendedMeasureC")
        return Column(ForeignKey(DrvDbBaseExperimentC.ExpID), primary_key= True, nullable=False)

    @declared_attr
    def MeasID(cls): # pylint: disable=no-self-argument, invalid-name
        '''
        Returns the foreign key column for the Meas ID.

        :return: The foreign key column for the Meas ID.
        :rtype: Column
        '''
        return Column(ForeignKey(DrvDbBaseGenericMeasureC.MeasID), primary_key= True,
                      nullable=False)

class DrvDbBaseStatusC:
    '''
    Class method to create a base model of database Status table.
    '''

    StatusID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Status = Column(Enum(*DrvDbEquipStatusE.get_all_values()), nullable=False)
    ErrorCode = Column(SMALLINT(unsigned=True), nullable=False)

    @declared_attr
    def ExpID(cls): # pylint: disable=no-self-argument, invalid-name
        '''
        Returns the foreign key column for the experiment ID.

        :return: The foreign key column for the experiment ID.
        :rtype: Column
        '''
        log.debug("EXPID DrvDbBaseStatusC")
        return Column(ForeignKey(DrvDbBaseExperimentC.ExpID), primary_key=True, nullable=False)

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
