#!/usr/bin/python3
'''
Example of use of drv flow.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from time import sleep
from os import path
from signal import signal, SIGINT

#######################       THIRD PARTY IMPORTS        #######################
from enum import Enum

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
#from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
#if __name__ == '__main__':
#    cycler_logger = SysLogLoggerC()
#log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
# import time
import csv

from drv_flow import DrvFlowDeviceC

end_condition = False

def signal_handler(sig, frame):
    print("Finishing...")
    global end_condition
    end_condition = True

def main():
    drv = DrvFlowDeviceC ()
    data = {
        "flow_p": [],
        "flow_n": []
    }        

    signal(SIGINT, signal_handler)

    # Open file for writing data
    file = open('data.csv', 'w')
    writer = csv.writer(file)

    # Write headers
    writer.writerow(list(data.keys()))

    # Start recording meas and save it periodically on csv
    iter = 0
    while not end_condition:
        iter += 1
        #print('Requesting measures...')
        measure = drv.get_meas()

        if measure is not None:
            data["flow_p"].append(measure.flow_p)
            data["flow_n"].append(measure.flow_n)

        sleep(0.5)


    # Save data on csv
    # Mix lists of dict to store on csv
    print("Saving data on csv...")
    csv_data= list(map(lambda x, y: [x, y], data["flow_p"], data["flow_n"]))
    print(csv_data)
    writer.writerows(csv_data)
    file.close()
    drv.close()

if __name__ == '__main__':
    main()