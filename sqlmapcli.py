#!/usr/bin/env python

# RESTful API(Part) for sqlmap server
# ---------------------------------------------------------------
#   @get("/task/new")
#   @get("/task/<taskid>/delete")

#   @post("/scan/<taskid>/start")
#   @get("/scan/<taskid>/stop")
#   @get("/scan/<taskid>/kill")
#   @get("/scan/<taskid>/status")
#   @get("/scan/<taskid>/data")
# ---------------------------------------------------------------

import os
import sys
import time
import json
import shutil
import logging
import requests
from report import Report
from threading import Timer
from urlparse import urljoin, urlparse

logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

RESTAPI_SERVER_HOST = "127.0.0.1"
RESTAPI_SERVER_PORT = 8775


class OperationFailed(Exception):

    def __init__(self, msg="???"):
        self.msg = msg

    def __str__(self):
        return "<OperationFailed:%s>" % self.msg


class SqlmapClient(object):

    """
    Sqlmap REST-JSON API client
    """

    def __init__(self, host=RESTAPI_SERVER_HOST, port=RESTAPI_SERVER_PORT):
        self.addr = "http://%s:%d" % (host, port)
        self.options = dict()
        logger.info("Starting REST-JSON API client to '%s'...\n", self.addr)

    def create_task(self):
        try:
            resp = requests.get(urljoin(self.addr, "/task/new"))
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                self.taskid = r.get("taskid", None)
                logger.info(">>> Create task<%s>", self.taskid)
                return self.taskid
            else:
                raise OperationFailed("Failed to create task")
        else:
            raise OperationFailed("Failed to create task, Response<%d>" %
                                  resp.status_code)

    def delete_task(self, taskid=None):
        if taskid is None:
            taskid = self.taskid
        uri = "".join(["/task/", taskid, "/delete"])
        try:
            resp = requests.get(urljoin(self.addr, uri))
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                logger.info("<<< Delete task<%s>", taskid)
                return True
            else:
                raise OperationFailed("Failed to delete task<%s>:%s" %
                                      (taskid, r.get("message")))
        else:
            raise OperationFailed("Failed to delete task<%s>, Response<%s>" %
                                  (taskid, resp.status_code))

    def start_scan(self):
        uri = "".join(["/scan/", self.taskid, "/start"])
        headers = {"content-type": "application/json"}

        try:
            resp = requests.post(urljoin(self.addr, uri),
                                 data=json.dumps(self.options),
                                 headers=headers)
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                self.engineid = r.get("engineid")
                logger.info("Task<%s> start scanning engine<%s>",
                            self.taskid, self.engineid)
            else:
                raise OperationFailed("Task<%s> failed to start engine<%s>:%s" %
                                      (self.taskid, self.engineid, r.get("message")))
        else:
            raise OperationFailed("Task<%s> failed to start engine<%s>, Response<%s>" %
                                  (self.taskid, self.engineid, resp.status_code))

    def stop_scan(self):
        uri = "".join(["/scan/", self.taskid, "/stop"])
        try:
            resp = requests.get(urljoin(self.addr, uri))
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                logger.info("Task<%s> stop engine<%s>",
                            self.taskid, self.engineid)
                return True
            else:
                raise OperationFailed("Task<%s> failed to stop engine<%s>:%s" %
                                      (self.taskid, self.engineid, r.get("message")))
        else:
            raise OperationFailed("Task<%s> failed to stop engine<%s>, Response<%s>" %
                                  (self.taskid, self.engineid, resp.status_code))

    def kill_scan(self):
        uri = "".join(["/scan/", self.taskid, "/kill"])
        try:
            resp = requests.get(urljoin(self.addr, uri))
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                logger.info("Task<%s> kill engine<%s>", self.taskid, self.engineid)
                return True
            else:
                raise OperationFailed("Task<%s> failed to kill engine<%s>:%s" %
                                      (self.taskid, self.engineid, r.get("message")))
        else:
            raise OperationFailed("Task<%s> failed to kill engineid<%s>,Response<%s>" %
                                  (self.taskid, self.engineid, resp.status_code))

    def get_scan_status(self):
        uri = "".join(["/scan/", self.taskid, "/status"])
        try:
            resp = requests.get(urljoin(self.addr, uri))
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                status, retcode = r.get("status"), r.get("returncode")
                logger.info("Engine<%s>(Task<%s>) status: %s", self.engineid, self.taskid, status)
                return retcode
            else:
                raise OperationFailed("Failed to get engine<%s>(Task<%s>) status:%s" %
                                      (self.engineid, self.taskid, r.get("message")))
        else:
            raise OperationFailed("Failed to get engine<%s>(Task<%s>) status,Response<%s>" %
                                  (self.engineid, self.taskid, resp.status_code))

    def get_scan_report(self):
        uri = "".join(["/scan/", self.taskid, "/data"])
        try:
            resp = requests.get(urljoin(self.addr, uri))
        except requests.RequestException as e:
            raise e
        if resp.status_code == 200:
            r = resp.json()
            if r.get("success", False):
                data, error = r.get("data"), r.get("error")
                logger.info("Get engine<%s>(Task<%s>) report, error: %s",
                            self.engineid, self.taskid, error)
                return data, error
            else:
                raise OperationFailed("Failed to get engine<%s>(Task<%s>) report:%s" %
                                      (self.engineid, self.taskid, r.get("message")))
        else:
            raise OperationFailed("Failed to get engine<%s>(Task<%s>) report,Response<%s>" %
                                  (self.engineid, self.taskid, resp.status_code))

    def set_option(self, key, value):
        self.options[key] = value
        return self

    def run(self, url=None, timeout=None):

        if url:
            self.scan_url = url
            self.set_option("url", url)

        if timeout:
            timer = Timer(timeout, self.ontimeout)
            timer.start()

        result = []
        try:
            self.start_scan()
            retcode = self.get_scan_status()
            while retcode is None:
                time.sleep(5)
                retcode = self.get_scan_status()
            if retcode == 0:
                result, _ = self.get_scan_report()
            if timeout:
                timer.cancel()
        except OperationFailed as e:
            if timeout:
                timer.cancel()
            raise e
        return Report(url, result)

    def ontimeout(self):
        if self.get_scan_status() is None:
            self.kill_scan()

    def clear_output(self, path=None):
        if path is None:
            path = os.path.join(os.getenv("HOME"), ".sqlmap/output")
        taskdir = os.path.join(path, urlparse(self.scan_url).hostname)
        if os.path.exists(taskdir):
            shutil.rmtree(taskdir)


#######################################################################
if __name__ == '__main__':

    filepath = "test.txt"
    f = open(filepath, "r")

    client = SqlmapClient()
    try:
        taskid = client.create_task()
    except Exception as e:
        logger.error("Failed to create task: %s", e)
        sys.exit(1)
    client.set_option("dbms", "mysql")  # .set_option("bulkFile", filepath)
    for url in f.readlines():
        try:
            report = client.run(url.strip())
            client.clear_output()
            for d in report.contents[0].values[0].data:
                logger.info("id: %s, title: %s", d.id, d.title)
        except Exception as e:
            logger.error(e)
            continue

    client.delete_task(taskid)

    f.close()
