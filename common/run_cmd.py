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


def do_telnet(ip, username, password, commands, pipe_name="/dev/null"):
    if not isinstance(commands, list):
        logger.error("type of commands parameter should be a list")
        return
        # try to open log file
    try:
        log_f = RecordFile(filename=pipe_name, when='m', interval=1, backupCount=48)
    except Exception, e:
        logger.warn(ip, "Continue with log_file not present", e)
        log_f = None
        # open String IO stream, for improve the processing speed,
        # because write to file then read will cause double effort
    str_buff = StringIO()

    try:
        telnet = telnetlib.Telnet(ip)
        telnet.read_until("Username:")
        telnet.write(username.encode('ascii', 'ignore') + "\n")
        telnet.read_until("Password:")
        telnet.write(password.encode('ascii', 'ignore') + "\n")

        for cmd in commands:
            cmd_separator = "=" * 10 + " " + ip + " == " + cmd + " " + "-" * 10 + "\n"
            cmd_starter = "===START===\n"
            cmd_stopper = "---STOP---\n"
            logger.debug("Running command %s" % cmd.encode('ascii', 'ignore'))
            try:
                telnet.write(cmd.encode('ascii', 'ignore') + "\n")
                _, _, stdout = telnet.expect(["<.*?>"], timeout=5)

                # WORKAROUND: fix later
                while not cmd.encode('ascii', 'ignore') in stdout:
                    _, _, stdout = telnet.expect(["<.*?>"], timeout=5)

                if "screen-length" in cmd:
                    continue

                if log_f:
                    log_f.write(cmd_separator)
                    log_f.write(cmd_starter)
                str_buff.write(cmd_separator)
                str_buff.write(cmd_starter)

                if log_f:
                    log_f.write(stdout)
                str_buff.write(stdout)

                if log_f:
                    log_f.write(cmd_stopper)
                str_buff.write(cmd_stopper)
            except Exception, e:
                logger.error(e)

        logger.info('%s\tOK' % ip)
        telnet.close()
        log_f.flush()
        log_f.close()
    except Exception, e:
        logger.error('%s\tError: %s' % (ip, e))

    # pprint(str_buff.getvalue())
    return str_buff.getvalue()


def run_cmd(ip, username, password, cmd, parse_func, conn_method='ssh', log_dir='.'):
    logger.info("Checking %s ..." % ip)
    str_buffer = ''
    if conn_method == 'ssh':
        pass
    elif conn_method == 'telnet':
        pass
    else:
        raise Exception("Unknow connect method")
    logger.debug("Parsing string buffer to json %s" % ip)
    return parse_func(str_buffer)

if __name__ == '__main__':
    pass
