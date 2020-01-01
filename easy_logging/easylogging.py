#!/usr/bin/env python
# """
# this module need concurrent_log_handler
# please do: pip install concurrent_log_handler
# core file
# 1 logging.py
# 2 para_config.json
# 3 path_config.json
# """
import os
import copy
import json
import datetime
import abc
from pathlib import Path

import logging
import logging.config

from numbers import Integral


class ABClassEasyLogging(abc.ABC):

    @abc.abstractmethod
    def get_config_dict(self):
        pass

    @abc.abstractmethod
    def get_logger(self):
        pass


class BaseEasyLogging(ABClassEasyLogging):

    log_para_config_json_name = 'para_config.json'  # logging config parameters file name
    log_path_config_json_name = 'path_config.json'  # logging output parameters file name

    log_para_config_local_json_name = 'para_config_local.json'  # local logging config parameters file name
    log_path_config_local_json_name = 'path_config_local.json'  # local logging output parameters file name

    abnormal_info_output_file = 'AbnormalLogConfigInfo.txt'  # abnormal info output file name 

    def __init__(self):
        self.log_para_config_json_name = BaseEasyLogging.log_para_config_json_name  # load file name
        self.log_path_config_json_name = BaseEasyLogging.log_path_config_json_name  # load file name
        self.code_file_dir = Path(os.path.dirname(__file__))  # current .py file dir
        # self.log_para_config_json_name ans self.log_path_config_json_name
        # will change in func self._set_load_json_name()
        self._set_load_json_name()  # set json file name
        self.abnormal_info_output_file = BaseEasyLogging.abnormal_info_output_file  # set abnormal file name
        self.para_dict = {}
        self.path_dict = {}
        self.config_dict = {}  # core logger config dict, will change in func get_config_dict()
        self.para_config_exist = None  # will change in func _check_config_json_exist
        self.path_config_exist = None  # will change in func _check_config_json_exist
        self._check_config_json_exist()
        self.para_config_load_success = False  # will change in func _load_json_dict()
        self.path_config_load_success = False  # will change in func _load_json_dict()
        self._load_json_dict()  # load mix json dict
        self.mix_para_path_success = False  # will change in func mix_para_path_dict()
        self._load_default_or_not = False
        self._mix_para_path_dict()  # mix config_dict with path_dict
        self.get_config_dict()  # load config dict

    def _set_load_json_name(self):
        if os.path.exists(
                f'{self.code_file_dir}/{BaseEasyLogging.log_para_config_local_json_name}'):
            self.log_para_config_json_name = BaseEasyLogging.log_para_config_local_json_name
        if os.path.exists(
                f'{self.code_file_dir}/{BaseEasyLogging.log_path_config_local_json_name}'):
            self.log_path_config_json_name = BaseEasyLogging.log_path_config_local_json_name

    def _load_json_dict(self):
        if self.para_config_exist:
            with open(self.para_config_json_path, 'r', encoding='utf-8') as para_config:
                try:
                    self.para_dict = json.load(para_config)
                    self.para_config_load_success = True
                except json.decoder.JSONDecodeError as error_info:
                    self.abnormal_info_output(f'para_config_json_path with error encoding,'
                                              f'please check json format.'
                                              f'error_info={error_info}')

        if self.para_config_load_success is True:
            if self.path_config_exist:
                with open(self.path_config_json_path, 'r', encoding='utf-8') as path_config:
                    try:
                        self.path_dict = json.load(path_config)
                        self.path_config_load_success = True
                    except json.decoder.JSONDecodeError as error_info:
                        self.abnormal_info_output(f'path_config_json_path with error encoding, '
                                                  f'please check json format. '
                                                  f'error_info={error_info}')
        return None

    def _mix_para_path_dict(self):
        if self.para_config_load_success:
            if self.path_config_load_success:
                # try mix
                for file_handler_key in self.path_dict.keys():
                    if file_handler_key in self.para_dict['handlers'].keys():
                        if 'filename' in self.para_dict['handlers'][file_handler_key]:
                            # original output path
                            raw_log_file_path = (
                                self.para_dict['handlers'][file_handler_key]['filename'])
                            # target output path
                            log_file_dir = self.path_dict[file_handler_key]
                            # get original output file name
                            (folder, file_name) = os.path.split(raw_log_file_path)
                            # mix the path
                            log_file_path = os.path.join(log_file_dir, file_name)
                            # overwrite and set the new output paht
                            self.para_dict['handlers'][file_handler_key]['filename'] = log_file_path
                        else:
                            abnormal_info = (f'Want to chang the output path of [handlers={file_handler_key}], '
                                             f'but this handler was not defined in para_config'
                                             f'please check [filename] key-value, and check the inner logical of json!')
                            self.abnormal_info_output(abnormal_info)
                    else:
                        abnormal_info = (f'Want to chang the output path of [handlers={file_handler_key}], '
                                         f'but this handler was not clearly defined, '
                                         f'please check the inner logical of json!')
                        self.abnormal_info_output(abnormal_info)
                self.mix_para_path_success = True
            else:
                # para_config.json is losing, so the para_dict and path_dict can not be mixed
                abnormal_info = f'Want to mix the path_dict and the para_dict, but load path_dict failed!'
                self.abnormal_info_output(abnormal_info)
                self.mix_para_path_success = True
        else:
            # load para_dict failed
            abnormal_info = f'load para_dict failed!'
            self.abnormal_info_output(abnormal_info)
        return None

    def get_config_dict(self):
        if self.mix_para_path_success:
            # load mixed config dict
            self.config_dict = copy.deepcopy(self.para_dict)
        else:
            # load default dict
            self.config_dict = self._load_default_dict()
            self.abnormal_info_output('load the default config dict')
        return None

    def get_logger(self, logger_name='root'):
        """
        according to logger_name get logger
        if logger_name was not given, than generate logger by root set
        if logger_name was given, than register corresponding logger
        if logger_name was given, but this name logger was not exist,
        than generate logger by root set, and it name will be changed as given name

        Parameters
        ----------
        logger_name : str

        Returns
        -------
        logger : logging.Logger
        """
        self._formalized_temp_logger(logger_name)
        logging.config.dictConfig(self.config_dict)
        self._export_to_local_json()  # if load config dict successfully then output the mix config dict as local
        easy_logger = logging.getLogger(logger_name)
        return easy_logger

    def _formalized_temp_logger(self, logger_name):
        if logger_name in self.get_loggers_list():
            self.check_folder_path(logger_name)
        else:
            root_logger_config_info = self.config_dict['loggers']['root']
            self.config_dict['loggers'][logger_name] = root_logger_config_info
            self.abnormal_info_output(f'given logger_name:{logger_name}, '
                                      f'was not exist in current logger list, '
                                      f'and it was auto added.')

    def _export_to_local_json(self):
        if self._load_default_or_not is True:
            # load default dict, so local json should not be output.
            return None

        output_para_dict_mirror = copy.deepcopy(self.config_dict)
        output_path_dict_mirror = {}
        for handler_key in output_para_dict_mirror['handlers'].keys():
            if 'filename' in output_para_dict_mirror['handlers'][handler_key]:
                log_path = output_para_dict_mirror['handlers'][handler_key]['filename']
                # get original json name
                (folder, file_name) = os.path.split(log_path)
                output_para_dict_mirror['handlers'][handler_key]['filename'] = file_name
                output_path_dict_mirror[handler_key] = folder
        with open(f'{self.code_file_dir}/'
                  f'{BaseEasyLogging.log_para_config_local_json_name}', 'w') as export_para_json:
            json.dump(output_para_dict_mirror, export_para_json)
        with open(f'{self.code_file_dir}/'
                  f'{BaseEasyLogging.log_path_config_local_json_name}', 'w') as export_path_json:
            json.dump(output_path_dict_mirror, export_path_json)
        return None

    def get_formatters_list(self) -> list:
        """
        Returns
        -------
        list(...) : list
        """
        return list(self.config_dict['formatters'].keys())

    def get_handlers_list(self) -> list:
        """
        Returns
        -------
        list(...) : list
        """
        return list(self.config_dict['handlers'].keys())

    def get_loggers_list(self) -> list:
        """
        Returns
        -------
        list(...) : list
        """
        return list(self.config_dict['loggers'].keys())

    def check_folder_path(self, logger_name: str):
        """
        According logger_name get it's handler and check the file dir exist or not.
        If the folder is not exist, this func will create the folder.

        Parameters
        ----------
        logger_name : str
        """
        handlers_list = self.config_dict['loggers'][logger_name]['handlers']
        for handle_key in self.config_dict['handlers'].keys():
            if handle_key in handlers_list:
                if 'filename' in self.config_dict['handlers'][handle_key]:
                    folder_path = os.path.dirname(
                        self.config_dict['handlers'][handle_key]['filename'])
                    if len(folder_path) > 0:
                        if os.path.exists(folder_path):
                            pass
                        else:
                            os.makedirs(folder_path)
                            abnormal_info = (f'The output folder was not exist, '
                                             f'so it was created automatically:{folder_path}')
                            self.abnormal_info_output(abnormal_info)
        return None

    def _load_default_dict(self):
        """
        for some reason, load the default config dict
        """
        default_config_dict = {
            'version': 1,
            'disable_existing_loggers': True,
            'incremental': False,
            'formatters': {
                'default_msg': {
                    'class': 'logging.Formatter',
                    'format': '[TIME:%(asctime)s][LEVEL:%(levelname)s][TID:%(thread)d]'
                              '[PID:%(process)d][NAME:%(name)s]'
                              '[FUNCTION:%(funcName)s][MESSAGE:%(message)s]',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'default_msg'
                },
                'file': {
                    'level': 'DEBUG',
                    'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
                    'formatter': 'default_msg',
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 32,
                    'delay': True,
                    'filename': 'DefaultLog.log',
                    'encoding': 'utf8'
                }
            },
            'loggers': {
                'root': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG',
                    'propagate': False
                }
            }
        }
        self._load_default_or_not = True
        return default_config_dict

    def abnormal_info_output(self, info_text):
        """
        when error or abnormal case happen, than output *.txt to current execute local path
        """
        with open(f'./{self.abnormal_info_output_file}', 'a', encoding='utf-8') as addition_info:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            addition_info_text = f'[TIME:{current_time}][LOGGING CONFIG ABNORMAL INFO:{info_text}]'
            print(addition_info_text)
            addition_info.write(addition_info_text + '\n')
        return None

    def _check_config_json_exist(self):
        """
        check json config file exist or nor
        """
        self._check_para_json_exist()
        self._check_path_json_exist()
        if self.para_config_exist is None:
            raise RuntimeError('self.para_config_exist should not be None, '
                               'please execute self._check_para_json_exist()')
        if self.path_config_exist is None:
            raise RuntimeError('self.path_config_exist should not be None, '
                               'please execute self._check_path_json_exist()')
        return None

    def _check_para_json_exist(self):
        """
        check para_config.json existence
        """
        if os.path.exists(self.para_config_json_path):
            self.para_config_exist = True
        else:
            self.para_config_exist = False
            error_info = f'{self.para_config_json_path} file lose.'
            self.abnormal_info_output(info_text=error_info)
        return None

    def _check_path_json_exist(self):
        """
        check log_path_config.json existence
        """
        if os.path.exists(self.path_config_json_path):
            self.path_config_exist = True
        else:
            self.path_config_exist = False
            error_info = f'{self.path_config_json_path} file lose.'
            self.abnormal_info_output(info_text=error_info)
        return None

    @property
    def para_config_json_path(self):
        path = f'{self.code_file_dir}/{self.log_para_config_json_name}'
        return path

    @property
    def path_config_json_path(self):
        path = f'{self.code_file_dir}/{self.log_path_config_json_name}'
        return path

    def show_formatters_list(self):
        for formatter_name in self.get_formatters_list():
            print(formatter_name)
        return None

    def show_loggers_list(self):
        for logger_name in self.get_loggers_list():
            print(logger_name)
        return None

    def show_handlers_list(self):
        for handler_name in self.get_handlers_list():
            print(handler_name)
        return None

    def show_logger_handlers(self, logger_name=None):
        """
        show the logger_name's handlers
        """
        if logger_name is None:
            print('logger_name should be assigned')
            return None

        if logger_name in self.config_dict['loggers'].keys():
            for handler in self.config_dict['loggers'][logger_name]['handlers']:
                print(handler)
        else:
            error_text = logger_name + ' was not defined'
            self.abnormal_info_output(error_text)
        return None

    def show_handler_info(self, handler_name=None):
        """
        show the config info of given handler_name
        """
        if handler_name is None:
            print('handler_name should be assigned')
            return None

        if handler_name in self.config_dict['handlers'].keys():
            for info_key in self.config_dict['handlers'][handler_name]:
                value = self.config_dict['handlers'][handler_name][info_key]
                print(f'{info_key:15}: {value}')
        else:
            error_text = handler_name + ' was not defined'
            self.abnormal_info_output(error_text)
        return None

    def show_formatter_info(self, format_name=None):
        """
        show the config info of given format_name
        """
        if format_name is None:
            print('format_name should be assigned')
            return None

        if format_name in self.config_dict['formatters'].keys():
            for info_key in self.config_dict['formatters'][format_name]:
                value = self.config_dict['formatters'][format_name][info_key]
                print(f'{info_key:15}: {value}')
        else:
            error_text = format_name + ' was not defined'
            self.abnormal_info_output(error_text)
        return None

    @staticmethod
    def show_help():
        help_text = (
            ">> formatters:  format1:  |-class    format2: |-class\n"
            "                          |-format            |-format\n"
            "                          |-datefmt           |-datefmt\n"
            "------------------------------------------------------------------------------------\n"
            ">> handlers:    handler1: |-level    handler2:|-level\n"
            "                          |-class             |-class\n"
            "                          |-formatter         |-formatter  <---should in formatters\n"
            "------------------------------------------------------------------------------------\n"
            ">> loggers:     logger1:  |-handlers logger2: |-handlers   <---should in handlers\n"
            "                          |                   |            ^---and should be list\n"
            "                          |-level             |-level\n")
        print(help_text)
        return None

    def _set_logger_handlers(self, logger, handlers_list):
        if isinstance(handlers_list, list):
            pass
        else:
            print(f'given handlers_list should be list')
            return None

        additional_info = ''
        operate_successful_flag = False
        if isinstance(self.config_dict, dict):
            if 'loggers' in self.config_dict.keys():
                if logger in self.config_dict['loggers']:
                    self.config_dict['loggers'][logger]['handlers'] = handlers_list
                    operate_successful_flag = True
                else:
                    additional_info = additional_info + f'{logger} was not exist in  loggers key-value;'
            else:
                additional_info = additional_info + f'loggers was not exist config_dict key-value;'
        else:
            additional_info = additional_info + f'config_dict type error, it should be dict;'

        if operate_successful_flag:
            self.abnormal_info_output(f'add handlers in {logger} success, '
                                      f'handlers_list:{handlers_list}')
        else:
            self.abnormal_info_output(f'_set_logger_handlers(logger={logger} operate failed,'
                                      f'handlers_list={handlers_list}),'
                                      f'error reason:{additional_info}')
        return None

    def _set_logger_level(self, logger, level):
        if isinstance(level, str):
            if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                pass
            else:
                print(f'given value of level should be DEBUG,INFO,WARNING,ERROR,CRITICAL')
                return None
        else:
            print(f'given type of level should be str')
            return None

        additional_info = ''
        operate_successful_flag = False
        if isinstance(self.config_dict, dict):
            if 'loggers' in self.config_dict.keys():
                if logger in self.config_dict['loggers']:
                    self.config_dict['loggers'][logger]['level'] = level
                    operate_successful_flag = True
                else:
                    additional_info = additional_info + f'{logger} was not exist in  loggers key-value;'
            else:
                additional_info = additional_info + f'loggers was not exist in  config_dict key-value;'
        else:
            additional_info = additional_info + f'config_dict type error, it should be dict;'

        if operate_successful_flag:
            self.abnormal_info_output(f'set {logger} level success,'
                                      f'now level is: {level}')
        else:
            self.abnormal_info_output(f'_set_logger_level(logger={logger},'
                                      f'level={level}) operate failed,'
                                      f'error reason:{additional_info}')

    def _set_handle_detail(self, handler, key, value):
        additional_info = ''
        operate_successful_flag = False
        if isinstance(self.config_dict, dict):
            if 'handlers' in self.config_dict.keys():
                if handler in self.config_dict['handlers']:
                    self.config_dict['handlers'][handler].update({key: value})
                    operate_successful_flag = True
                else:
                    additional_info = additional_info + f'{handler} was not exist in  handlers key-value;'
            else:
                additional_info = additional_info + f'handlers was not exist in  config_dict key-value;'
        else:
            additional_info = additional_info + f'config_dict type error, it should be dict;'

        if operate_successful_flag:
            self.abnormal_info_output(f'_set_handle_detail(handler={handler}, '
                                      f'key={key},value={value}) operate success')
        else:
            self.abnormal_info_output(f'_set_handle_detail(handler={handler}, '
                                      f'key={key},value={value}) operate failed,'
                                      f'error reason:{additional_info}')

    def add_formatter(self, format_dict=None):
        """
        add formatter

        Examples
        ----------
        from easy_logging.easylogging import BaseEasyLogging
        format_dict = {'some_format':{'class':'logging.Formatter','format':'%(message)s'}}
        logger_set = BaseEasyLogging().add_formatter(format_dict)
        """
        if format_dict is None:
            print(f'please input format_dict')
            return None

        if isinstance(format_dict, dict):
            pass
        else:
            self.abnormal_info_output(f'given format_dict:{format_dict} should be dict')
            return None

        check_successful_flag = True
        additional_info = ''
        for format_name in format_dict.keys():
            for each_key in ['class', 'format']:
                if each_key in format_dict[format_name].keys():
                    pass
                else:
                    additional_info = additional_info + f'given {format_name} lose {each_key} key-value;'
                    check_successful_flag = False

        if check_successful_flag:
            self.config_dict['formatters'].update(format_dict)
            self.abnormal_info_output(f'add formatters:{format_dict} success')
        else:
            self.abnormal_info_output(f'add formatters failed, error reason:{additional_info}')
        return None

    def add_handler(self, handler_dict=None):
        """
        add dict handler

        Examples
        ----------
        from easy_logging.easylogging import BaseEasyLogging
        handler_dict = {'some_handler':
                         {'level': 'DEBUG',
                          'class':'logging.StreamHandler',
                          'formatter':'msg'}
                      }
        logger_set = BaseEasyLogging().add_formatter(handler_dict)
        """

        if handler_dict is None:
            print(f'please input handler_dict')
            return None

        if isinstance(handler_dict, dict):
            pass
        else:
            self.abnormal_info_output(f'given handler_dict:{handler_dict} should be dict')
            return None

        check_successful_flag = True
        additional_info = ''
        for handler_name in handler_dict.keys():
            for each_key in ['class', 'formatter', 'level']:
                if each_key in handler_dict[handler_name].keys():
                    pass
                else:
                    additional_info = additional_info + f'given {handler_name} lose the {each_key} key-value;'
                    check_successful_flag = False

        if check_successful_flag:
            self.config_dict['handlers'].update(handler_dict)
            self.abnormal_info_output(f'add handlers:{handler_dict} success')
        else:
            self.abnormal_info_output(f'add handlers failed, error reason:{additional_info}')
        return None

    def add_logger(self, logger_dict=None):
        """
        add dict logger

        Examples
        ----------
        from easy_logging.easylogging import BaseEasyLogging
        logger_dict = {'some_logger':
                          {'handlers': ['handler1','handler2'],
                           'level':'DEBUG',
                           'propagate': False}
                     }
        logger_set = BaseEasyLogging().add_formatter(logger_dict)
        """

        if logger_dict is None:
            print(f'please input logger_dict')
            return None

        if isinstance(logger_dict, dict):
            pass
        else:
            self.abnormal_info_output(f'given logger_dict:{logger_dict} should be  dict')
            return None

        check_successful_flag = True
        additional_info = ''
        for logger_name in logger_dict.keys():
            for each_key in ['handlers', 'level']:
                if each_key in logger_dict[logger_name].keys():
                    pass
                else:
                    additional_info = additional_info + f'given {logger_name} lose {each_key} key-value;'
                    check_successful_flag = False

        if check_successful_flag:
            self.config_dict['loggers'].update(logger_dict)
            self.abnormal_info_output(f'add loggers:{logger_dict} success.')
        else:
            self.abnormal_info_output(f'add loggers, error reason:{additional_info}')
        return None


class EasyLogging(BaseEasyLogging):
    this_class_file_handler_name = 'file'
    this_class_log_name = 'root'

    def __init__(self,
                 this_class_file_handler_name=None,
                 this_class_log_name=None):
        BaseEasyLogging.__init__(self)
        self.this_class_file_handler_name = this_class_file_handler_name
        self.this_class_log_name = this_class_log_name
        self._set_class_info()

    def _set_class_info(self):
        if self.this_class_file_handler_name is None:
            self.this_class_file_handler_name = EasyLogging.this_class_file_handler_name
        if self.this_class_log_name is None:
            self.this_class_log_name = EasyLogging.this_class_log_name

    def get_class_logger(self):
        class_logger = self.get_logger(logger_name=self.this_class_log_name)
        return class_logger

    def set_class_logger_level(self, level):
        self._set_logger_level(logger=self.this_class_log_name, level=level)

    def set_class_logger_file_name(self, file_name):
        this_class_log_path = None
        additional_info = ''
        get_raw_info_success = False
        if 'handlers' in self.config_dict.keys():
            if self.this_class_file_handler_name in self.config_dict['handlers']:
                if 'filename' in self.config_dict['handlers'][self.this_class_file_handler_name]:
                    this_class_log_path = self.config_dict['handlers'][
                        self.this_class_file_handler_name]['filename']
                    get_raw_info_success = True
                else:
                    additional_info = additional_info + (f'{self.this_class_file_handler_name} lose '
                                                         f'filename key-value')
            else:
                additional_info = additional_info + (f'handlers lose'
                                                     f'{self.this_class_file_handler_name} key-value')
        else:
            additional_info = additional_info + 'config_dict lose handlers key-value'

        if get_raw_info_success is True:
            pass
        else:
            self.abnormal_info_output(f'change file name failed, error reason:{additional_info}')
            return None

        # get original output path
        (folder, old_file_name) = os.path.split(this_class_log_path)
        if old_file_name == file_name:
            return None

        # mix path
        log_file_path = os.path.join(folder, file_name)
        # overwrite path
        self._set_handle_detail(handler=self.this_class_file_handler_name,
                                key='filename',
                                value=log_file_path)
        return None

    def set_class_logger_file_dir(self, file_dir):
        this_class_log_path = None
        additional_info = ''
        get_raw_info_success = False
        if 'handlers' in self.config_dict.keys():
            if self.this_class_file_handler_name in self.config_dict['handlers']:
                if 'filename' in self.config_dict['handlers'][self.this_class_file_handler_name]:
                    this_class_log_path = self.config_dict['handlers'][
                        self.this_class_file_handler_name]['filename']
                    get_raw_info_success = True
                else:
                    additional_info = additional_info + (f'{self.this_class_file_handler_name} '
                                                         f'lose filename key-value')
            else:
                additional_info = additional_info + (f'handlers lose '
                                                     f'{self.this_class_file_handler_name} key-value')
        else:
            additional_info = additional_info + 'config_dict lose handlers key-value'

        if get_raw_info_success is True:
            pass
        else:
            self.abnormal_info_output(f'change dir failed, error reason:{additional_info}')
            return None

        # get original output path
        (old_folder, file_name) = os.path.split(this_class_log_path)
        if old_folder == file_dir:
            return None

        # mix path
        log_file_path = os.path.join(file_dir, file_name)
        # overwrite path
        self._set_handle_detail(handler=self.this_class_file_handler_name,
                                key='filename',
                                value=log_file_path)
        return None

    def set_class_logger_file_path(self, file_path):
        self._set_class_handler_key_value(set_key='filename', new_value=file_path)
        return None

    def set_class_logger_file_bkupcnt(self, cnt):
        if isinstance(cnt, Integral):
            pass
        else:
            self.abnormal_info_output(
                f'set error, cnt:{cnt} must be int, current type was {type(cnt)}, please retry')
            return None
        self._set_class_handler_key_value(set_key='backupCount', new_value=cnt)
        return None

    def set_class_logger_file_size(self, size):
        if isinstance(size, Integral):
            pass
        else:
            self.abnormal_info_output(
                f'set error, size:{size} must be int,current type was {type(size)}, please retry')
            return None
        self._set_class_handler_key_value(set_key='maxBytes', new_value=size)
        return None

    def set_class_logger_file_level(self, level):
        if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            pass
        else:
            self.abnormal_info_output(
                f'set error, level:{level} must in DEBUG,INFO,WARNING,ERROR,CRITICAL, please retry')
            return None
        self._set_class_handler_key_value(set_key='level', new_value=level)
        return None

    def _set_class_handler_key_value(self, set_key, new_value):
        old_value = None
        additional_info = ''
        get_raw_info_success = False
        if 'handlers' in self.config_dict.keys():
            if self.this_class_file_handler_name in self.config_dict['handlers']:
                if set_key in self.config_dict['handlers'][self.this_class_file_handler_name]:
                    old_value = self.config_dict['handlers'][
                        self.this_class_file_handler_name][set_key]
                    get_raw_info_success = True
                else:
                    additional_info = additional_info + (f'{self.this_class_file_handler_name} '
                                                         f'lose {set_key} key-value')
            else:
                additional_info = additional_info + (f'handlers lose'
                                                     f'{self.this_class_file_handler_name} key-value')
        else:
            additional_info = additional_info + 'config_dict lose handlers key-value'

        if get_raw_info_success is True:
            pass
        else:
            self.abnormal_info_output(f'change value of {set_key} failed, error reason:{additional_info}')
            return None

        if new_value == old_value:
            return None

        self._set_handle_detail(handler=self.this_class_file_handler_name,
                                key=set_key,
                                value=new_value)
        return None

    def show_class_log_output_path(self):
        additional_info = ''
        if 'handlers' in self.config_dict.keys():
            if self.this_class_file_handler_name in self.config_dict['handlers']:
                if 'filename' in self.config_dict['handlers'][self.this_class_file_handler_name]:
                    this_class_log_path = self.config_dict['handlers'][
                        self.this_class_file_handler_name]['filename']

                    this_class_log_path = this_class_log_path.replace('\\', '/')
                    print(this_class_log_path)
                    return this_class_log_path
                else:
                    additional_info = additional_info + (f'{self.this_class_file_handler_name} '
                                                         f'lose filename key-value')
            else:
                additional_info = additional_info + (f'handlers lose '
                                                     f'{self.this_class_file_handler_name} key-value')
        else:
            additional_info = additional_info + 'config_dict lose handlers key-value'

        self.abnormal_info_output(f'show output path failed, error reason:{additional_info}')
        return None

    def enable_console(self):
        # handler name must be console
        console_handler_exist = False
        set_success = False
        if 'handlers' in self.config_dict:
            if 'console' in self.config_dict['handlers']:
                console_handler_exist = True

        if console_handler_exist:
            pass
        else:
            self.abnormal_info_output(f'Because of lose handler console, so enable failed.')
            return None

        if 'loggers' in self.config_dict:
            if self.this_class_log_name in self.config_dict['loggers']:
                if 'handlers' in self.config_dict['loggers'][self.this_class_log_name]:
                    current_value = self.config_dict['loggers'][
                        self.this_class_log_name]['handlers']

                    if 'console' in current_value:
                        pass
                    else:
                        current_value.append('console')

                    self.config_dict['loggers'][self.this_class_log_name]['handlers'] = (
                        current_value)
                    set_success = True

        if set_success:
            self.abnormal_info_output(f'{self.this_class_log_name} enable console success')
        else:
            self.abnormal_info_output(f'{self.this_class_log_name} enable console failed')

    def disable_console(self):
        # handler name must be console
        console_handler_exist = False
        set_success = False
        if 'handlers' in self.config_dict:
            if 'console' in self.config_dict['handlers']:
                console_handler_exist = True

        if console_handler_exist:
            pass
        else:
            self.abnormal_info_output(f'Because of lose handler console, so enable failed.')
            return None

        if 'loggers' in self.config_dict:
            if self.this_class_log_name in self.config_dict['loggers']:
                if 'handlers' in self.config_dict['loggers'][self.this_class_log_name]:
                    current_value = self.config_dict['loggers'][
                        self.this_class_log_name]['handlers']

                    if 'console' in current_value:
                        current_value = list(set(current_value) - {'console'})
                    else:
                        pass

                    self.config_dict['loggers'][self.this_class_log_name]['handlers'] = (
                        current_value)
                    set_success = True

        if set_success:
            self.abnormal_info_output(f'{self.this_class_log_name} disable console success')
        else:
            self.abnormal_info_output(f'{self.this_class_log_name} disable console success')


class EasyFileLogging(EasyLogging):
    """
    Examples
    ----------
    >>>logger = EasyFileLogging().get_class_logger()
    >>>logger.info('some log information...')
    """

    def __init__(self):
        EasyLogging.__init__(self,
                             this_class_file_handler_name='file',
                             this_class_log_name='logger_file')


class EasySimpleLogging(EasyLogging):
    """
    Examples
    ----------
    >>>logger = EasySimpleLogging().get_class_logger()
    >>>logger.info('some log information...')
    """

    def __init__(self):
        EasyLogging.__init__(self,
                             this_class_file_handler_name='file_simple',
                             this_class_log_name='logger_simple_msg')


class EasyNormalLogging(EasyLogging):
    """
    Examples
    ----------
    >>>logger = EasySimpleLogging().get_class_logger()
    >>>logger.info('some log information...')
    """

    def __init__(self):
        EasyLogging.__init__(self,
                             this_class_file_handler_name='file_normal',
                             this_class_log_name='logger_normal_msg')


class EasyParticularLogging(EasyLogging):
    """
    Examples
    ----------
    >>>logger = EasySimpleLogging().get_class_logger()
    >>>logger.info('some log information...')
    """

    def __init__(self):
        EasyLogging.__init__(self,
                             this_class_file_handler_name='file_particular',
                             this_class_log_name='logger_particular_msg')


class EasyVerboseLogging(EasyLogging):
    """
    Examples
    ----------
    >>>logger = EasySimpleLogging().get_class_logger()
    >>>logger.info('some log information...')
    """

    def __init__(self):
        EasyLogging.__init__(self,
                             this_class_file_handler_name='file_verbose',
                             this_class_log_name='logger_verbose_msg')
                             

if __name__ == '__main__':
    BELobj = BaseEasyLogging()
    mylogger = BELobj.get_logger('logger_console_red')
    mylogger.debug('test11')
    mylogger.info('test12')
    mylogger.warning('test13')
    mylogger.error('test14')
    mylogger.critical('test15')
    print('---')
    ELobj = EasyLogging()
    mylogger = ELobj.get_class_logger()
    mylogger.info('test2')
    print('---')
    EFLobj = EasyFileLogging()
    mylogger = EFLobj.get_class_logger()
    mylogger.info('test3')
    print('---')
    ENLobj = EasyNormalLogging()
    mylogger = ENLobj.get_class_logger()
    mylogger.info('test4')
    print('---')
    EPLobj = EasyParticularLogging()
    mylogger = EPLobj.get_class_logger()
    mylogger.info('test5')
    print('---')
    EVLobj = EasyVerboseLogging()
    mylogger = EVLobj.get_class_logger()
    mylogger.info('test6')