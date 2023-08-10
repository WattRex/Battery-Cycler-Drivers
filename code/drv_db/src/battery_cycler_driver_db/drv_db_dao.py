#!/usr/bin/python3
'''
Create a ORM model of the defined database.

This document's base structure is generated automaticly using sqlacodegen extracting data from DB.\
Attributes in this script does not follow PEP8 snake_case naming convention.

sqlacodegen mysql+mysqlconnector://user:password@ip:port/db_name --outfile drv_db_dao.py
'''
#######################        MANDATORY IMPORTS         #######################
import sys
import os

#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################
from sqlalchemy import Column, DateTime, ForeignKey, ForeignKeyConstraint, \
                        Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMINT, SMALLINT
from sqlalchemy.ext.declarative import declarative_base

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_types import DrvDbBatteryTechE, DrvDbBipolarTypeE, DrvDbCyclingLimitE, \
                        DrvDbCyclingModeE, DrvDbDeviceTypeE, DrvDbElectrolyteTypeE, \
                        DrvDbEquipStatusE, DrvDbExpStatusE, DrvDbLeadAcidChemistryE, \
                        DrvDbLithiumChemistryE, DrvDbMembraneTypeE, DrvDbAvailableCuE

#######################              ENUMS               #######################


#######################             CLASSES              #######################
Base = declarative_base()
metadata = Base.metadata


class DrvDbBatteryC(Base):
    '''
    Class method to create a DRVDB model of database Battery table.
    '''
    __tablename__ = 'Battery'
    __table_args__ = (
        Index('Battery_unq_1', 'Name', 'Manufacturer', 'Model', 'SN', unique=True),
    )

    BatID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Description = Column(String(250))
    Manufacturer = Column(String(20), nullable=False)
    Model = Column(String(20), nullable=False)
    SN = Column(String(30), nullable=False)
    FabDate = Column(DateTime, nullable=False)
    Tech = Column(DrvDbBatteryTechE, nullable=False)
    CellsNum = Column(MEDIUMINT(unsigned=True), nullable=False)
    CellVoltMin = Column(MEDIUMINT(unsigned=True))
    CellVoltMax = Column(MEDIUMINT(unsigned=True))
    VoltMin = Column(MEDIUMINT(unsigned=True), nullable=False)
    VoltMax = Column(MEDIUMINT(unsigned=True), nullable=False)
    CurrMin = Column(MEDIUMINT(), nullable=False)
    CurrMax = Column(MEDIUMINT(), nullable=False)


class DrvDbLithiumC(Base):
    '''
    Class method to create a DRVDB model of database Lithium table.
    '''
    __tablename__ = 'Lithium'

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True)
    Capacity = Column(String(30), nullable=False)
    Chemistry = Column(DrvDbLithiumChemistryE, nullable=False)

    Battery = relationship('DrvDbBatteryC')


class DrvDbLeadAcidC(Base):
    '''
    Class method to create a DRVDB model of database LeadAcid table.
    '''
    __tablename__ = 'LeadAcid'

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True)
    Capacity = Column(String(30), nullable=False)
    Chemistry = Column(DrvDbLeadAcidChemistryE, nullable=False)

    Battery = relationship('DrvDbBatteryC')


class DrvDbRedoxStackC(Base):
    '''
    Class method to create a DRVDB model of database RedoxStack table.
    '''
    __tablename__ = 'RedoxStack'

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True)
    ElectrodeSize = Column(MEDIUMINT(unsigned=True), nullable=False)
    ElectrodeComposition = Column(String(30), nullable=False)
    BipolarType = Column(DrvDbBipolarTypeE, nullable=False)
    MembraneType = Column(DrvDbMembraneTypeE, nullable=False)
    ElectrolyteType = Column(DrvDbElectrolyteTypeE, nullable=False)

    Battery = relationship('DrvDbBatteryC')


class DrvDbCompatibleDeviceC(Base):
    '''
    Class method to create a DRVDB model of database CompatibleDevices table.
    '''
    __tablename__ = 'CompatibleDevices'
    __table_args__ = (
        Index('CompatibleDevices_unq_1', 'Name', 'Manufacturer', 'DeviceType', unique=True),
    )

    CompDevID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Manufacturer = Column(String(30), nullable=False)
    DeviceType = Column(DrvDbDeviceTypeE, nullable=False)
    MinSWVersion = Column(SMALLINT(unsigned=True), nullable=False)
    VoltMin = Column(MEDIUMINT(unsigned=True))
    VoltMax = Column(MEDIUMINT(unsigned=True))
    CurrMin = Column(MEDIUMINT())
    CurrMax = Column(MEDIUMINT())


class DrvDbComputationalUnitC(Base):
    '''
    Class method to create a DRVDB model of database ComputationalUnit table.
    '''
    __tablename__ = 'ComputationalUnit'
    __table_args__ = (
        Index('ComputationalUnit_unq_1', 'Name', 'IP', 'Port', unique=True),
    )

    CUID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(50), nullable=False)
    IP = Column(String(20), nullable=False)
    Port = Column(SMALLINT(unsigned=True), nullable=False)
    User = Column(String(20), nullable=False)
    Pass = Column(String(100), nullable=False)
    LastConnection = Column(DateTime, nullable=False)
    Available = Column(DrvDbAvailableCuE, nullable=False)


class DrvDbCycleStationC(Base):
    '''
    Class method to create a DRVDB model of database CycleStation table.
    '''
    __tablename__ = 'CycleStation'

    CSID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CUID = Column(ForeignKey('ComputationalUnit.CUID'), primary_key=True, \
                  nullable=False, index=True)
    Name = Column(String(30), nullable=False)
    Location = Column(String(30), nullable=False)
    RegisterDate = Column(DateTime, nullable=False)

    ComputationalUnit = relationship('DrvDbComputationalUnitC')


class DrvDbUsedDeviceC(Base):
    '''
    Class method to create a DRVDB model of database UsedDevices table.
    '''
    __tablename__ = 'UsedDevices'
    __table_args__ = (
        Index('UsedDevices_unq_1', 'CSID', 'CompDevID', 'SN', unique=True),
    )

    DevID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CSID = Column(ForeignKey('CycleStation.CSID'), primary_key=True, nullable=False)
    CompDevID = Column(ForeignKey('CompatibleDevices.CompDevID'), nullable=False, index=True)
    SN = Column(String(30), nullable=False)
    UdevName = Column(String(30), nullable=False)

    CycleStation = relationship('DrvDbCycleStationC')
    CompatibleDevice = relationship('DrvDbCompatibleDeviceC')


class DrvDbProfileC(Base):
    '''
    Class method to create a DRVDB model of database Profile table.
    '''
    __tablename__ = 'Profile'

    ProfID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(40), nullable=False)
    Description = Column(String(250), nullable=False)
    VoltMax = Column(MEDIUMINT(unsigned=True), nullable=False)
    VoltMin = Column(MEDIUMINT(unsigned=True), nullable=False)
    CurrMax = Column(MEDIUMINT(), nullable=False)
    CurrMin = Column(MEDIUMINT(), nullable=False)


class DrvDbExperimentC(Base):
    '''
    Class method to create a DRVDB model of database Experiment table.
    '''
    __tablename__ = 'Experiment'

    ExpID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Description = Column(String(250), nullable=False)
    DateCreation = Column(DateTime, nullable=False)
    DateBegin = Column(DateTime, nullable=False)
    DateFinish = Column(DateTime, nullable=False)
    Status = Column(DrvDbExpStatusE, nullable=False)
    CSID = Column(ForeignKey('CycleStation.CSID'), nullable=False, index=True)
    BatID = Column(ForeignKey('Battery.BatID'), nullable=False, index=True)
    ProfID = Column(ForeignKey('Profile.ProfID'), nullable=False, index=True)

    Battery = relationship('DrvDbBatteryC')
    CycleStation = relationship('DrvDbCycleStationC')
    Profile = relationship('DrvDbProfileC')


class DrvDbAlarmC(Base):
    '''
    Class method to create a DRVDB model of database Alarm table.
    '''
    __tablename__ = 'Alarm'

    ExpID = Column(ForeignKey('Experiment.ExpID'), primary_key=True, nullable=False)
    AlarmID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    Code = Column(MEDIUMINT(unsigned=True), nullable=False)
    Value = Column(MEDIUMINT(), nullable=False)

    Experiment = relationship('DrvDbExperimentC')


class DrvDbStatusC(Base):
    '''
    Class method to create a DRVDB model of database Status table.
    '''
    __tablename__ = 'Status'

    ExpID = Column(ForeignKey('Experiment.ExpID'), primary_key=True, nullable=False)
    DevID = Column(ForeignKey('UsedDevices.DevID'), primary_key=True, nullable=False, index=True)
    Timestamp = Column(DateTime, nullable=False)
    Status = Column(DrvDbEquipStatusE, nullable=False)
    ErrorCode = Column(SMALLINT(unsigned=True), nullable=False)

    UsedDevice = relationship('DrvDbUsedDeviceC')
    Experiment = relationship('DrvDbExperimentC')


class DrvDbRedoxElectrolyteC(Base):
    '''
    Class method to create a DRVDB model of database RedoxElectrolyte table.
    '''
    __tablename__ = 'RedoxElectrolyte'

    ExpID = Column(ForeignKey('Experiment.ExpID'), primary_key=True, nullable=False)
    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True, nullable=False, index=True)
    ElectrolyteVol = Column(MEDIUMINT(unsigned=True), nullable=False)
    MaxFlowRate = Column(MEDIUMINT(unsigned=True), nullable=False)

    Battery = relationship('DrvDbBatteryC')
    Experiment = relationship('DrvDbExperimentC')


class DrvDbInstructionC(Base):
    '''
    Class method to create a DRVDB model of database Instructions table.
    '''
    __tablename__ = 'Instructions'

    InstrID = Column(MEDIUMINT(), primary_key=True, nullable=False)
    ProfID = Column(ForeignKey('Profile.ProfID'), primary_key=True, nullable=False, index=True)
    Mode = Column(DrvDbCyclingModeE, nullable=False)
    SetPoint = Column(MEDIUMINT(), nullable=False)
    LimitType = Column(DrvDbCyclingLimitE, nullable=False)
    LimitPoint = Column(MEDIUMINT(), nullable=False)

    Profile = relationship('DrvDbProfileC')


class DrvDbGenericMeasureC(Base):
    '''
    Class method to create a DRVDB model of database GenericMeasures table.
    '''
    __tablename__ = 'GenericMeasures'

    ExpID = Column(ForeignKey('Experiment.ExpID'), primary_key=True, nullable=False)
    MeasID = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    Timestamp = Column(DateTime, nullable=False)
    InstrID = Column(ForeignKey('Instructions.InstrID'), nullable=False, index=True)
    Voltage = Column(MEDIUMINT(), nullable=False)
    Current = Column(MEDIUMINT(), nullable=False)

    Experiment = relationship('DrvDbExperimentC')
    Instruction = relationship('DrvDbInstructionC')


class DrvDbMeasuresDeclarationC(Base):
    '''
    Class method to create a DRVDB model of database MeasuresDeclaration table.
    '''
    __tablename__ = 'MeasuresDeclaration'

    MeasType = Column(MEDIUMINT(unsigned=True), primary_key=True)
    MeasName = Column(String(20), nullable=False, unique=True)


class DrvDbExtendedMeasureC(Base):
    '''
    Class method to create a DRVDB model of database ExtendedMeasures table.
    '''
    __tablename__ = 'ExtendedMeasures'
    __table_args__ = (
        ForeignKeyConstraint(['ExpID', 'MeasID'], \
                             ['GenericMeasures.ExpID', 'GenericMeasures.MeasID']),
        Index('ExtendedMeasures_fk_3', 'ExpID', 'MeasID')
    )

    ExpID = Column(ForeignKey('Experiment.ExpID'), primary_key=True, nullable=False)
    MeasType = Column(ForeignKey('MeasuresDeclaration.MeasType'), \
                      primary_key=True, nullable=False, index=True)
    MeasID = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    Value = Column(MEDIUMINT(), nullable=False)

    GenericMeasure = relationship('DrvDbGenericMeasureC')
    Experiment = relationship('DrvDbExperimentC')
    MeasuresDeclaration = relationship('DrvDbMeasuresDeclarationC')
