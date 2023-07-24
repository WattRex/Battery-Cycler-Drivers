# README

- ```__init.py__``` has to be edited to work properly in your project.
- Change the variable name where the main logger is declared.

# Logging template

## Code to paste on top after imports of the main.py file

```
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)
```

## Code to paste on top after imports of every .py file

```
from sys_abs.sys_log import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from sys_abs.sys_log import SysLogLoggerC
    cycler_logger = SysLogLoggerC('./sys_abs/sys_log/logginConfig.conf')
log = sys_log_logger_get_module_logger(__name__)
```

# Complete the ```log_config.yaml``` file (or whatever name you gave it)

- You can place this file where you want but you have to specify its path and name when sys_log_logger_get_module_logger function is used.
- If the file ```log_config.yaml``` is empty, all loggers created on your modules will be defined at error level by default.
- To assign an specific logging level to a module, you have to write its name in this file and set the desired logging level like the following example.
- There is a template of the file in ```template_log_config.yaml```
