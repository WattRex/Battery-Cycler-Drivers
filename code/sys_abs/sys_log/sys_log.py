#!/usr/bin/python3
"""
    This module works to have a logger instead of using prints,
    it will create a file to save all the messages
    with the hour and the module the message belongs to.
"""
#######################        MANDATORY IMPORTS         #######################
from pathlib import Path
import sys
import os

#######################      LOGGING CONFIGURATION       #######################


#######################         GENERIC IMPORTS          #######################
import logging
import logging.handlers
import logging.config
import configparser

#######################       THIRD PARTY IMPORTS        #######################

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
sys.path.append(os.getcwd())  #get absolute path
from sys_abs.sys_conf import sys_conf_read_config_params, SysConfSectionNotFoundErrorC

#######################          PROJECT IMPORTS         #######################


#######################              ENUMS               #######################


#######################             CLASSES              #######################
class SysLogLoggerC():
    """This function will be called after the system has been called .
    """
    def __init__(self, file_config_path:str) -> None:
        #Example: file_config_path = './myLogginConfig.conf'
        '''
        Initialize the main logger.
        It is necessaty to be used only once and before any other module is imported
        in the main file.

        Args:
            file_config_path (str): Path to the yaml file that containg the log configuration
        '''
        config_parser = configparser.ConfigParser()
        config_parser.read(file_config_path)
        if 'handler_rotatingFileHandler' in config_parser and 'args' \
            in config_parser['handler_rotatingFileHandler']:   # Check if the logConfigFile
            log_folder = self.__parse_log_folder(config_parser)
            Path(log_folder).mkdir(parents = True, exist_ok = True)
        logging.config.fileConfig(file_config_path,disable_existing_loggers=True)
        #, encoding='utf-8'
        for han in logging.getLogger().handlers:
            if isinstance(han, logging.handlers.RotatingFileHandler):
                han.doRollover()
        logging.debug('First log message')

    def __parse_log_folder(self, config_parser) -> str:
        '''
        This function will transform a string retrieved from
        config_parser['handler_rotatingFileHandler']['args'] like
        "('./log_mqtt_client/logging_rotatingfile_example.log', 'w', 1000000, 20)"
            into
        "./log_mqtt_client"
        '''
        log_folder_list = config_parser['handler_rotatingFileHandler']\
            ['args'].split(",", 1)[0][2:-1].split("/")
        log_folder = ""
        for aux in range(len(log_folder_list)-1):
            log_folder += log_folder_list[aux] + "/"
        return log_folder[:-1]


class SysLogCustomFormatterC(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;5;253m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    #bold_red = '\x1b[31;1m'
    bold_red = '\x1b[1;37;41m'
    reset = '\x1b[0m'

    def __init__(self, fmt: str or None = ..., datefmt: str or None = ..., style = ...) -> None:
        """Initialize the custom format logger .

        Args:
            fmt (strorNone, optional): String used to format the log message.
            datefmt (strorNone, optional): Format used to print the datetime.
            style ([type], optional): Style used to print the log message.
        """
        super().__init__(fmt, datefmt, style)
        self.fmt = fmt
        self.formats = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record) -> str:
        '''
        Format log record.

        Args:
            record ([type]): Logger record to be formatted.

        Returns:
            [type]: return the record formatted.
        '''
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


#######################            FUNCTIONS             #######################
def sys_log_logger_get_module_logger(name : str,
            config_by_module_filename : str = './log_config.yaml') -> logging.Logger:
    '''
    Configures the logger for the given module name and assigns custom logging level defined
    in a .yaml file.

    Args:
        name (str): __name__ E.g. MID.MID_DABS.MID_DABS_Node
        config_by_module_filename (str, optional): Path to the yaml file
        that contains the log configuration by module. Defaults to './log_config.yaml'.

    Returns:
        log (Logger): Return the log to be used in a specific module file
    '''
    log = logging.getLogger(name)
    try:
        if name != '__main__': #Main script is not named (__name__) like the other scripts
            name_list = name.split('.')
            name = ''
            if len(name_list) > 1:
                # Convert name to module name. Ex: APP.APP_DIAG.APP_DIAG_String -> APP.APP_DIAG
                name = '.'.join(name_list[:-1])
            else:
                # For test file. Ex: Test_APP_DIAG
                name = name_list[0]
        custom_level = sys_conf_read_config_params(
            filename = config_by_module_filename, section = name)
        log.setLevel(str(custom_level))
        log.debug(f"log level of {name} has been set to {custom_level}")

        # Assign the file handler to the logger
        # if the module name is found in the file_handlers section
        file_handlers = sys_conf_read_config_params(
            filename = config_by_module_filename, section = 'file_handlers')
        for key in file_handlers:
            for module_name in file_handlers[key]:
                # log.critical(f"module_name: {module_name}")
                if name == module_name:
                    file_handler = logging.FileHandler(filename = "./log/" +\
                                        key + ".log", mode = 'w+', encoding = 'utf-8')
                    config_parser = configparser.ConfigParser()
                    config_parser.read("./SYS/SYS_LOG/logginConfig.conf")
                    # if 'formatter_plain' in config_parser and
                    # 'format' in config_parser['handler_rotatingFileHandler']:
                    file_handler.setFormatter(logging.Formatter(fmt = \
                                        config_parser.items('formatter_plain', True)[0][1]))
                    file_handler.setLevel("DEBUG")
                    log.addHandler(file_handler)
                    log.debug(f"Added handler for {module_name} ({key} file)")
        # Custom logging level set in .yaml file will be applied

    except SysConfSectionNotFoundErrorC as exception:
        #Default logging level set in config will be applied
        log.warning(f"{exception}")
        # log.warning(f"Module {name} not found in the log level
        # configuration by module file\n{exception.__str__()}")
    except Exception as exception:
        log.error(f"{exception}")
    return log
