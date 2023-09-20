#!/usr/bin/python3
'''
Example of use of drv flow.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
from time import sleep, time
import csv
from datetime import datetime
from signal import signal, SIGINT

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
#from system_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger
#if __name__ == '__main__':
#    cycler_logger = SysLogLoggerC()
#log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################

#######################          MODULE IMPORTS          #######################
from .drv_flow import DrvFlowDeviceC
#######################              ENUMS               #######################

#######################             CLASSES              #######################

class DrvFlowWriter():
    """Class for flowmeter to a read data and write on csv.
    """
    def __init__(self, serial_port : str = '/dev/ttyACM0', data_file : str = 'data.csv') -> None:
        self.data = {
            "timestamp": [],
            "flow_p": [],
            "flow_n": []
        }
        self.drv = DrvFlowDeviceC (serial_port= serial_port)
        self.file = open(data_file, 'w', encoding= 'utf-8') #pylint: disable=consider-using-with
        self.csv_writer = csv.writer(self.file)
        self.end_condition = False

        # Write headers
        self.csv_writer.writerow(list(self.data.keys()))
        #csv_writer.writerow(list(self.data.keys()))

        signal(SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame): #pylint: disable=unused-argument
        """Handle signal handler.
        """
        print("Finishing...")
        self.end_condition = True

    def run(self) -> None:
        """AI is creating summary for run
        """
        # Start recording meas and save it periodically on csv
        time_ini = time()
        time_save = 10
        while not self.end_condition:
            print('Requesting measures...')
            measure = self.drv.get_meas()

            if measure is not None:
                timestamp = datetime.now()
                self.data["timestamp"].append(timestamp.strftime("%m/%d/%y %H:%M:%S"))
                self.data["flow_p"].append(measure.flow_p)
                self.data["flow_n"].append(measure.flow_n)

            if time() - time_ini > time_save:
                self.write_csv()
                time_ini = time()
            sleep(1)

        self.close()

    def write_csv(self) -> None:
        """Write data to csv file .
        """
        print("Saving data on csv...")
        csv_data= list(map(lambda x, y, z: [x, y, z],\
                self.data["timestamp"], self.data["flow_p"], self.data["flow_n"]))
        print(csv_data)
        self.csv_writer.writerows(csv_data)
        self.file.flush()
        self.data['timestamp'].clear()
        self.data['flow_n'].clear()
        self.data['flow_p'].clear()

    def close(self) -> None:
        """Close the system and the file .
        """
        print("Closing system")
        self.write_csv()
        self.file.close()
        self.drv.close()
