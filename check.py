#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: check.py
# @time: 17/5/2 上午10:56

import json
import sys
import os
from os.path import dirname, realpath
sys.path.append(dirname(realpath(__file__)))

from common import setup_logging
from common.run_cmd import run_cmd
from log_parser import juniper_log, h3c_log, huawei_log

os.chdir(dirname(realpath(__file__)))

if __name__ == '__main__':
    setup_logging()
    params = []
    with open("settings.json") as setting_f:
        settings = json.load(setting_f)
        if settings.get("juniper"):
            for host in settings["juniper"].get("host_list", []):
                run_cmd(host, settings["juniper"]["username"],
                        settings["juniper"]["password"],
                        settings["juniper"]["cmd"], juniper_log,
                        log_dir=settings["log_path"])
        if settings.get("h3c"):
            for host in settings["h3c"].get("host_list", []):
                run_cmd(host, settings["h3c"]["username"],
                        settings["h3c"]["password"],
                        settings["h3c"]["cmd"], h3c_log,
                        log_dir=settings["log_path"])
        if settings.get("huawei"):
            for host in settings["huawei"].get("host_list", []):
                run_cmd(host, settings["huawei"]["username"],
                        settings["huawei"]["password"],
                        settings["huawei"]["cmd"], huawei_log,
                        log_dir=settings["log_path"],
                        conn_method="telnet")
