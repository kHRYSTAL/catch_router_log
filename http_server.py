#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @version: ??
# @usage: 
# @author: kHRYSTAL
# @license: Apache Licence 
# @contact: khrystal0918@gmail.com
# @site: https://github.com/kHRYSTAL
# @software: PyCharm
# @file: http_server.py
# @time: 17/4/4 下午3:06
from tornado import httpserver, ioloop, web
from tornado.options import define, options
import tornado.options
from datetime import datetime

import json
import os
import re

LOG_PATH = "./logs/"

# 定义全局可以使用的选项port 调用方式 options.port
define("port", default=8005, help="run on the given port", type=int)


def listDir(path, fnFilter=None):
    if not os.path.isdir(path):
        return
    for file_name in os.listdir(path):
        if os.path.isfile(os.path.join(path, file_name)):
            if fnFilter is not None and not re.match(fnFilter, file_name):
                continue
            yield file_name


class RootHandler(web.RequestHandler):
    def get(self):
        self.redirect("/index.html")


class HostList(web.RequestHandler):
    def get(self):
        file_list = list(set([re.sub("\.\d{4}-\d{2}-\d{2}_\d{2}-\d{2}", "", file_name)
                              for file_name in listDir(LOG_PATH,
                                                  "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$")]))
        self.write(json.dumps({"host_list": file_list}))


class HostStatus(web.RequestHandler):
    def get(self):
        ip = self.get_argument("ip")
        log_path = "./logs/"
        backup_list = [datetime.strptime(re.match(".*(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})$",
                                                  file_name).group(1),
                                         "%Y-%m-%d_%H-%M")
                       for file_name in listDir(log_path,
                                                ip + ".json" + ".\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$")
                       if re.match(".*(\d{4}-\d{2}-\d{2}_\d{2}-\d{2})$", file_name)]
        backup_list.sort()
        with open(os.path.join(log_path, ip + ".json." + backup_list[-1].strftime("%Y-%m-%d_%H-%M")), 'r') as fjson:
            print log_path + ip + ".json." + backup_list[-1].strftime("%Y-%m-%d_%H-%M")
            data = json.loads(fjson.read())
            fjson.close()
            self.set_header("Content-Type", "application/json")
            self.set_status(200)
            self.write(json.dumps(data))
        self.flush()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class SwitchLog(web.RequestHandler):
    def get(self):
        log_path = "./logs/"
        hostIp = self.get_argument("ip")
        if os.path.isfile(os.path.join(log_path, hostIp + ".json")):
            fjson = open(os.path.join(log_path, hostIp + ".json"), 'r')
            data = json.loads(fjson.read())
            fjson.close()
            self.write(json.dumps(data))
        else:
            self.write_error(404)


if __name__ == '__main__':
    SETTINGS = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret="secret"
    )
    urls = [
        (r"/", RootHandler),
        (r"/index.html", IndexHandler),
        (r"/host_list", HostList),
        (r"/sw_log", HostStatus),
    ]
    tornado.options.parse_command_line()
    app = web.Application(
        handlers=urls,
        **SETTINGS
    )
    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()