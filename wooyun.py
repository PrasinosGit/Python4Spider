# encoding: utf-8
import MySQLdb
import requests
import re
import sys
reload(sys)
sys.setdefaultencoding("UTF-8")
class wooyun:
    def __init__(self):
        host = "127.0.0.1"
        user = "root"
        password = "passwd"
        self.conn = MySQLdb.Connect(host=host,port=3306,user=user,passwd=password,db="wooyun",charset="utf8")
        self.cur = self.conn.cursor()


    def __del__(self):
        self.cur.close()
        self.conn.close()

    #爬取所有的公开漏洞信息,包括漏洞链接,名称,关注数
    def GetAllPage(self):
        base_url = "http://www.wooyun.org/bugs/new_public/page/"
        for i in range(1861,1,-1):
            url = base_url+str(i)
            self.GetPage(url)

    #爬取单个页面
    def GetPage(self,url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        onepage = requests.get(url=url,headers=headers)

        #漏洞链接和名称正则
        regex_herfandname = re.compile('/bugs/wooyun-[0-9]+-[0-9]+\">.+</a>')
        result_herfandname = re.findall(regex_herfandname,onepage.text)

        #漏洞关注数正则
        regex_guanzhu = re.compile('#comment\">[0-9]*/[0-9]*')
        result_guanzhu = re.findall(regex_guanzhu,onepage.text)

        #单个页面漏洞数小于20,应该是存在问题的
        if (len(result_guanzhu) != len(result_herfandname)) or (len(result_guanzhu) != 20):
            print "re error"
            print url

        record_list = []

        for i in range(0,len(result_guanzhu)):
            onebug = result_herfandname[i]
            url = (onebug.split('>')[0][:-1])
            name = (onebug.split('>')[1][:-3])
            guanzhu = result_guanzhu[i].split('/')[1]
            record = [url,name,guanzhu]
            record_list.append(record)
        self.insert_bugs(record_list)

    #漏洞信息入库mysql
    def insert_bugs(self,record_list):
        for oneline in record_list:
            self.cur.execute("DELETE FROM bug WHERE url = %s",oneline[0])
            self.cur.execute("INSERT INTO bug(url,name,guanzhu) VALUE (%s,%s,%s)",oneline)
        self.conn.commit()

    #爬取所有漏洞的详细信息
    def Detailofallbug(self):
        self.cur.execute("SELECT url FROM bug")
        url_list = self.cur.fetchall()
        for url in url_list:
            try:
                self.Detailofbug(url[0])
                print i
                i=i+1
            except:
                print "Got ERROR : "+ str(url)

    #目前只正则公开时间,可以后续拓展
    def Detailofbug(self,url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        long_url = "http://www.wooyun.org"+url
        onepage = requests.get(url=long_url,headers=headers)

        #公开时间正则
        regex_opentime = re.compile("<h3 class=\'wybug_open_date\'>.+</h3>")
        result = re.search(regex_opentime,onepage.text).group()
        regex_Opentime = re.compile("[1-3][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]")
        result = re.search(regex_Opentime,result).group()
        record = [result,url]

        self.cur.execute("UPDATE bug set opentime= %s WHERE url = %s",record)
        self.conn.commit()
