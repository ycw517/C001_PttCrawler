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
import db_util
import SysInfo


notice_num = 0
requests.packages.urllib3.disable_warnings()

PttName, fileName = "", ""
load = {
    'from': '/bbs/' + PttName + '/index.html',
    'yes': 'yes'
}

rs = requests.session()

link_list = []



def lineNotify(token, msg):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    #while msg:
    #	send = msg.pop(0)
    payload = {'message': msg}
    r = requests.post(url, headers=headers, params=payload)

    return r.status_code

def getPageNumber(content):
    startIndex = content.find('index')
    endIndex = content.find('.html')
    pageNumber = content[startIndex + 5: endIndex]
    return pageNumber


def over18(board):
    res = rs.get('https://www.ptt.cc/bbs/' + board + '/index.html', verify=False)
    # 先檢查網址是否包含'over18'字串 ,如有則為18禁網站
    if (res.url.find('over18') > -1):
        print("18禁網頁")
        load = {
            'from': '/bbs/' + board + '/index.html',
            'yes': 'yes'
        }
        res = rs.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
        return BeautifulSoup(res.text, 'html.parser')
    return BeautifulSoup(res.text, 'html.parser')


def crawler(url_list, curjob):
    count, g_id = 0, 0
    total = len(url_list)
    # 開始爬網頁
    while url_list:
        url = url_list.pop(0)
        res = rs.get(url, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 如網頁忙線中,則先將網頁加入 index_list 並休息1秒後再連接
        if (soup.title.text.find('Service Temporarily') > -1):
            url_list.append(url)
            # print u'error_URL:', url
            # print u'error_URL head:', soup.title.text
            time.sleep(1)
        else:
            count += 1
            # print u'OK_URL:', url
            # print u'OK_URL head:', soup.title.text
            #for entry in soup.select('.r-ent'):
                #print(entry.select('.title')[0].text,entry.select('.date')[0].text,entry.select('.author')[0].text)
            for r_ent in soup.find_all(class_="r-ent"):
                # 先得到每篇文章的篇url
                link = r_ent.find('a')
                tt = r_ent.select('.title')[0].text
                print (tt)
                if (curjob.search in tt and link):
                    # 確定得到url
                    URL = 'https://www.ptt.cc' + link['href']
                    g_id = g_id + 1
                    # 避免被認為攻擊網站
                    time.sleep(0.1)
                    # 開始爬文章內容
                    sql_check = items['SysInfo']['job_check_exist']
                    sql_check = sql_check.replace(':LINE_ID',curjob.token)
                    sql_check = sql_check.replace(':DATA', URL)
                    check_ret = db_util.check_job_exist(curjob.con,sql_check)
                    if (check_ret==False):
                        parseGos(URL, g_id)
            print("download: " + str(100 * count / total) + " %.")
        # 避免被認為攻擊網站
        time.sleep(0.1)


def checkformat(soup, class_tag, data, index, link):
    # 避免有些文章會被使用者自行刪除 標題列 時間  之類......
    try:
        content = soup.select(class_tag)[index].text
    except Exception as e:
        print('checkformat error URL', link)
        # print 'checkformat:',str(e)
        content = "no " + data
    return content


def parseGos(link, g_id):
    res = rs.get(link, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')

    # author 文章作者
    # author  = soup.select('.article-meta-value')[0].text
    author = checkformat(soup, '.article-meta-value', 'author', 0, link)
    # print 'author:',author

    # title 文章標題
    # title = soup.select('.article-meta-value')[2].text
    title = checkformat(soup, '.article-meta-value', 'title', 2, link)
    # print 'title:',title

    # date 文章日期
    # date = soup.select('.article-meta-value')[3].text
    date = checkformat(soup, '.article-meta-value', 'date', 3, link)
    # print 'date:',date

    # ip 文章文章ip
    try:
        targetIP = u'※ 發信站: 批踢踢實業坊'
        ip = soup.find(string=re.compile(targetIP))
        ip = re.search(r"[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*", ip).group()
    except:
        ip = "ip is not find"
    # print 'ip:',ip

        # content  文章內文
    try:
        content = soup.find(id="main-content").text
        target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'
        content = content.split(target_content)
        content = content[0].split(date)
        main_content = content[1].replace('\n', '  ')
        # print 'content:',main_content
    except Exception as e:
        main_content = 'main_content error'
        print('main_content error URL' + link)
        return
        # print 'main_content error:',str(e)

    try:
        #print(items['SysInfo']['job_check_exist'])
        #delta = datetime.now() - datetime.strptime(date, "%a %b %d %H:%M:%S %Y")
        if 1 == 1 : #curjob.search in title and delta.seconds < interval:
            global sendmsg
            sendmsg += '\n'+str(datetime.strptime(date, "%a %b %d %H:%M:%S %Y"))+'\n' + title +'\n'+ link
            link_list.append(link)
    except:
    	print("error")
    	return

def purge_data(connection,sql):
    try:
        SysInfo.Non_query(connection,sql)
    except:
        print("purge data error")

if __name__ == "__main__":
    ParsingPage, CfgPath = int(sys.argv[1]), sys.argv[2]
    start_time = time.time()
    timep = datetime.now().strftime("%H:%M:%S")
    print('Start parsing ' + PttName + '....' + timep)

    try:
        items = db_util.get_cfg_items(CfgPath)
        #print(items['SysInfo']['job_check_exist'])
        connection = db_util.get_sql_con(items['SysInfo']['host'],items['SysInfo']['user'],items['SysInfo']['pass'])
        sql_enable = items['SysInfo']['job_enable']
        if db_util.get_job_enable(connection,sql_enable) == False:
            print ("JOb Disable")
            exit (0)
        sql_purge = items['SysInfo']['job_purge']
        #print(sql_purge)
        purge_data(connection, sql_purge)
        with connection.cursor() as cursor:
            # Read a single record
            sql = items['SysInfo']['job_main']
            cursor.execute(sql)
            for  r  in  cursor :
                print(r['board_name'], r['board_title'])
                soup = over18(r['board_name'])
                ALLpageURL = soup.select('.btn.wide')[1]['href']
                # 得到本看板全部的index數量
                ALLpage = int(getPageNumber(ALLpageURL)) + 1
                index_list = []
                #notice_num = 0
                sendmsg = " " + r['board_title'] + " at " +  r['board_name']
                link_list = []
                for index in range(ALLpage, ALLpage - int(ParsingPage), -1):
                    page_url = 'https://www.ptt.cc/bbs/' + str(r['board_name']) + '/index' + str(index) + '.html'
                    index_list.append(page_url)
                curjob = SysInfo.CurJob(connection, r['line_id'], r['board_title'])
                crawler(index_list, curjob)
                #crawler(index_list, r['board_title'], r['line_id'], connection, item)
                if link_list: #notice_num != 0:
                    lineNotify(r['line_id'], sendmsg)  # print(sendmsg)#
                    db_util.Insert_DB(r['line_id'], link_list,connection,items)

        cursor.close ()
    finally:
        connection.close()
    print("爬蟲結束...")
    print("execution time:" + str(time.time() - start_time) + "s")

