#!/usr/bin/python
# -*- coding: UTF-8 -*-

import commands
import os
import config
from var_dump import var_dump
from time import ctime, sleep, time
import socket
import pymysql


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


db = pymysql.connect(host="127.0.0.1", user="root", password="xx", db="newping", port=3306)
cur = db.cursor()
aff = cur.execute("truncate table fpings")
db.commit()
cur.close()
db.close()

ip_source = get_host_ip()

start = time()
st = int(round(start))

getipallsql = "SELECT ipdb.ip,assoc.mainid AS mainid,assoc.targetid AS targetid,targetipdb.targetip FROM ipassoc assoc JOIN ipdb ON assoc.mainid = ipdb.id JOIN targetipdb ON assoc.targetid = targetipdb.id WHERE targetipdb.targetip = '%s'" % (
    ip_source)
# print getipallsql
iplist = list(config.zhudb.query(getipallsql))

# var_dump(iplist)
ipall_list = []
ipdic = {}
targetids = ''
for var_ip in iplist:
    ipall_list.append(var_ip['ip'])
    targetids = var_ip['targetid']
    ipdic[var_ip['ip']] = var_ip['mainid']

print 'targetid >>>>>> ', targetids
print '=============='
var_dump(ipdic)
ipss = " ".join(ipall_list);
# var_dump(ipss)
micmd = "/usr/sbin/fping %s -c 3 -q -i 0.1 -a --period=500" % (ipss)
# print 'micmd>>>',micmd
(state, output) = commands.getstatusoutput(micmd)
# print state
# print output
reslist = output.split('\n')
# 执行truncate操作
# sql_truncate = "truncate table fpings"
# config.mysqldb.query(sql_truncate)

for baseres in reslist:
    ipandres = baseres.split(':')
    ipinfo = ipandres[0].strip()  # IP信息
    ifins = '100%' in baseres  # 判断是否100%loss
    if ifins:
        sqlinserts = "insert into fpings (`ip`,`name`,`loss`,`times`,`lasttime`,`point_belong`) values ('%s','%s','%s','%s','%s','%s')" % (
        ipinfo, '', '100%', '0', st, '')

        config.mysqldb.query(sqlinserts)
        sqlhis = "insert into ping_history (`ip`,`name`,`loss`,`times`,`lasttime`,`point_belong`) values ('%s','%s','%s','%s','%s','%s')" % (
        ipinfo, '', '100%', '0', st, '')

        config.mysqldb.query(sqlhis)
    else:
        lossres = ipandres[1].split(',')
        lossinfo = lossres[0].split('=')[1].split('/')[2]
        pinginfo = lossres[1].split('=')[1].split('/')[1]
        lossif = float(lossinfo[:-1])
        pingif = float(pinginfo)
        sqlinserts = "insert into fpings (`ip`,`name`,`loss`,`times`,`lasttime`,`point_belong`) values ('%s','%s','%s','%s','%s','%s')" % (
        ipinfo, '', lossinfo, pinginfo, st, '')
        # print(sqlinserts)
        config.mysqldb.query(sqlinserts)
        sqlhis = "insert into ping_history (`ip`,`name`,`loss`,`times`,`lasttime`,`point_belong`) values ('%s','%s','%s','%s','%s','%s')" % (
        ipinfo, '', lossinfo, pinginfo, st, '')
        # print(sqlhis)
        config.mysqldb.query(sqlhis)
# for var_ip in iplist
