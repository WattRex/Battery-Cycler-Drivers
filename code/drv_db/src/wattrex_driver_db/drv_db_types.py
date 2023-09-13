#!/usr/bin/python3
'''
Enumerations defined to standardize names.
'''
#######################        MANDATORY IMPORTS         #######################

#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
from enum import Enum

#######################    SYSTEM ABSTRACTION IMPORTS    #######################

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################


#######################              ENUMS               #######################

### DB_TYPE ###
class DrvDbTypeE(Enum):
    '''Enum used to define database types.
    '''
    CACHE_DB = 'mysql'
    MASTER_DB = 'mysql'

### CYCLER ###
class DrvDbBatteryTechE(Enum):          # pylint: disable= too-many-ancestors
    '''Enum used to define battery technology types.
    '''
    LITHIUM = 'Lithium'
    LEADACID = 'LeadAcid'
    REDOXSTACK = 'RedoxStack'


class DrvDbLithiumChemistryE(Enum):     # pylint: disable= too-many-ancestors
    '''Enum used to define lithium battery chemistry.
    '''
    NMC = 'NMC'
    NCA = 'NCA'
    LMO = 'LMO'
    LFP = 'LFP'
    LCO = 'LCO'
    OTHER = 'Other'


class DrvDbLeadAcidChemistryE(Enum):    # pylint: disable= too-many-ancestors
    '''Enum used to define leadacid battery chemistry.
    '''
    LIQUID = 'Liquid'
    GEL = 'GEL'
    OTHER = 'Other'


class DrvDbBipolarTypeE(Enum):          # pylint: disable= too-many-ancestors
    '''Enum used to define redox bipolar type.
    '''
    PAPYEX_MERSEN = 'Papyex Mersen'
    COMPOSITE_SCHUNK = 'Composite Schunk'
    GRAPHITE = 'Graphite'
    OTHER = 'Other'


class DrvDbMembraneTypeE(Enum):         # pylint: disable= too-many-ancestors
    '''Enum used to define redox membrane type.
    '''
    FUMASEP_ANIONIC = 'Fumasep-Anionic'
    FUMASEP_CATHIONIC = 'Fumasep-Cathionic'
    NAFION = 'Nafion'
    VANADION = 'Vanadion'
    PEEK = 'PEEK'
    OTHER = 'Other'


class DrvDbElectrolyteTypeE(Enum):      # pylint: disable= too-many-ancestors
    '''Enum used to define redox electrolyte type.
    '''
    ALL_VANADIUM = 'All-vanadium'
    ALL_IRON = 'All-iron'
    VANADIUM_BASED = 'Vanadium-based'
    IRON_BASED = 'Iron-based'
    OTHER = 'Other'


class DrvDbDeviceTypeE(Enum):           # pylint: disable= too-many-ancestors
    '''Enum used to define compatible device type.
    '''
    SOURCE = 'Source'
    BISOURCE = 'BiSource'
    LOAD = 'Load'
    METER = 'Meter'


class DrvDbEquipStatusE(Enum):          # pylint: disable= too-many-ancestors
    '''Enum used to define equipment working status.
    '''
    COMM_ERROR = 'COMM_ERROR'
    OK = 'OK'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


class DrvDbAvailableCuE(Enum):          # pylint: disable= too-many-ancestors
    '''Enum used to define computational unit available status.
    '''
    ON = 'ON'
    OFF = 'OFF'


class DrvDbExpStatusE(Enum):            # pylint: disable= too-many-ancestors
    '''Enum used to define experiment status types.
    '''
    ERROR = 'ERROR'
    FINISHED = 'FINISHED'
    PAUSED = 'PAUSED'
    RUNNING = 'RUNNING'
    QUEUED = 'QUEUED'

class DrvDbCyclingModeE(Enum):          # pylint: disable= too-many-ancestors
    '''Enum used to define cycling control modes.
    '''
    WAIT = 'WAIT'
    CC = 'CC'
    CV = 'CV'
    CP = 'CP'


class DrvDbCyclingLimitE(Enum):         # pylint: disable= too-many-ancestors
    '''Enum used to define cycling limits.
    '''
    TIME = 'TIME'
    VOLTAGE = 'VOLTAGE'
    CURRENT = 'CURRENT'
    POWER = 'POWER'


#######################             CLASSES              #######################


#######################            FUNCTIONS             #######################
