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
                        String, Enum
from sqlalchemy.dialects.mysql import MEDIUMINT, SMALLINT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_types import (DrvDbBatteryTechE, DrvDbBipolarTypeE, DrvDbCyclingLimitE,
                        DrvDbCyclingModeE, DrvDbDeviceTypeE, DrvDbElectrolyteTypeE,
                        DrvDbLeadAcidChemistryE, DrvDbLithiumChemistryE, DrvDbMembraneTypeE,
                        DrvDbAvailableCuE, DrvDbConnStatusE, DrvDbRedoxPolarityE)
from .drv_db_dao_base import (DrvDbBaseStatusC, DrvDbBaseExperimentC, DrvDbBaseExtendedMeasureC,
                            DrvDbBaseGenericMeasureC)

#######################              ENUMS               #######################


#######################             CLASSES              #######################
Base = declarative_base()
metadata = Base.metadata

class DrvDbBatteryC(Base):
    '''
    Class method to create a DRVDB model of database Battery table.
    '''
    __tablename__ = 'Battery'

    BatID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Description = Column(String(250))
    Manufacturer = Column(String(20), nullable=False)
    Model = Column(String(20), nullable=False)
    SN = Column(String(30), nullable=False)
    FabDate = Column(DateTime, nullable=False)
    Tech = Column(Enum(*DrvDbBatteryTechE.get_all_values()), nullable=False)
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
    __table_args__ = (ForeignKeyConstraint(['BatID'], [DrvDbBatteryC.BatID]),)

    BatID = Column(ForeignKey(DrvDbBatteryC.BatID), primary_key=True)
    Capacity = Column(String(30), nullable=False)
    Chemistry = Column(Enum(*(DrvDbLithiumChemistryE.get_all_values())), nullable=False)

class DrvDbLeadAcidC(Base):
    '''
    Class method to create a DRVDB model of database LeadAcid table.
    '''
    __tablename__ = 'LeadAcid'
    __table_args__ = (ForeignKeyConstraint(['BatID'], [DrvDbBatteryC.BatID]),)

    BatID = Column(ForeignKey(DrvDbBatteryC.BatID), primary_key=True)
    Capacity = Column(String(30), nullable=False)
    Chemistry = Column(Enum(*(DrvDbLeadAcidChemistryE.get_all_values())), nullable=False)

class DrvDbRedoxStackC(Base):
    '''
    Class method to create a DRVDB model of database RedoxStack table.
    '''
    __tablename__ = 'RedoxStack'
    __table_args__ = (ForeignKeyConstraint(['BatID'], [DrvDbBatteryC.BatID]),)

    BatID = Column(ForeignKey(DrvDbBatteryC.BatID), primary_key=True)
    ElectrodeSize = Column(MEDIUMINT(unsigned=True), nullable=False)
    ElectrodeComposition = Column(String(30), nullable=False)
    BipolarType = Column(Enum(*(DrvDbBipolarTypeE.get_all_values())), nullable=False)
    MembraneType = Column(Enum(*(DrvDbMembraneTypeE.get_all_values())), nullable=False)
    ElectrolyteType = Column(Enum(*(DrvDbElectrolyteTypeE.get_all_values())), nullable=False)

class DrvDbComputationalUnitC(Base):
    '''
    Class method to create a DRVDB model of database ComputationalUnit table.
    '''
    __tablename__ = 'ComputationalUnit'

    CUID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(50), nullable=False)
    IP = Column(String(20), nullable=False)
    Port = Column(SMALLINT(unsigned=True), nullable=False)
    User = Column(String(30), nullable=False)
    LastConnection = Column(DateTime, nullable=False)
    Available = Column(Enum(*(DrvDbAvailableCuE.get_all_values())), nullable=False)

class DrvDbCyclerStationC(Base):
    '''
    Class method to create a DRVDB model of database CyclerStation table.
    '''
    __tablename__ = 'CyclerStation'
    __table_args__ = (ForeignKeyConstraint(['CUID'], [DrvDbComputationalUnitC.CUID]),)

    CSID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CUID = Column(ForeignKey(DrvDbComputationalUnitC.CUID), primary_key=True, \
                  nullable=False)
    Name = Column(String(30), nullable=False)
    Location = Column(String(30), nullable=False)
    RegisterDate = Column(DateTime, nullable=False)
    Parent = Column(MEDIUMINT(unsigned=True))
    Deprecated = Column(BOOLEAN, nullable=False)

class DrvDbCompatibleDeviceC(Base):
    '''
    Class method to create a DRVDB model of database CompatibleDevices table.
    '''
    __tablename__ = 'CompatibleDevices'

    CompDevID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Manufacturer = Column(String(30), nullable=False)
    Model = Column(String(30), nullable=False)
    DeviceType = Column(Enum(*DrvDbDeviceTypeE.get_all_values()), nullable=False)
    MinSWVersion = Column(SMALLINT(unsigned=True), nullable=False)
    VoltMin = Column(MEDIUMINT(unsigned=True))
    VoltMax = Column(MEDIUMINT(unsigned=True))
    CurrMin = Column(MEDIUMINT())
    CurrMax = Column(MEDIUMINT())

class DrvDbDetectedDeviceC(Base):
    '''
    Class method to create a DRVDB model of database DetectedDevice table.
    '''
    __tablename__ = 'DetectedDevices'
    __table_args__ = (ForeignKeyConstraint(['CUID'], [DrvDbComputationalUnitC.CUID]),
                      ForeignKeyConstraint(['CompDevID'], [DrvDbCompatibleDeviceC.CompDevID]),)

    DevID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CUID = Column(ForeignKey(DrvDbCyclerStationC.CSID), nullable=False)
    CompDevID = Column(ForeignKey(DrvDbCompatibleDeviceC.CompDevID), nullable=False)
    SN = Column(String(30), nullable=False)
    LinkName = Column(String(30), nullable=False)
    ConnStatus = Column(Enum(*(DrvDbConnStatusE.get_all_values())), nullable=False)

class DrvDbUsedDeviceC(Base):
    '''
    Class method to create a DRVDB model of database UsedDevices table.
    '''
    __tablename__ = 'UsedDevices'
    __table_args__ = (ForeignKeyConstraint(['CSID'], [DrvDbCyclerStationC.CSID]),
                      ForeignKeyConstraint(['DevID'], [DrvDbDetectedDeviceC.DevID]),)

    DevID = Column(ForeignKey(DrvDbDetectedDeviceC.DevID), primary_key=True, nullable=False)
    CSID = Column(ForeignKey(DrvDbCyclerStationC.CSID), primary_key=True, nullable=False)

class DrvDbLinkConfigurationC(Base):
    '''
    Class method to create a DRVDB model of database LinkConfiguration table.
    '''
    __tablename__ = 'LinkConfiguration'
    __table_args__ = (ForeignKeyConstraint(['CompDevID'], [DrvDbCompatibleDeviceC.CompDevID]),)

    CompDevID = Column(ForeignKey(DrvDbCompatibleDeviceC.CompDevID), primary_key=True,
                    nullable=False)
    Property = Column(String(30), primary_key = True, nullable=False)
    Value = Column(String(30), nullable=False)

class DrvDbAvailableMeasuresC(Base):
    '''
    Class method to create a DRVDB model of database AvailableMeasures table.
    '''
    __tablename__ = 'AvailableMeasures'
    __table_args__ = (ForeignKeyConstraint(['CompDevID'], [DrvDbCompatibleDeviceC.CompDevID]),)

    MeasType = Column(MEDIUMINT(unsigned=True), primary_key=True)
    CompDevID = Column(ForeignKey(DrvDbCompatibleDeviceC.CompDevID), nullable=False)
    MeasName = Column(String(20), nullable=False)

class DrvDbUsedMeasuresC(Base):
    '''
    Class method to create a DRVDB model of database UsedMeasures table.
    '''
    __tablename__ = 'UsedMeasures'
    __table_args__ = (ForeignKeyConstraint(['MeasType'], [DrvDbAvailableMeasuresC.MeasType]),
                      ForeignKeyConstraint(['DevID'], [DrvDbDetectedDeviceC.DevID]),
                      ForeignKeyConstraint(['CSID'], [DrvDbCyclerStationC.CSID]),)

    UsedMeasID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CSID = Column(ForeignKey(DrvDbCyclerStationC.CSID), nullable=False)
    MeasType = Column(ForeignKey(DrvDbAvailableMeasuresC.MeasType), nullable=False)
    DevID = Column(ForeignKey(DrvDbDetectedDeviceC.DevID), nullable=False)
    CustomName = Column(String(30), nullable=False)

class DrvDbProfileC(Base):
    '''
    Class method to create a DRVDB model of database Profile table.
    '''
    __tablename__ = 'Profile'

    ProfID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(40), nullable=False)
    Description = Column(String(250), nullable=False)
    VoltMax = Column(MEDIUMINT(unsigned=True))
    VoltMin = Column(MEDIUMINT(unsigned=True))
    CurrMax = Column(MEDIUMINT())
    CurrMin = Column(MEDIUMINT())

class DrvDbInstructionC(Base):
    '''
    Class method to create a DRVDB model of database Instructions table.
    '''
    __tablename__ = 'Instructions'
    __table_args__ = (ForeignKeyConstraint(['ProfID'], [DrvDbProfileC.ProfID]),)

    InstrID = Column(MEDIUMINT(), primary_key=True, nullable=False)
    ProfID = Column(ForeignKey(DrvDbProfileC.ProfID), primary_key=True, nullable=False)
    Mode = Column(Enum(*(DrvDbCyclingModeE.get_all_values())), nullable=False)
    SetPoint = Column(MEDIUMINT(), nullable=False)
    LimitType = Column(Enum(*(DrvDbCyclingLimitE.get_all_values())), nullable=False)
    LimitPoint = Column(MEDIUMINT(), nullable=False)

class DrvDbMasterExperimentC(DrvDbBaseExperimentC): #pylint: disable=too-many-instance-attributes
    '''
    Class method to create a DRVDB model of database Experiment table.
    '''
    __tablename__ = 'Experiment'
    __table_args__ = (ForeignKeyConstraint(['CSID'], [DrvDbCyclerStationC.CSID]),
                      ForeignKeyConstraint(['BatID'], [DrvDbBatteryC.BatID]),
                      ForeignKeyConstraint(['ProfID'],[DrvDbProfileC.ProfID]),
                    {'extend_existing': True},)

    CSID = Column(ForeignKey(DrvDbCyclerStationC.CSID), nullable=False)
    BatID = Column(ForeignKey(DrvDbBatteryC.BatID), nullable=False)
    ProfID = Column(ForeignKey(DrvDbProfileC.ProfID), nullable=False)


class DrvDbMasterGenericMeasureC(DrvDbBaseGenericMeasureC): #pylint: disable=too-many-instance-attributes
    '''
    Class method to create a model of cache database GenericMeasures table.
    '''
    __tablename__ = 'GenericMeasures'
    __table_args__ = (ForeignKeyConstraint(['InstrID'], [DrvDbInstructionC.InstrID]),
                      {'extend_existing': True},)

    InstrID = Column(ForeignKey(DrvDbInstructionC.InstrID), nullable=False)
    PowerMode = Column(Enum(*DrvDbCyclingModeE.get_all_values()))

class DrvDbMasterExtendedMeasureC(DrvDbBaseExtendedMeasureC):
    '''
    Class method to create a DRVDB model of database ExtendedMeasures table.
    '''
    __tablename__ = 'ExtendedMeasures'
    __table_args__ = (ForeignKeyConstraint(['UsedMeasID'], [DrvDbUsedMeasuresC.UsedMeasID]),
                      {'extend_existing': True},)

    UsedMeasID = Column(ForeignKey(DrvDbUsedMeasuresC.UsedMeasID),
                      primary_key=True, nullable=False)

class DrvDbMasterStatusC(DrvDbBaseStatusC):
    '''
    Class method to create a DRVDB model of database Status table.
    '''
    __tablename__ = 'Status'
    __table_args__ = (ForeignKeyConstraint(['DevID'], [DrvDbUsedDeviceC.DevID]),
                      {'extend_existing': True},)

    DevID = Column(ForeignKey(DrvDbUsedDeviceC.DevID), primary_key=True, nullable=False)

class DrvDbRedoxElectrolyteC(Base):
    '''
    Class method to create a DRVDB model of database RedoxElectrolyte table.
    '''
    __tablename__ = 'RedoxElectrolyte'
    __table_args__ = (ForeignKeyConstraint(['BatID'], [DrvDbBatteryC.BatID]),
                      ForeignKeyConstraint(['ExpID'], [DrvDbMasterExperimentC.ExpID]),)

    BatID = Column(ForeignKey(DrvDbBatteryC.BatID), primary_key=True, nullable=False)
    ExpID = Column(ForeignKey(DrvDbMasterExperimentC.ExpID), primary_key=True, nullable=False)
    Polarity = Column(Enum(*(DrvDbRedoxPolarityE.get_all_values())), primary_key=True,
                      nullable=False)
    ElectrolyteVol = Column(MEDIUMINT(unsigned=True), nullable=False)
    InitialSOC = Column(MEDIUMINT(unsigned=True), nullable=False)
    MinFlowRate = Column(MEDIUMINT(unsigned=True), nullable=False)
    MaxFlowRate = Column(MEDIUMINT(unsigned=True), nullable=False)
