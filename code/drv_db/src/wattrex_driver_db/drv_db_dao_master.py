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
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import MEDIUMINT, SMALLINT, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_types import DrvDbBatteryTechE, DrvDbBipolarTypeE, DrvDbCyclingLimitE, \
                        DrvDbCyclingModeE, DrvDbDeviceTypeE, DrvDbElectrolyteTypeE, \
                        DrvDbLeadAcidChemistryE, DrvDbLithiumChemistryE, DrvDbMembraneTypeE,\
                        DrvDbAvailableCuE
from .drv_db_dao_base import DrvDbBaseStatusC, DrvDbBaseExperimentC, DrvDbBaseExtendedMeasureC, \
                            DrvDbBaseGenericMeasureC
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
    __table_args__ = (ForeignKeyConstraint(['BatID'], ['Battery.BatID']),)

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True)
    Capacity = Column(String(30), nullable=False)
    Chemistry = Column(Enum(*(DrvDbLithiumChemistryE.get_all_values())), nullable=False)

    # Battery = relationship('DrvDbBatteryC')

class DrvDbLeadAcidC(Base):
    '''
    Class method to create a DRVDB model of database LeadAcid table.
    '''
    __tablename__ = 'LeadAcid'
    __table_args__ = (ForeignKeyConstraint(['BatID'], ['Battery.BatID']),)

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True)
    Capacity = Column(String(30), nullable=False)
    Chemistry = Column(Enum(*(DrvDbLeadAcidChemistryE.get_all_values())), nullable=False)

    # Battery = relationship('DrvDbBatteryC')

class DrvDbRedoxStackC(Base):
    '''
    Class method to create a DRVDB model of database RedoxStack table.
    '''
    __tablename__ = 'RedoxStack'
    __table_args__ = (ForeignKeyConstraint(['BatID'], ['Battery.BatID']),)

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True)
    ElectrodeSize = Column(MEDIUMINT(unsigned=True), nullable=False)
    ElectrodeComposition = Column(String(30), nullable=False)
    BipolarType = Column(Enum(*(DrvDbBipolarTypeE.get_all_values())), nullable=False)
    MembraneType = Column(Enum(*(DrvDbMembraneTypeE.get_all_values())), nullable=False)
    ElectrolyteType = Column(Enum(*(DrvDbElectrolyteTypeE.get_all_values())), nullable=False)

    # Battery = relationship('DrvDbBatteryC')

class DrvDbComputationalUnitC(Base):
    '''
    Class method to create a DRVDB model of database ComputationalUnit table.
    '''
    __tablename__ = 'ComputationalUnit'

    CUID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(50), nullable=False)
    IP = Column(String(20), nullable=False)
    Port = Column(SMALLINT(unsigned=True), nullable=False)
    User = Column(String(20), nullable=False)
    Pass = Column(String(100), nullable=False)
    LastConnection = Column(DateTime, nullable=False)
    Available = Column(Enum(*(DrvDbAvailableCuE.get_all_values())), nullable=False)

class DrvDbCyclerStationC(Base):
    '''
    Class method to create a DRVDB model of database CyclerStation table.
    '''
    __tablename__ = 'CyclerStation'
    __table_args__ = (ForeignKeyConstraint(['CUID'], ['ComputationalUnit.CUID']),)

    CSID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CUID = Column(ForeignKey('ComputationalUnit.CUID'), primary_key=True, \
                  nullable=False)
    Name = Column(String(30), nullable=False)
    Location = Column(String(30), nullable=False)
    RegisterDate = Column(DateTime, nullable=False)
    Deprecated = Column(BOOLEAN, nullable=False)

    ComputationalUnit = relationship('DrvDbComputationalUnitC')

class DrvDbCompatibleDeviceC(Base):
    '''
    Class method to create a DRVDB model of database CompatibleDevices table.
    '''
    __tablename__ = 'CompatibleDevices'

    CompDevID = Column(MEDIUMINT(unsigned=True), primary_key=True)
    Name = Column(String(30), nullable=False)
    Manufacturer = Column(String(30), nullable=False)
    DeviceType = Column(Enum(*DrvDbDeviceTypeE.get_all_values()), nullable=False)
    MinSWVersion = Column(SMALLINT(unsigned=True), nullable=False)
    VoltMin = Column(MEDIUMINT(unsigned=True))
    VoltMax = Column(MEDIUMINT(unsigned=True))
    CurrMin = Column(MEDIUMINT())
    CurrMax = Column(MEDIUMINT())

class DrvDbUsedDeviceC(Base):
    '''
    Class method to create a DRVDB model of database UsedDevices table.
    '''
    __tablename__ = 'UsedDevices'
    __table_args__ = (ForeignKeyConstraint(['CSID'], ['CyclerStation.CSID']),
                      ForeignKeyConstraint(['CompDevID'], ['CompatibleDevices.CompDevID']),)

    DevID = Column(MEDIUMINT(unsigned=True), primary_key=True, nullable=False)
    CSID = Column(ForeignKey('CyclerStation.CSID'), primary_key=True, nullable=False)
    CompDevID = Column(ForeignKey('CompatibleDevices.CompDevID'), nullable=False)
    SN = Column(String(30), nullable=False)
    UdevName = Column(String(30), nullable=False)

    CyclerStation = relationship('DrvDbCyclerStationC')
    CompatibleDevice = relationship('DrvDbCompatibleDeviceC')

class DrvDbLinkConfigurationC(Base):
    '''
    Class method to create a DRVDB model of database LinkConfiguration table.
    '''
    __tablename__ = 'LinkConfiguration'
    __table_args__ = (ForeignKeyConstraint(['CompDevID'], ['CompatibleDevices.CompDevID']),)

    CompDevID = Column(ForeignKey('CompatibleDevices.CompDevID'), nullable=False)
    Property = Column(String(30), nullable=False)
    Value = Column(String(30), nullable=False)

    CompatibleDevice = relationship('DrvDbCompatibleDeviceC')


class DrvDbMeasuresDeclarationC(Base):
    '''
    Class method to create a DRVDB model of database MeasuresDeclaration table.
    '''
    __tablename__ = 'MeasuresDeclaration'

    MeasType = Column(MEDIUMINT(unsigned=True), primary_key=True)
    MeasName = Column(String(20), nullable=False, unique=True)

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

class DrvDbInstructionC(Base):
    '''
    Class method to create a DRVDB model of database Instructions table.
    '''
    __tablename__ = 'Instructions'
    __table_args__ = (ForeignKeyConstraint(['ProfID'], ['Profile.ProfID']),)

    InstrID = Column(MEDIUMINT(), primary_key=True, nullable=False)
    ProfID = Column(ForeignKey('Profile.ProfID'), primary_key=True, nullable=False)
    Mode = Column(Enum(*(DrvDbCyclingModeE.get_all_values())), nullable=False)
    SetPoint = Column(MEDIUMINT(), nullable=False)
    LimitType = Column(Enum(*(DrvDbCyclingLimitE.get_all_values())), nullable=False)
    LimitPoint = Column(MEDIUMINT(), nullable=False)

    Profile = relationship('DrvDbProfileC')

class DrvDbMasterExperimentC(DrvDbBaseExperimentC):
    '''
    Class method to create a DRVDB model of database Experiment table.
    '''
    __tablename__ = 'Experiment'
    __table_args__ = (ForeignKeyConstraint(['CSID'], ['CyclerStation.CSID']),
                      ForeignKeyConstraint(['BatID'], ['Battery.BatID']),
                      ForeignKeyConstraint(['ProfID'],['Profile.ProfID']),
                    {'extend_existing': True},)

    CSID = Column(ForeignKey('CyclerStation.CSID'), nullable=False)
    BatID = Column(ForeignKey('Battery.BatID'), nullable=False)
    ProfID = Column(ForeignKey('Profile.ProfID'), nullable=False)

    # CyclerStation = relationship('DrvDbCyclerStationC')
    # Battery = relationship('DrvDbBatteryC')
    # Profile = relationship('DrvDbProfileC')

class DrvDbMasterGenericMeasureC(DrvDbBaseGenericMeasureC):
    '''
    Class method to create a model of cache database GenericMeasures table.
    '''
    __tablename__ = 'GenericMeasures'
    __table_args__ = {'extend_existing': True}

    InstrID = Column(ForeignKey('Instructions.InstrID'), nullable=False)
    # Instruction = relationship('DrvDbInstructionC')

class DrvDbMasterExtendedMeasureC(DrvDbBaseExtendedMeasureC):
    '''
    Class method to create a DRVDB model of database ExtendedMeasures table.
    '''
    __tablename__ = 'ExtendedMeasures'
    __table_args__ = {'extend_existing': True}

    MeasType = Column(ForeignKey('MeasuresDeclaration.MeasType'), \
                      primary_key=True, nullable=False)
    # Measure = relationship('DrvDbMeasuresDeclarationC')

class DrvDbMasterStatusC(DrvDbBaseStatusC):
    '''
    Class method to create a DRVDB model of database Status table.
    '''
    __tablename__ = 'Status'
    __table_args__ = (ForeignKeyConstraint(['DevID'], ['UsedDevices.DevID']),
                      {'extend_existing': True},)

    DevID = Column(ForeignKey('UsedDevices.DevID'), primary_key=True, nullable=False)
    # UsedDevice = relationship('DrvDbUsedDeviceC')

class DrvDbRedoxElectrolyteC(Base):
    '''
    Class method to create a DRVDB model of database RedoxElectrolyte table.
    '''
    __tablename__ = 'RedoxElectrolyte'
    __table_args__ = (ForeignKeyConstraint(['BatID'], ['Battery.BatID']),
                      ForeignKeyConstraint(['ExpID'], ['Experiment.ExpID']),)

    BatID = Column(ForeignKey('Battery.BatID'), primary_key=True, nullable=False)
    ExpID = Column(ForeignKey('Experiment.ExpID'), primary_key=True, nullable=False)
    ElectrolyteVol = Column(MEDIUMINT(unsigned=True), nullable=False)
    MaxFlowRate = Column(MEDIUMINT(unsigned=True), nullable=False)

    # Battery = relationship('DrvDbBatteryC')
    # Experiment = relationship('DrvDbMasterExperimentC')
