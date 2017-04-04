#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: setup_logging.py
# @time: 17/4/4 下午3:11
import os
import logging.config
import yaml
from logging.handlers import TimedRotatingFileHandler as RecordFile
from logging import LogRecord


def write(self, msg):
    self.emit(LogRecord('run_cmd', logging.INFO, __file__, 0, msg, '', ''))
RecordFile.write = write


def setup_logging(
        default_path='logging.yaml',
        default_level=logging.DEBUG,
        env_key='LOG_CFG'
):
    """Setup logging config"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    pass

