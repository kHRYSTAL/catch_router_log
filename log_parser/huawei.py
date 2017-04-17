#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: huawei.py
# @time: 17/4/15 下午8:11


import os, re
import json
from common.setup_logging import RecordFile

STDOUT_FILTER_PATTERN = r"========== (?P<ip>.*?) == (?P<cmd>.*?) ----------.+?" \
                        r"===START===.*?" \
                        r"(?P=cmd)(?P<stdout>.*?)" \
                        r"---STOP---"

INTERFACE_IO_ERR = r"(?P<interface_name>\S+?)[\s]+current state.*?Line protocol.*?" \
                   r"Input:\s+\d+ packets.*?Total Error:\s+(?P<input_err_number>\d+).*?" \
                   r"Output:\s+\d+ packets.*?Total Error:\s+(?P<output_err_number>\d+)"

DTDI_OUTPUT = r"Port\s+(?P<interface_name>\S+?)[\s]+transceiver diagnostic"
DTDI_OUTPUT_GETPOWER = r"Port\s+(?P<interface_name>\S+?)[\s]+transceiver diagnostic.*?" \
                       r"TxPower\(dBm\)\s+(?P<tx_power>[-\d\.]+).*?" \
                       r"RxPower\(dBm\)\s+(?P<rx_power>[-\d\.]+)"


def huawei_log(str_buffer, log_path='.'):
    # write log to log file
    rtn = {
        "type": "huawei",
        "status": []
    }
    ipaddr = ''
    for ip, cmd, stdout in re.findall(STDOUT_FILTER_PATTERN, str_buffer, re.S|re.M):
        ipaddr = ip
        model_json = {
            "cmd": cmd,
            "output": []
        }

        if "dis int XGigabitEthernet" in cmd:
            # for
            for interface, input_err_number, output_err_number in \
                    re.findall(INTERFACE_IO_ERR, stdout, re.S | re.M):
                model_json["output"].append({
                        "interface": interface,
                        "input_err_number": input_err_number,
                        "output_err_number": output_err_number
                })
            rtn["status"].append(model_json)
            continue
        elif "display transceiver diagnosis interface" in cmd:
            start_index = [m.start(0) for m in re.finditer(DTDI_OUTPUT, stdout, re.S | re.M)]
            index_tuple = zip(start_index, map(lambda x: x - 1, start_index[1:] + [0]))
            for start, stop in index_tuple:
                m = re.match(DTDI_OUTPUT_GETPOWER, stdout[start:stop], re.S | re.M)
                if m:
                    model_json["output"].append({
                        "interface": m.group("interface_name"),
                        "tx_power": m.group("tx_power"),
                        "rx_power": m.group("rx_power")
                    })
            rtn["status"].append(model_json)
            continue

    # pprint(rtn)
    rtn["ip"] = ipaddr
    log_f = RecordFile(filename=os.path.sep.join([log_path, ipaddr + ".json"]),
                       when='m', interval=1, backupCount=56)
    log_f.write(json.dumps(rtn))
    log_f.close()

