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

class CurJob():
	token = ""
	search = ""
	link_list = []
	def __init__(self, connection, token, search):
		self.con = connection
		self.token = token
		self.search = search

class ReturnMsg():
	Result = False
	Cursor = None
	Message = "OK"
	def __init__(self, Result):
		self.Result = Result
		
#	def sql_query(self, sql):
#		connection.cursor().execute(self.sql)

def Non_query(connection, sql):
    ret = False
    try:
        cursor = connection.cursor()
        cursur.execute(sql)
        connection.commit()
        print(cursor.rowcount, " executed!!" )
        cursor.close()
        ret = True
    finally:
        return ret

def query(connection, sql):
    ret = ReturnMsg(False)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        ret.Cursor = cursor
        ret.Result = True
    except Exception as e:
        ret.Message = str(e)
        ret.Result = False
        print(ret.Message)
    finally:
        if cursor:
            cursor.close()
        return ret
