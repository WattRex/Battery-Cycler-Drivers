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

#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################
from .drv_db_dao_cache import (DrvDbCacheExperimentC, DrvDbCacheGenericMeasureC,
                            DrvDbCacheExtendedMeasureC, DrvDbCacheStatusC)
from .drv_db_dao_master import (DrvDbMasterExperimentC, DrvDbMasterGenericMeasureC,
                                DrvDbMasterExtendedMeasureC, DrvDbMasterStatusC)
#######################              ENUMS               #######################


#######################             Functions              #######################

def transform_experiment_db(source: DrvDbMasterExperimentC|DrvDbCacheExperimentC,
                            target: DrvDbMasterExperimentC|DrvDbCacheExperimentC) -> None:
    """Transform an experiment from cache DB to master DB and viceversa.
    """
    target.ExpID = source.ExpID #pylint: disable=invalid-name
    target.Name = source.Name #pylint: disable=invalid-name
    target.Description = source.Description #pylint: disable=invalid-name
    target.DateCreation = source.DateCreation #pylint: disable=invalid-name
    target.DateBegin = source.DateBegin #pylint: disable=invalid-name
    target.DateFinish = source.DateFinish #pylint: disable=invalid-name
    target.Status = source.Status #pylint: disable=invalid-name
    target.BatID = source.BatID #pylint: disable=invalid-name
    target.CSID = source.CSID #pylint: disable=invalid-name
    target.ProfID = source.ProfID #pylint: disable=invalid-name

def transform_gen_meas_db(source: DrvDbCacheGenericMeasureC| DrvDbMasterGenericMeasureC,
                          target: DrvDbCacheGenericMeasureC| DrvDbMasterGenericMeasureC):
    """Transform a generic measurement from cache DB to master DB and viceversa.
    """
    target.Timestamp = source.Timestamp #pylint: disable=invalid-name
    target.InstrID = source.InstrID #pylint: disable=invalid-name
    target.ExpID = source.ExpID #pylint: disable=invalid-name
    target.MeasID = source.MeasID #pylint: disable=invalid-name
    target.Current = source.Current #pylint: disable=invalid-name
    target.Voltage = source.Voltage #pylint: disable=invalid-name
    target.Power = source.Power #pylint: disable=invalid-name
    target.PowerMode = source.PowerMode #pylint: disable=invalid-name

def transform_status_db(source: DrvDbCacheStatusC| DrvDbMasterStatusC,
                        target: DrvDbCacheStatusC| DrvDbMasterStatusC):
    """Transform a status from cache DB to master DB.
    """
    target.StatusID = source.StatusID #pylint: disable=invalid-name
    target.DevID = source.DevID #pylint: disable=invalid-name
    target.ExpID = source.ExpID #pylint: disable=invalid-name
    target.Status = source.Status #pylint: disable=invalid-name
    target.ErrorCode = source.ErrorCode #pylint: disable=invalid-name
    target.Timestamp = source.Timestamp #pylint: disable=invalid-name

def transform_ext_meas_db(source: DrvDbMasterExtendedMeasureC| DrvDbCacheExtendedMeasureC,
                          target: DrvDbMasterExtendedMeasureC| DrvDbCacheExtendedMeasureC):
    """Transform an extended measurement from cache DB to master DB.
    """
    target.UsedMeasID = source.UsedMeasID #pylint: disable=invalid-name
    target.ExpID = source.ExpID #pylint: disable=invalid-name
    target.Value = source.Value #pylint: disable=invalid-name
    target.MeasID = source.MeasID #pylint: disable=invalid-name
