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
from drv_db.src.wattrex_driver_db import DrvDbSqlEngineC, DrvDbTypeE, DrvDbMasterExperimentC, \
    DrvDbMasterGenericMeasureC, DrvDbMasterStatusC, DrvDbMasterExtendedMeasureC,\
    DrvDbAlarmC, DrvDbBatteryC

#######################              ENUMS               #######################

#######################             CLASSES              #######################

def test_read() -> None:
    """Runs the test read command from master database.
    """
    drv = DrvDbSqlEngineC(db_type=DrvDbTypeE.MASTER_DB,
                          config_file='code/drv_db/tests/.cred_master.yaml')

    stmt = select(DrvDbBatteryC)
    result = drv.session.execute(stmt).one()
    row: DrvDbBatteryC = result[0]
    print(row.__dict__)

    stmt = select(DrvDbMasterExperimentC)
    result = drv.session.execute(stmt).all()
    row: DrvDbMasterExperimentC = result[0][0]
    print(row.__dict__)

    stmt = select(DrvDbMasterGenericMeasureC)
    result = drv.session.execute(stmt).all()
    row : DrvDbMasterGenericMeasureC = result[0][0]
    print(row.__dict__)

    stmt = select(DrvDbAlarmC)
    result = drv.session.execute(stmt).all()
    row : DrvDbAlarmC = result[0][0]
    print(row.__dict__)

    stmt = select(DrvDbMasterStatusC)
    result = drv.session.execute(stmt).all()
    row : DrvDbMasterStatusC = result[0][0]
    print(row.__dict__)


    stmt = select(DrvDbMasterExtendedMeasureC)
    result = drv.session.execute(stmt).all()
    row : DrvDbMasterExtendedMeasureC = result[0][0]
    print(row.__dict__)

if __name__ == '__main__':
    test_read()
