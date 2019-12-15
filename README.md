# EasyLogging
- No painful to use  :)
- If your os is windows7/10, just click ***Quick Install.bat*** to install this module.
- You can alse install this package as follows in command window.

```
python setup.py install
```

- User Guide

  - It will show logger in console and save file in BaseLog.log or user specified path.
  - It can work in multi-process.
  - All config settings will be changed permanent.
  - Config file is centralized management, and visible in **para_config.json** and **path_config.json**.
  - Log configuration can be restored by deleting the  **para_config_local.json** and **path_config_local.json**.

  

- Simple example

```python
from easy_logging.easylogging import EasyLogging

# get logger
mylogger = EasyLogging().get_class_logger()

mylogger.debug('debug')
mylogger.info('info')
mylogger.warning('warning')
mylogger.error('error')
mylogger.critical('critical')
```
- Output to console with striking error

```python
from easy_logging.easylogging import BaseEasyLogging

# get logger
mylogger = BaseEasyLogging().get_logger('logger_console_red')

mylogger.debug('debug') # only sys.stdout
mylogger.info('info') # only sys.stdout
mylogger.warning('warning') # sys.stdout and sys.error
mylogger.error('error') # sys.stdout and sys.error
mylogger.critical('critical') # sys.stdout and sys.error

```

- Another example with private config

```python
from easy_logging.easylogging import EasyLogging

# create EL object
ELobj = EasyLogging()
ELobj.set_class_logger_level('WARNING')  # set level
ELobj.set_class_logger_file_dir('D:/')  # set dir
ELobj.set_class_logger_file_name('mylog.log')  # set log name
ELobj.set_class_logger_file_size(1024*1024*30)  # set log size
ELobj.set_class_logger_file_bkupcnt(512)  # set backup count

# get logger
mylogger = ELobj.get_class_logger()

# use it
mylogger.debug('debug')
mylogger.info('info')
mylogger.warning('warning')
mylogger.error('error')
mylogger.critical('critical')
```

- In this package， it also provide several different logger

```python
from easy_logging.easylogging import EasyLogging # root logger
from easy_logging.easylogging import EasyFileLogging  # only file
from easy_logging.easylogging import EasySimpleLogging # simple msg
from easy_logging.easylogging import EasyNormalLogging # normal msg
from easy_logging.easylogging import EasyParticularLogging # detail msg
from easy_logging.easylogging import EasyVerboseLogging # verbose msg
```




