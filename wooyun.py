# encoding: utf-8
import MySQLdb
import requests
import re
import sys
import time
import Queue
import threading

reload(sys)
sys.setdefaultencoding("UTF-8")

class wooyun:
    def __init__(self):
        host = "127.0.0.1"
        user = "username"
        password = "passwd"

        self.queue_url = Queue.Queue()
        self.queue_record = Queue.Queue()

        self.conn = MySQLdb.Connect(host=host,port=3306,user=user,passwd=password,db="wooyun",charset="utf8")
        self.cur = self.conn.cursor()

        self.headers = {
                'Host': 'www.wooyun.org',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0',
                'Referer': 'http://www.wooyun.org/bugs/new_public/',
                'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8'
                  }

        self.proxy = {'http':'http://username:passwd@proxy.XXX.com:8080','https':'https://username:passwd@proxy.XXX.com:8080'}
        self.flag = True


    def __del__(self):
        self.cur.close()
        self.conn.close()


    #爬取所有的公开漏洞信息,包括漏洞链接,名称,关注数
    def GetAllPage(self):
        base_url = "http://www.wooyun.org/bugs/new_public/page/"
        for i in range(1864,0,-1):
            url = base_url+str(i)
            self.GetPage(url)


    #爬取单个页面
    def GetPage(self,url):
        onepage = requests.get(url=url,proxies=self.proxy,headers=self.headers)

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
            url = (onebug.split('>')[0][:-1])#漏洞链接
            name = (onebug.split('>')[1][:-3])#漏洞名称
            guanzhu = result_guanzhu[i].split('/')[1]#漏洞关注数
            record = [url,name,guanzhu]
            record_list.append(record)
        self.insert_bugs(record_list)


    #漏洞信息入库mysql
    def insert_bugs(self,record_list):
        for oneline in record_list:

            if self.flag == True:
                self.cur.execute("SELECT url FROM bug WHERE url = %s",oneline[0])
                url = self.cur.fetchone()
                if url != None:
                    self.flag = False
                    print "Should finish"

            self.cur.execute("DELETE FROM bug WHERE url = %s",oneline[0])
            self.cur.execute("INSERT INTO bug(url,name,guanzhu) VALUE (%s,%s,%s)",oneline)
        self.conn.commit()


    #获取url队列
    def Geturlqueue(self):
        self.cur.execute("SELECT url FROM bug WHERE opentime IS NULL ORDER BY id")
        url_list = self.cur.fetchall()
        print len(url_list)
        for url in url_list:
            try:
                self.queue_url.put(url[0])
            except:
                print "ERROR get queue_url : "+ str(url)
                exit(1)
        print "[~]Got queue_url done"


    #获取整个页面
    def Detailofbug(self):
        while not self.queue_url.empty():
            url = self.queue_url.get()
            long_url = "http://www.wooyun.org"+url
            onepage = requests.get(url=long_url,proxies=self.proxy,headers=self.headers)
            try:
                regex_opentime = re.compile("<h3 class=\'wybug_open_date\'>.+</h3>")
                result = re.search(regex_opentime,onepage.text).group()
                regex_Opentime = re.compile("[1-3][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]")
                opentime = re.search(regex_Opentime,result).group()
            except:
                print long_url
                continue
            record = [onepage.text,opentime,url]
            self.queue_record.put(record)

#页面入库
    def insertdetailofbug(self):
        while True:
            if self.queue_record.empty():
                print "No record in queue_record"
                time.sleep(20)
            else:
                record = self.queue_record.get(timeout=20)
                self.cur.execute("UPDATE bug SET wholepage=%s,opentime= %s WHERE url=%s",record)
                self.conn.commit()

#多线程爬取
    def ThreadStart(self):
        self.Geturlqueue()
        for i in range(1,3):
            print "thread " + str(i) + " start"
            time.sleep(1)

            thr = threading.Thread(target=self.Detailofbug,args=())
            thr.setDaemon(True)
            thr.start()

        print "[~]ALL thread start!"
        self.insertdetailofbug()

#每日更新，只爬取数据库中没有的漏洞
    def DaliyUpdate(self):
        while True:
            i = 1
            True_url = "http://www.wooyun.org/bugs/new_public/page/"+str(i)
            self.GetPage(True_url)
            if self.flag == False:
                break
            i = i + 1
        self.ThreadStart()


instance = wooyun()
instance.DaliyUpdate()
