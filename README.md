# EasyLogging
- No painful to use  :)

- User Guide

  - It will also show logger in console and save file in BaseLog.log 

  

Simple example
```python
from easy_logging.easylogging import EasyLogging

mylogger = EasyLogging().get_class_logger()

mylogger.debug('debug')
mylogger.info('info')
mylogger.warning('warning')
mylogger.error('error')
mylogger.critical('critical')

```

Another example
```python
from easy_logging.easylogging import EasyLogging

ELobj = EasyLogging()
ELobj.set_class_logger_level('WARNING')  # set level
ELobj.set_class_logger_file_dir('D:/')  # set dir
ELobj.set_class_logger_file_name('mylog.log')  # set log name
ELobj.set_class_logger_file_size(1024*1024*30)  # set log size
ELobj.set_class_logger_file_bkupcnt(512)  # set backup count

mylogger = ELobj.get_class_logger()  # get logger

# use it
mylogger.debug('debug')
mylogger.info('info')
mylogger.warning('warning')
mylogger.error('error')
mylogger.critical('critical')
```