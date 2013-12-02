#coding=utf-8

import re

def get_standard_url(url):
    """标准化url，比如："http://www.baidu.com/"
    """
    url = url.strip()
    if url[:4] != "http":
        url = "http://" + url;
        
    if re.match(r'(.*)\?(.*)', url) or re.match(r'(.*)\#(.*)', url):
        return url
    
    #对于http://www.baidu.com/1.html，这种url最后为文件名的情况
    if re.match(r'^(http://|https://)[^\/]*/.*([^\.]*\.[^\.]*)$', url):
        return url
    
    #对于http://www.baidu.com/abc，url最后为路径名称的情况
    if url[-1] != "/":
        url = url + "/";
    return url;

def is_path_url(url):
    url = get_standard_url(url)
    if re.match(r'^(http://|https://)[^\/]*/.*([^\.]*\.[^\.]*)$', url):
        return 0
    return 1

def get_host(url):
    """提取url中域名host，如：http://www.baidu.com/abc，则提取www.baidu.com
        主要在存储数据库中使用
    """
    url += "/"
    pattern = re.compile(r'^(http://|https://)(.*?)/')
    match = pattern.search(url)
    if match:
        url = match.group(2)
    pattern = re.compile(r'(.*):(.*)')
    match = pattern.search(url)
    if match:
        return match.group(1)
    
    return url

def get_domain(url):
    """
    提取host中主域名，如：www.baidu.com，则提取baidu.com
    主要在源代码提取到链接后，判断该链接是否为同域名链接    
    """
    host = get_host(url)
    #判断是否为ip
    if re.match(r'\d*\.\d*\.\d*\.\d*', host):
        return host
    
    topDomains = ['com','cn','edu','gov','int','mil','net','org','biz','info','pro','name','museum','coop','aero','xxx','idv']
    domain = ''
    flag1 = 0
    while True:
        flag2 = 0
        for i in range(len(topDomains)):
            pattern = re.compile(r'(.*)(\.'+topDomains[i]+')$')
            match = pattern.search(host)
            if match:
                host = match.group(1)
                domain = match.group(2) + domain
                flag1 = 1
                flag2 = 1
                break;
        if flag2 == 0:
            break;
    
    #如果通用顶级域名均没出现，则从后到前取两位域名即可
    if flag1 == 0:
        pattern = re.compile(r'([^\.]*\.[^\.]*)$')
        match = pattern.search(host)
        if match:
            return match.group(1)
    else:
        pattern = re.compile(r'[^\.]*$')
        match = pattern.search(host)
        if match:
            return match.group()+domain
            
    return host

def get_whole_host(url):
    """
    提取url整个域名，比如：http://www.baidu.com/abc
    则提取：http://www.baidu.com/
    """
    url = get_standard_url(url)
    pattern = re.compile(r'^(http|https)://(.*?)/')
    match = pattern.search(url)
    if match:
        return match.group(1)+"://"+match.group(2)+"/"

def get_url_path(url):
    """
    返回一个url的路径，比如：http://www.baidu.com/abc/abc.html?123#123
    则返回：http://www.baidu.com/abc/
    """
    _url = url
    
    #去？号
    pattern = re.compile(r'(.*)\?')
    match = pattern.search(_url)
    if match:
        _url = match.group(1)
        
    #去#号
    pattern = re.compile(r'(.*)\#')
    match = pattern.search(_url)
    if match:
        _url = match.group(1)
        
    _url = get_standard_url(_url)
    flag = is_path_url(_url)
    if flag == 0:
        _url += '/'
    pattern = re.compile(r'(http://|https://)(.*)/[^\/]*\/$')
    match = pattern.search(_url)
    if match:
        _url = match.group(1) + match.group(2)
    
    return get_standard_url(_url)

def get_real_url(curPath, url):
    """
    通过传递当前路径curPath和从源代码中提取到的内部链接url进行处理。
    主要四种情况：1.html  /1.html  ./1.html  ../1.html，
    针对不同情况提取出真实的url，同时可能会出现../../1.html这种情况，所以需要进行递归处理。
    """
    pattern1 = re.compile(r'^[^\/\.].*') # 2.html
    pattern2 = re.compile(r'^/(.*)') # /2.html
    pattern3 = re.compile(r'^\./(.*)') # ./2.html
    pattern4 = re.compile(r'^\.\./(.*)') # ../2.html
    
    match = pattern2.search(url)
    if match:
        return get_whole_host(curPath) + url[1:]
    
    match = pattern3.search(url)
    if match:
        return get_real_url(curPath, match.group(1))
    
    match = pattern4.search(url)
    if match:
        preUrl = get_url_path(curPath)
        if preUrl:
            return get_real_url(preUrl, match.group(1))
        
    match = pattern1.search(url)
    if match:
        return curPath + url
    
    return None


def get_complete_url(url, tempUrl):
    """
    对源代码中url进行处理，如果合理，则返回处理后完整的url
    如果不合理，则返回None
    """
    if tempUrl[0] == "#":
        return None
    if re.match('^(http://|https://)', tempUrl) or re.match('^//', tempUrl):
        if re.match('^//', tempUrl):
            tempUrl = "http:" + tempUrl
        if get_domain(url) == get_domain(tempUrl):
            return tempUrl
        else:
            return None
    else:
        curPath = get_url_path(url)
        tempUrl = get_real_url(curPath, tempUrl)
        return tempUrl


if __name__ == "__main__":
    url = "http://www.baidu.com/abc/abc/1.html#abc=123"
    print get_standard_url(url)