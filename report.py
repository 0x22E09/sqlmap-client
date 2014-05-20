#!/usr/bin/env python
#-*- coding: utf-8 -*-

class Conf(object):
    def __init__(self, data):
        self.string = data['string']
        self.notString = data['notString']
        self.titles = data['titles']
        self.regexp = data['regexp']
        self.textOnly = data['textOnly']
        self.optimize = data['optimize']


class Data(object):
    def __init__(self, id, data):
        self.id = id
        self.comment = data['comment']
        self.matchRatio = data['matchRatio']
        self.title = data['title']
        self.templatePayload = data['templatePayload']
        self.vector = data['vector']
        self.where = data['where']
        self.payload = data['payload']


class Value(object):
    def __init__(self, data):
        self.dbms = data['dbms']
        self.suffix = data['suffix']
        self.clause = data['clause']
        self.ptype = data['ptype']
        self.dbms_version = data['dbms_version']
        self.prefix = data['prefix']
        self.place = data['place']
        self.data = []
        for i in data['data']:
            self.data.append(Data(i, data['data'][i]))
        self.conf = Conf(data['conf'])
        self.parameter = data['parameter']
        self.os = data['os']


class ReportItem(object):
    def __init__(self, data):
        self.status = data['status']
        self.type = data['type']
        self.values = []
        for v in data['value']:
            self.values.append(Value(v))


class Report(object):
    def __init__(self, url, data):
        self.count = 0
        self.url = url
        self.reports = []
        for d in data:
            self.reports.append(ReportItem(d))
            self.count += 1

    def __str__(self):
        return "<url:'%s', nreport:%d>" % (self.url, self.count)

    def __repr__(self):
        return "<url:'%s', nreport:%d>" % (self.url, self.count)

    def __iter__(self):
        return self.reports


if __name__ == '__main__':
    example = [{u'status': 1,
                u'type': 0,
                u'value': [{u'dbms': u'MySQL',
                            u'suffix': u'',
                            u'clause': [1],
                            u'ptype': 1,
                            u'dbms_version': [u'> 5.0.11'],
                            u'prefix': u'',
                            u'place': u'GET',
                            u'data': {u'1':{u'comment': u'',
                                            u'matchRatio': None,
                                            u'title': u'AND boolean-based blind - WHERE or HAVING clause',
                                            u'templatePayload': None,
                                            u'vector': u'AND [INFERENCE]',
                                            u'where': 1,
                                            u'payload': u'id=1 AND 6981=6981'},
                                      u'3':{u'comment': u'#',
                                            u'matchRatio': None,
                                            u'title': u'MySQL UNION query (NULL) - 1 to 20 columns',
                                            u'templatePayload': None, u'vector': [0, 1, u'#', u'', u'', u'NULL', 1, False],
                                            u'where': 1,
                                            u'payload': u'id=1 UNION ALL SELECT CONCAT(0x716b726771,0x54577443486b6268564d,0x7165697971)#'},
                                      u'5':{u'comment': u'',
                                            u'matchRatio': None,
                                            u'title': u'MySQL > 5.0.11 AND time-based blind',
                                            u'templatePayload': None,
                                            u'vector': u'AND [RANDNUM]=IF(([INFERENCE]),SLEEP([SLEEPTIME]),[RANDNUM])',
                                            u'where': 1,
                                            u'payload': u'id=1 AND SLEEP([SLEEPTIME])'}
                                     },
                            u'conf': {u'string': None,
                                      u'notString': None,
                                      u'titles': False,
                                      u'regexp': None,
                                      u'textOnly': False,
                                      u'optimize': False},
                            u'parameter': u'id',
                            u'os': None}]
                }]

    print(Report("http://www.sina.com.cn", example))
