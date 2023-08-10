#!/usr/bin/python3
'''
Enumerations defined to standardize names.
'''
#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
from sqlalchemy import Enum

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC()
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################


#######################              ENUMS               #######################

### CYCLER ###
class DrvDbBatteryTechE(Enum):
    '''Enum used to define battery technology types.
    '''
    LITHIUM = 'Lithium'
    LEADACID = 'LeadAcid'
    REDOXSTACK = 'RedoxStack'


class DrvDbLithiumChemistryE(Enum):
    '''Enum used to define lithium battery chemistry.
    '''
    NMC = 'NMC'
    NCA = 'NCA'
    LMO = 'LMO'
    LFP = 'LFP'
    LCO = 'LCO'
    OTHER = 'Other'


class DrvDbLeadAcidChemistryE(Enum):
    '''Enum used to define leadacid battery chemistry.
    '''
    LIQUID = 'Liquid'
    GEL = 'GEL'
    OTHER = 'Other'


class DrvDbBipolarTypeE(Enum):
    '''Enum used to define redox bipolar type.
    '''
    PAPYEX_MERSEN = 'Papyex Mersen'
    COMPOSITE_SCHUNK = 'Composite Schunk'
    GRAPHITE = 'Graphite'
    OTHER = 'Other'


class DrvDbMembraneTypeE(Enum):
    '''Enum used to define redox membrane type.
    '''
    FUMASEP_ANIONIC = 'Fumasep-Anionic'
    FUMASEP_CATHIONIC = 'Fumasep-Cathionic'
    NAFION = 'Nafion'
    VANADION = 'Vanadion'
    PEEK = 'PEEK'
    OTHER = 'Other'


class DrvDbElectrolyteTypeE(Enum):
    '''Enum used to define redox electrolyte type.
    '''
    ALL_VANADIUM = 'All-vanadium'
    ALL_IRON = 'All-iron'
    VANADIUM_BASED = 'Vanadium-based'
    IRON_BASED = 'Iron-based'
    OTHER = 'Other'


class DrvDbDeviceTypeE(Enum):
    '''Enum used to define compatible device type.
    '''
    SOURCE = 'Source'
    BISOURCE = 'BiSource'
    LOAD = 'Load'
    METER = 'Meter'


class DrvDbEquipStatusE(Enum):
    '''Enum used to define equipment working status.
    '''
    COMM_ERROR = 'COMM_ERROR'
    OK = 'OK'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


class DrvDbAvailableCuE(Enum):
    '''Enum used to define computational unit available status.
    '''
    ON = 'ON'
    OFF = 'OFF'


class DrvDbExpStatusE(Enum):
    '''Enum used to define experiment status types.
    '''
    ERROR = 'ERROR'
    FINISHED = 'FINISHED'
    PAUSED = 'PAUSED'
    RUNNING = 'RUNNING'
    QUEUED = 'QUEUED'


class DrvDbCyclingModeE(Enum):
    '''Enum used to define cycling control modes.
    '''
    WAIT = 'WAIT'
    CC = 'CC'
    CV = 'CV'
    CP = 'CP'


class DrvDbCyclingLimitE(Enum):
    '''Enum used to define cycling limits.
    '''
    TIME = 'TIME'
    VOLTAGE = 'VOLTAGE'
    CURRENT = 'CURRENT'
    POWER = 'POWER'


#######################             CLASSES              #######################


#######################            FUNCTIONS             #######################
