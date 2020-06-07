#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      517
#
# Created:     25/10/2019
# Copyright:   (c) 517 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#coding=utf-8
import re
import sys
import json
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import configparser
import time
import pymysql.cursors
import pymysql
import SysInfo
import socket

requests.packages.urllib3.disable_warnings()

PttName, fileName = "", ""
load = {
    'from': '/bbs/' + PttName + '/index.html',
    'yes': 'yes'
}

rs = requests.session()


def get_cfg_items(path = '/home/pi/Crawler/config.ini'):
    config = configparser.RawConfigParser()
    config.read(path,encoding="utf-8")
    return config

def get_sql_con(host, user, passwd):
    connection = pymysql.connect(host=host,
                             user=user,
                             password=passwd,
                             #db='db1',
                             cursorclass=pymysql.cursors.DictCursor)
    return connection

def check_job_exist(connection,sql):
    ret = False
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        r = cursor.rowcount    
        cursor.close ()
        if r == 0:
            ret = False
        else:
            ret = True
    finally:
        #print(ret)
        return ret

def get_job_enable(connection,sql):
    ret = False
    try:
        rmsg = SysInfo.query(connection,sql)
        if rmsg.Result:
            for r in rmsg.Cursor:
                result = r['enable'].upper()
        if result != "Y" and result != "T":
            ret = False
        else:
            ret = True
    finally:
        print(ret)
        return ret

def Insert_DB(token, data,connection,items):
		ret =False
		try:
			sql = items['SysInfo']['job_insert']
			sql = sql.replace(":LINE_ID", token)
			sql = sql.replace(":DATA", data)
			sql = sql.replace(":HOST", socket.gethostname())
			sql = sql.replace("https://www.ptt.cc/bbs/","")		
			ret = SysInfo.Non_query(connection,sql)			
			#cursor = connection.cursor()
			#cursor.execute(sql)
			#connection.commit()
			#print(cursor.rowcount, "Record inserted successfully into Laptop table")
			#cursor.close()
		finally:
			print("Insert_DB done!")

def Insert_DB(token, data_list,connection,items):
		try:
			cursor = connection.cursor()
			while data_list:
				data = data_list.pop(0)
				sql = items['SysInfo']['job_insert']
				sql = sql.replace(":LINE_ID", token)
				sql = sql.replace(":DATA", data)		
				sql = sql.replace(":HOST", socket.gethostname())
				sql = sql.replace("https://www.ptt.cc/bbs/","")
				SysInfo.Non_query(connection,sql)	
				#print(sql)		
				#cursor.execute(sql)
				#connection.commit()
				#print(cursor.rowcount, "Record inserted successfully into Laptop table")				
		finally:
			if cursor:
				cursor.close()
			print("Insert_DB done!")	


if __name__ == "__main__":
    start_time = time.time()
    items = get_cfg_items()
    connection = get_sql_con(items['SysInfo']['host'],items['SysInfo']['user'],items['SysInfo']['pass'])

    try:
        #sql = "SELECT t.enable FROM db1.home_control t where t.id=1 and t.name='matrix_show' limit 1"
        sql = items['SysInfo']['job_enable']
        if get_job_enable(connection,sql):
            print("OK")
        else :
            print("NG")
    finally:
        connection.close()
    print("execution time:" + str(time.time() - start_time) + "s")
