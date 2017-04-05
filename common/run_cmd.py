#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: run_cmd.py
# @time: 17/4/5 上午10:20
import os
import paramiko
import logging
from cStringIO import StringIO
from common.setup_logging import RecordFile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def do_ssh(ip, username, password, commands, pipe_name="/dev/null"):
    if not isinstance(commands, list):
        logger.error("type of commands parameter should be a list")

    # try to open log file
    try:
        log_f = RecordFile(filename=pipe_name, when='m', interval=1, backupCount=48)
    except Exception, e:
        logger.warn(ip, "Continue with log_file not present", e)
        log_f = None
    str_buff = StringIO()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, look_for_keys=False,
                    username=username, password=password, timeout=15,)
        for cmd in commands:
            cmd_separator = "=" * 10 + " " + ip + "==" + cmd + " " + "-" * 10 + "\n"
            cmd_starter = "===START===\n"
            cmd_stopper = "---STOP---\n"
            logger.debug("Running command %s" % cmd)
            try:
                _, stdout, _ = ssh.exec_command(cmd)

                if log_f:
                    log_f.write(cmd_separator)
                    log_f.write(cmd_starter)
                str_buff.write(cmd_separator)
                str_buff.write(cmd_starter)

                read_buffer = ''
                for char in stdout.read():
                    if not char == '\n':
                        read_buffer += char
                        continue
                    else:
                        if log_f:
                            log_f.write(read_buffer)
                        str_buff.write(read_buffer + '\n')
                        # print line
                        read_buffer = ''

                if log_f:
                    log_f.write(cmd_stopper)
                str_buff.write(cmd_stopper)
            except Exception, e:
                logger.error(e)

        logger.info('%s\tOK' % ip)
        ssh.close()
        log_f.flush()
        log_f.close()
    except Exception, e:
        logger.error('%s\tError: %s' % (ip, e))

    # pprint(str_buff.getValue)
    return str_buff.getvalue()

if __name__ == '__main__':
    pass
