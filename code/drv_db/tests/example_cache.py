#!/usr/bin/python3
'''
Enumerations defined to standardize names.
'''
#######################        MANDATORY IMPORTS         #######################
import sys
import os
#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
from sqlalchemy import select, Row
#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC(file_log_levels="code/drv_db/tests/log_config.yaml")
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/')
from drv_db.src.wattrex_driver_db.drv_db_engine import DrvDbSqlEngineC
from drv_db.src.wattrex_driver_db.drv_db_types import DrvDbTypeE
from drv_db.src.wattrex_driver_db.drv_db_dao_cache import DrvDbExperimentC,\
    DrvDbExpStatusE, DrvDbGenericMeasureC, DrvDbStatusC, DrvDbExtendedMeasureC
from drv_db.src.wattrex_driver_db.drv_db_dao_base import DrvDbAlarmC

#######################              ENUMS               #######################

#######################             CLASSES              #######################

def test_read() -> None:

    drv = DrvDbSqlEngineC(db_type=DrvDbTypeE.CACHE_DB, config_file='code/drv_db/tests/.cred.yaml')
    stmt = select(DrvDbExperimentC)
    result = drv.session.execute(stmt).all()
    row: DrvDbExperimentC = result[0][0]
    print(row.__dict__)

    stmt = select(DrvDbGenericMeasureC)
    result = drv.session.execute(stmt).all()
    row : DrvDbGenericMeasureC = result[0][0]
    print(row.__dict__)

    stmt = select(DrvDbAlarmC)
    result = drv.session.execute(stmt).all()
    row : DrvDbAlarmC = result[0][0]
    print(row.__dict__)

    stmt = select(DrvDbStatusC)
    result = drv.session.execute(stmt).all()
    row : DrvDbStatusC = result[0][0]
    print(row.__dict__)


    stmt = select(DrvDbExtendedMeasureC)
    result = drv.session.execute(stmt).all()
    row : DrvDbExtendedMeasureC = result[0][0]
    print(row.__dict__)

if __name__ == '__main__':
    test_read()