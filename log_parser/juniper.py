#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: juniper.py
# @time: 17/4/16 下午7:22


# import os

import os, re
import json
import logging
from common.setup_logging import RecordFile

ERR_INTERFACE_LINE = "Physical interface:"
Host = "Hostname:"
ERR_KEYWORD = "Input errors:"
PATTERN_ERR = "Input errors: (\d+), Output errors: (\d+)"

err_compiled_pattern = re.compile(PATTERN_ERR)
logger = logging.getLogger(__name__)

STR_PATTERN = "========== (?P<ip>.*?) == (?P<cmd>.*?) ----------.+?===START===(?P<stdout>.*?)---STOP---"
# INTERFACE_STATISTICS = "Physical interface: (.*?),.*?(?:Input errors: (-?\d+), Output errors: (-?\d+))"
INTERFACE_STATISTICS = r"(?<=Physical interface): (?P<interface_name>.*?),.*?\n(?P<space>^\s)?" \
                       r"(?(space)(?:.*?[Ii]nput errors: (?P<input_error>\d+), [Oo]utput errors: (?P<output_error>\d+))|(?:.*?))"
systime = r"Current time:.*CST\b" \
          r"System booted:.*CST\b"


def juniper_log(str_buffer, log_path='.'):
    # write log to log file
    rtn = {
        "type":"juniper",
        "status": []
    }

    ipaddr = ''
    for (ip, cmd, stdout) in re.findall(STR_PATTERN, str_buffer, re.S | re.M):
        model_json = None
        m = re.search("Hostname: (.*?)\n*Model: (.*?)\n.*", stdout)
        if m is not None:
            if ipaddr == '':
                ipaddr = ip
            model_json = {"cmd": cmd,
                          "output": {
                              "hostname": m.group(1),
                              "model": m.group(2)
                          }}
            rtn["status"].append(model_json)
            continue

        # for 'show interfaces statistics'
        m = re.findall(INTERFACE_STATISTICS, stdout, re.S | re.M)
        if m:
            output = []
            for (interface_name, _, input_err_number, output_err_number) in m:
                output.append({"interface": interface_name,
                               "input_err_number": input_err_number,
                               "output_err_number": output_err_number})
            model_json = {
                "cmd": cmd,
                "output": output
            }
            rtn["status"].append(model_json)
            continue
        # for 'show system uptime'
        m = re.findall(systime,stdout,re.S | re.M)
        if m:
            output = []
            for (current_time, system_booted) in m:
                output.append({"current_time": current_time,
                               "system_booted": system_booted})
            model_json = {
                "cmd": cmd,
                "output": output
            }
            rtn["status"].append(model_json)
            continue

        # for 'show routine-engine'
        re_patten = r"Routing Engine status:\s*?(Slot \d):.*?" \
                    r"Memory utilization\s+(\d+).*?CPU utilization:.*?Idle\s+(\d+)\s+percent"
        m = re.findall(re_patten, stdout, re.S)
        if m:
            model_json = {
                "cmd": cmd,
                "output": []
            }
            for (slot_name, mem_utilization, cpu_utilization) in m:
                model_json["output"].append({
                                  "slot_name": slot_name,
                                  "mem_utilization": mem_utilization,
                                  "cpu_utilization": cpu_utilization
                              })
            rtn["status"].append(model_json)
            continue
        # for 'system/chassis alarms'
        if 'alarms' in cmd:
            model_json = {"cmd": cmd,
                          "output": stdout.strip()}
            rtn["status"].append(model_json)
            continue

    rtn["ip"] = ipaddr
    logger.info("Dumping json object to file " + os.path.sep.join([log_path, ipaddr+".json"]))
    log_f = RecordFile(filename=os.path.sep.join([log_path, ipaddr+".json"]),
                       when='m', interval=1, backupCount=56)

    log_f.write(json.dumps(rtn))
    log_f.close()