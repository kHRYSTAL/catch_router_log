#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: h3c.py
# @time: 17/4/13 上午9:51
import json
import os
import re
from common.setup_logging import RecordFile

STDOUT_FILTER_PATTERN = r"========== (?P<ip>.*?) == (?P<cmd>.*?) ----------.+?" \
                        r"===START===" \
                        r".*?(?P=cmd)(?P<stdout>.*?)" \
                        r"---STOP---"

DI_CURRENT_STATE = r"(?P<interface_name>[^\s]+?)[\n\r]+Current state:"
DI_STDOUT_WITH_INOUT_PATTERN = r"(?P<interface_name>\S+?)[\n\r]+Current state:.*?" \
                               r"Input:\s+(?P<input_err_number>\d+|-) input errors.*?" \
                               r"Output:\s+(?P<output_err_number>\d+|-) output errors"
DI_STDOUT_WO_INOUT_PATTERN = r"(?P<interface_name>\S+?)[\n\r]+Current state:.*?"

DIDI_OUTPUT = r"(?P<interface_name>\S+?)[\s]+transceiver diagnostic information:.*?"
DIDI_OUTPUT_GETPOWER = r"(?P<interface_name>\S+?)[\s]+transceiver diagnostic information:.*?" \
                       r"Current diagnostic parameters:.*?" \
                       r"\d+\s+[-\d.]+\s+[-\d.]+\s+(?P<rx_power>[-\d.]+)\s+(?P<tx_power>[-\d.]+)"

def h3c_log(str_buffer, log_path='.'):
    # write log to log file
    rtn = {
        "type": "h3c",
        "status": []
    }
    ipaddr = ''
    for ip, cmd, stdout in re.findall(STDOUT_FILTER_PATTERN, str_buffer, re.S|re.M):
        ipaddr = ip
        model_json = {
            "cmd": cmd,
            "output": []
        }

        if "dis interface" in cmd:
            start_index = [m.start(0) for m in re.finditer(DI_CURRENT_STATE, stdout, re.S|re.M)]
            index_tuple = zip(start_index, map(lambda x: x-1, start_index[1:] + [0]))
            for start, stop in index_tuple:
                m = re.match(DI_STDOUT_WITH_INOUT_PATTERN, stdout[start:stop], re.S|re.M)
                if m:
                    model_json["output"].append({
                        "interface": m.group("interface_name"),
                        "input_err_number": m.group("input_err_number"),
                        "output_err_number": m.group("output_err_number")
                    })
                    continue
                else:
                    m = re.match(DI_STDOUT_WO_INOUT_PATTERN, stdout[start:stop], re.S|re.M)
                    if not m:
                        continue
                    model_json["output"].append({
                        "interface": m.group("interface_name"),
                        "input_err_number": "0",
                        "output_err_number": "0"
                    })
                    continue
            rtn["status"].append(model_json)
            continue
        elif "dis transceiver diagnosis interface" in cmd:
            start_index = [m.start(0) for m in re.finditer(DIDI_OUTPUT, stdout, re.S | re.M)]
            index_tuple = zip(start_index, map(lambda x: x - 1, start_index[1:] + [len(stdout)]))
            for start, stop in index_tuple:
                m = re.match(DIDI_OUTPUT_GETPOWER, stdout[start:stop], re.S|re.M)
                if not m:
                    model_json["output"].append({
                        "interface": m.group("interface_name"),
                        "rx_power": m.group("rx_power"),
                        "tx_power": m.group("tx_power")
                    })
            rtn["status"].append(model_json)
            continue

    rtn["ip"] = ipaddr
    # pprint(rtn)
    log_f = RecordFile(filename=os.path.sep.join([log_path, ipaddr + ".json"]),
                       when='m', interval=1, backupCount=56)
    log_f.write(json.dumps(rtn))
    log_f.close()
    pass

if __name__ == '__main__':
    pass
