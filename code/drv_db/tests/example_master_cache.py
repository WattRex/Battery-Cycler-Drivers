#!/usr/bin/python3
#pylint: disable= duplicate-code
'''
Enumerations defined to standardize names.
'''
#######################        MANDATORY IMPORTS         #######################
import sys
import os
#######################         GENERIC IMPORTS          #######################

#######################       THIRD PARTY IMPORTS        #######################
from sqlalchemy import select
#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from system_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC(file_log_levels="code/log_config.yaml")
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/')
from drv_db.src.wattrex_driver_db import (DrvDbSqlEngineC, DrvDbTypeE, DrvDbCacheExperimentC,
    DrvDbCacheGenericMeasureC, DrvDbCacheExtendedMeasureC, DrvDbMasterExperimentC,
    DrvDbCacheStatusC, DrvDbMasterGenericMeasureC, DrvDbMasterExtendedMeasureC, DrvDbMasterStatusC)

#######################              ENUMS               #######################

#######################             CLASSES              #######################

def test_read() -> None:
    """Runs a test to read from cache and write on master
    """
    drv_cache = DrvDbSqlEngineC(db_type=DrvDbTypeE.CACHE_DB,
                          config_file='code/drv_db/tests/.cred_cache.yaml')
    drv_master = DrvDbSqlEngineC(db_type=DrvDbTypeE.MASTER_DB,
                          config_file='code/drv_db/tests/.cred_master.yaml')

    stmt = select(DrvDbCacheExperimentC)
    result = drv_cache.session.execute(stmt).all()
    cache_row: DrvDbCacheExperimentC = result[0][0]
    print(cache_row.__dict__)
    master_row = DrvDbMasterExperimentC()
    master_row.transform(cache_row)
    drv_master.session.add(master_row)
    drv_master.session.commit()

    stmt = select(DrvDbCacheGenericMeasureC)
    result = drv_cache.session.execute(stmt).all()
    cache_row : DrvDbCacheGenericMeasureC = result[0][0]
    print(cache_row.__dict__)
    master_row = DrvDbMasterGenericMeasureC()
    master_row.transform(cache_row)
    drv_master.session.add(master_row)
    drv_master.session.commit()

    stmt = select(DrvDbCacheStatusC)
    result = drv_cache.session.execute(stmt).all()
    cache_row : DrvDbCacheStatusC = result[0][0]
    print(cache_row.__dict__)
    master_row = DrvDbMasterStatusC()
    master_row.transform(cache_row)
    drv_master.session.add(master_row)
    drv_master.session.commit()


    stmt = select(DrvDbCacheExtendedMeasureC)
    result = drv_cache.session.execute(stmt).all()
    cache_row : DrvDbCacheExtendedMeasureC = result[0][0]
    print(cache_row.__dict__)
    master_row = DrvDbMasterExtendedMeasureC()
    master_row.transform(cache_row)
    drv_master.session.add(master_row)
    drv_master.session.commit()
    drv_cache.session.close()
    drv_master.session.close()

if __name__ == '__main__':
    test_read()
