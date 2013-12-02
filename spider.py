#coding=UTF-8
"""
Worker WorkerManager模型
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time, urllib, urllib2
from BeautifulSoup import BeautifulSoup
import argparse
import urlfunction
import workerthreading
import dboper
import log
import re


def get_url(tag, attr, soup, list):
    """
    从BeautifulSoup中提取tag标签中attr属性
    """
    temp = soup.findAll(tag, attrs={attr: True})
    for i in range(len(temp)):
        list.append(temp[i][attr])


def process_url_list(url, list):
    """
    对list中所有url进行处理
    """
    length = len(list)
    pos = 0
    for i in range(length):
        tempUrl = list[pos].strip()
        tempUrl = urlfunction.get_complete_url(url, tempUrl)
        if(tempUrl == None):
            del list[pos]
        else:
            tempUrl = urlfunction.get_standard_url(tempUrl)
            list[pos] = tempUrl
            pos += 1
            continue


def job(url):
    """
    从网站源代码中提取网址
    """
    global _logger
    global urlScanNum
    try:
        #打印扫描进度
        print_progress()
        
        req = urllib2.Request(url)
        content = urllib2.urlopen(req,None,timeout=10).read()
        soup = BeautifulSoup(content)
        list = []
        get_url('', 'href', soup, list)
        get_url('', 'src', soup, list)
        list = {}.fromkeys(list).keys()
        urlScanNum += len(list)
        process_url_list(url, list)
        return list
    except urllib2.URLError, e:
        detailError = ";url=" + url + ";exception=" + str(e)
        _logger.info(detailError)
    except urllib2.HTTPError, e:
        detailError = ";url=" + url + ";exception=" + str(e)
        _logger.info(detailError)




def init():
    """
    获取命令行参数
    """
    newParser = argparse.ArgumentParser();
    newParser.add_argument("-u", "--url", dest="url", help="target url");
    newParser.add_argument("-dbfile", "--dbfile", dest="dbfile", help="database file name");
    newParser.add_argument("-d", "--depth", type=int, dest="depth", help="scann depth(default=2)");
    newParser.add_argument("-thread", "--thread", type=int, dest="thread", help="thread pool(default=10)");
    newParser.add_argument("-key", "--key", dest="key", help="keyword");
    newParser.add_argument("-l", "--log", type=int, dest="log", help="loglevel");
    
    args = newParser.parse_args();
    argsDict = args.__dict__;
    
    url = ""
    if argsDict["url"] == None:
        print "please input the url,for example: python 1.py -u www.baidu.com"
        return
    else:
        url = argsDict["url"]
        
    dbfile = "spider.db"
    if argsDict["dbfile"] != None:
        dbfile = argsDict["dbfile"]
        if dbfile[-3:] != ".db":
            dbfile += ".db"
            
    depthMax = 2
    if argsDict['depth'] != None:
        depthMax = argsDict['depth'];
        
    threadNum = 10
    if argsDict['thread'] != None:
        threadNum = argsDict['thread']
        
    keyword = ""
    if argsDict['key'] != None:
        keyword = argsDict['key']
        
    logLevel = 1
    if argsDict['log'] != None:
        logLevel = argsDict['log']
        
    return url, dbfile, depthMax, threadNum, keyword, logLevel


def start():
    global _logger
    global urlStoreNum
    global urlKeywordStoreNum
    url, dbfile, depthMax, threadNum, keyword, logLevel = init()
    url = urlfunction.get_standard_url(url)
    domain = urlfunction.get_domain(url)
    domain_table = domain.replace('.','_')
    domain_table = '_' + domain_table
    
    db = dboper.Dboper(dbfile)
    if db.isExistTable(domain_table) == 0:
        db.createTable(domain_table)
    else:
        db.clearTable(domain_table)
    if keyword != "":
        if db.isExistTable(domain_table+'_key') == 0:
            db.createTable(domain_table+'_key')
        else:
            db.clearTable(domain_table+'_key')
            
    if db.select_count(domain_table, url) == 0:
        db.insert(domain_table, url, 0)
        urlStoreNum += 1
        if is_match_keyword(url, keyword):
            db.insert(domain_table+'_key', url, 0, keyword)
            urlKeywordStoreNum += 1
    
    print 'Start spidering'
    depth = 0
    urlList = []
    urlList2 = []
    urlList2.append(url)    
    while len(urlList2) and depth < depthMax:
        depth += 1
        tempScanUrlList = []
        urlList = urlList2
        urlList2 = []
        lengthUrlList = len(urlList)
        for i in range(lengthUrlList):
            tempScanUrlList.append(urlList.pop())
            if ((i + 1) % threadNum == 0) or (i == lengthUrlList - 1):
                wm = workerthreading.WorkerManager(threadNum)
                for j in range(len(tempScanUrlList)):
                    url = tempScanUrlList.pop()
                    wm.add_job(job, url)
                wm.wait_for_complete()
                queue = wm.get_result()
                while queue.empty() != True:
                    tempList = queue.get()
                    if tempList == None:
                        continue
                    for i in range(len(tempList)):
                        #打印扫描进度
                        print_progress()
                        #将数据库操作进行异常处理
                        try:
                            count = db.select_count(domain_table, tempList[i])
                            if count == 0:
                                urlList2.append(tempList[i])
                                db.insert(domain_table, tempList[i], depth)
                                urlStoreNum += 1
                                if is_match_keyword(tempList[i], keyword):
                                    db.insert(domain_table+'_key', tempList[i], depth, unicode(keyword, "gbk"))
                                    urlKeywordStoreNum += 1
                        except Exception, e:
                            _logger.info(str(e))
                            
    
    print_progress(1)
    print 'End spider'
    
def is_match_keyword(url, keyword):
    """
     判断网页是否与关键字keyword匹配，如果keyword为空，则返回False
    """
    if keyword=="":
        return False
    try:
        req = urllib2.Request(url)
        content = urllib2.urlopen(req,None,timeout=10).read()
        keyword = unicode(keyword, "gbk")
        content = unicode(content, "gbk")
        flag = keyword in content
        return flag
    except urllib2.URLError, e:
        detailError = ";url=" + url + ";exception=" + str(e)
        _logger.info(detailError)        
    except urllib2.HTTPError, e:
        detailError = ";url=" + url + ";exception=" + str(e)
        _logger.info(detailError)
    return False




def get_seconts(_time):
    """
    将日期换算成秒
    """
    hour = time.strftime('%H',time.localtime(_time))
    minute = time.strftime('%M',time.localtime(_time))
    secont = time.strftime('%S',time.localtime(_time))    
    return int(hour) * 3600 + int(minute) * 60 + int(secont)

def print_progress(flag=0):
    """
    打印进度
    """
    global preSecont
    global urlScanNum
    global urlStoreNum
    _time = time.time()
    curSecont = get_seconts(_time)
    if curSecont-preSecont > 10 or flag:
        print "Scan progress........."
        print time.strftime('%H:%M:%S',time.localtime(_time))
        preSecont = curSecont
        print "Scaned url numbers:", urlScanNum, ", Stored to url database url numbers:",urlStoreNum
    



#设置日志文件
_logging = log.Logging()
_logger = _logging.get_logger();
preSecont = 0
urlScanNum = 1
urlStoreNum = 0
urlKeywordStoreNum = 0

start()

#http://127.0.0.1:8080/test_environment/spider/1/1.html
