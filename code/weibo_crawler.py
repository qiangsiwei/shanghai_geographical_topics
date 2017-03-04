# -*- coding: utf-8 -*-

import sys
import urllib2
import urllib
import json
import re
import base64
import hashlib
import rsa
import binascii
import cookielib
import time
import random
import fileinput

body = {  
   '__rnd':'',
   '_k':'',
   '_t':'0',
   'count':'50',
   'end_id':'',
   'max_id':'',
   'pagebar':'',
   'pre_page':'0',
   'uid':'1742439305'
}

uuid = None
cj = cookielib.LWPCookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
urllib2.install_opener(opener)

# 获取 servertime noce pubkey rsakv
def get_info():
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.4)'
    data = urllib2.urlopen(url).read()
    p = re.compile('\((.*)\)')
    try:
        json_data = p.search(data).group(1)
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        publicKey = data['pubkey']
        rsakey = data['rsakv']
        return servertime, nonce, publicKey, rsakey
    except:
        print 'error'
        return None

st, non, pubkey, rsakv = get_info()

# 用户名加密
def get_user(username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username

# 密码加密
def get_pwd(pwd):
    rsaPublicKey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublicKey, 65537)
    message = str(st) + '\t' + str(non) + '\n' + str(pwd)
    pwd_1 = rsa.encrypt(message, key)
    pwd_2 = binascii.b2a_hex(pwd_1)
    return pwd_2

def login(username, pwd):
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)'
    postdata = {  
        'entry': 'weibo',  
        'gateway': '1',  
        'from': '',  
        'savestate': '7',  
        'userticket': '1',  
        'ssosimplelogin': '1',  
        'vsnf': '1',  
        'vsnval': '',  
        'su': '',  
        'service': 'miniblog',  
        'servertime': '',  
        'nonce': '',  
        'pwencode': 'rsa2',  
        'sp': '',  
        'encoding': 'UTF-8',  
        'prelt':'115',
        'rsakv': rsakv,
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',  
        'returntype': 'META'  
    }  
    postdata['servertime'] = st
    postdata['nonce'] = non
    postdata['su'] = get_user(username)
    postdata['sp'] = get_pwd(pwd)
    postdata_url = urllib.urlencode(postdata)
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0 Chrome/20.0.1132.57 Safari/536.11'}
    req = urllib2.Request(url = url, data = postdata_url, headers = headers)
    result = urllib2.urlopen(req)
    text = result.read()
    print text
    p = re.compile('location\.replace\(\'(.*?)\'\)')
    try:
        url_login = p.search(text).group(1)
        content = urllib2.urlopen(url_login).read()
        p = re.compile('uniqueid\"\:\"(.*?)\"')
        uuid =  p.search(content).group(1)
    except:
        print 'error'

def crawl_weibo_place(start=1):
    _file = open("weibo_place.txt","a")
    login('2475023337@qq.com', 'qsw1229')
    for i in range(start, 3760):
        print i
        url = "http://place.weibo.com/search?city=0021&keyword=上海&page="+str(i)+"&"
        url = url + urllib.urlencode(body)
        result = re.sub(r' +',' ',urllib2.urlopen(urllib2.Request(url), timeout=20).read().replace('\r\n','').replace('\t',''))
        for (_type, content, location) in re.findall(r'<li>.*?<img class="([^\s]+?)".*?<dd class="details">([\s\S]*?)</dd>.*?<div class="w_vspii"([\s\S]*?)>.*?</li>', result):
            regex_poid = re.compile(r'href="/poi/([^\s]+?)"')
            regex_name = re.compile(r'class="pao_dl_dd_nr">(.+?)</a>')
            regex_weibo_num = re.compile(r'href="/weibo/.*?">([^\s]+?)</a>')
            regex_users_num = re.compile(r'href="/users/.*?">([^\s]+?)</a>')
            regex_photo_num = re.compile(r'href="/photos/.*?">([^\s]+?)</a>')
            _poid = (regex_poid.findall(content) or ["NA"])[0]
            _name = re.sub(r'<.+?>','',(regex_name.findall(content) or ["NA"])[0])
            _regex_weibo_num = (regex_weibo_num.findall(content) or ["NA"])[0]
            _regex_users_num = (regex_users_num.findall(content) or ["NA"])[0]
            _regex_photo_num = (regex_photo_num.findall(content) or ["NA"])[0]
            regex_location = re.compile(r'actlat="([^\s]+?)" actlon="([^\s]+?)"')
            _location = ','.join((regex_location.findall(location) or ["NA","NA"])[0])
            _file.write('\t'.join([_type,_poid,_name,_regex_weibo_num,_regex_users_num,_regex_photo_num,_location])+'\n')
    _file.close()

def crawl_weibo(_index_begin, _index_end, _weibo_username, _weibo_password='qsw1229'):
    _lng_bound, _lat_bound = [121.308,121.598], [31.146,31.306]
    _poid_dict = {}
    for line in fileinput.input("weibo_place.txt"):
        _type, _poid, _name, _regex_weibo_num, _regex_users_num, _regex_photo_num, _location = line.strip().split('\t')
        _lng, _lat = float(_location.split(',')[1]), float(_location.split(',')[0])
        if _regex_weibo_num != "NA" and int(_regex_weibo_num) > 1000 and _lng_bound[0]<_lng<_lng_bound[1] and _lat_bound[0]<_lat<_lat_bound[1]:
            _poid_dict[_poid] = {'_name':_name, '_location':_location, '_weibo_num':int(_regex_weibo_num)}
    fileinput.close()
    _poid_list = []
    for _poid, _value in _poid_dict.iteritems():
        _value['_poid'] = _poid
        _poid_list.append(_value)
    _poid_list = sorted(_poid_list, key=lambda x:x['_weibo_num'], reverse=True)
    login(_weibo_username, _weibo_password)
    _file = open("weibo_place_weibo_{0}_{1}.txt".format(_index_begin,_index_end),"w")
    _file_record = open("weibo_place_weibo_{0}_{1}_record.txt".format(_index_begin,_index_end),"w")
    _sum = 0
    for _index, _item in enumerate(_poid_list[_index_begin:_index_end]):
        _poid, _name, _weibo_num, _location = _item['_poid'], _item['_name'], _item['_weibo_num'], _item['_location']
        for _page in range(1, int(_weibo_num)/20):
            print "{0}/{1}".format(_index,len(_poid_list)), _poid, "{0}/{1}".format(_page,int(_weibo_num)/20)
            url, result = "http://place.weibo.com/weibo/"+_poid+"/"+str(_page), None
            for r in xrange(3):
                try:
                    result = re.sub(r' +',' ',urllib2.urlopen(urllib2.Request(url), timeout=20).read().replace('\r\n','').replace('\t',''))
                    # time.sleep(random.uniform(0, 20))
                    time.sleep(10)
                    break
                except:
                    continue
            if result:
                _do_break = False
                weibo_items = re.findall('<dd class="content">([\s\S]*?)<dd class="clear"></dd>', result)
                for line in weibo_items:
                    _file.write('\t'.join([_poid,str(_page),line.strip()])+'\n')
                    try:
                        _text = re.sub(r'<.+?>','',re.findall(r'</a>：([\s\S]*?)</a>', line)[0]).strip()
                        _date = re.findall(r'<a.*?class="date">(.*?)</a>', line)[0].strip()
                        _time = time.strptime(_date, "%Y-%m-%d %H:%M")
                        if _time.tm_year <= 2014:
                          _do_break = True
                        _file_record.write("{0}\t{1}\t{2}\t{3}\n".format(_index, _name, _date, _text))
                    except:
                        _file_record.write("{0}\t{1}\t{2}\t{3}\n".format(_index, _name, _date, ""))
                if _do_break:
                    # or len(weibo_items) == 0
                    break
    _file.close()
    _file_record.close()

def extract_weibo(_index_begin, _index_end):
    _file = open("weibo_place_weibo_{0}_{1}_extracted.txt".format(_index_begin, _index_end), "w")
    _index, _curr_poid, _curr_poid_index, _curr_poid_count, _time_begin, _time_end = 0, "", 0, 0, "", ""
    for line in fileinput.input("weibo_place_weibo_{0}_{1}.txt".format(_index_begin, _index_end)):
        # _index += 1
        # print _index
        _poid = line.strip().split('\t')[0]
        _content = ' '.join(line.strip().split('\t')[2:])
        try:
            _uid = re.findall(r'<a.*?class="card_content" alt="(.+?)">', _content)[0].strip()
            _text = re.sub(r'<.+?>','',re.findall(r'</a>：([\s\S]*?)</a>', _content)[0]).strip()
            _date = re.findall(r'<a.*?class="date">(.*?)</a>', line)[0].strip()
            _loc, _lng, _lat = re.findall(r'<a class="showmapbox" action-data="(.*?)\|(.*?),(.*?)\|0\|.*?">', _content)[0]
            _lng, _lat = round(float(_lng),3), round(float(_lat),3)
            _cord = "{0}|{1},{2}".format(_loc.strip(), _lng, _lat)
            _file.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(_poid,_date,_cord,_uid,_text))
            # validation
            if _poid != _curr_poid:
                if _curr_poid != "":
                    print _curr_poid_index, _curr_poid, _curr_poid_count, _time_begin, _time_end
                _curr_poid, _curr_poid_index, _curr_poid_count, _time_begin = _poid, _curr_poid_index+1, 0, _date
            else:
                _time_end, _curr_poid_count = _date, _curr_poid_count+1
        except:
            continue
    fileinput.close()
    _file.close()

crawl_weibo_place()

# crawl_weibo(0,9,'1484526076@qq.com')
# crawl_weibo(9,27,'2475023337@qq.com')
# crawl_weibo(27,54,'qswcrtest1@qq.com')
# crawl_weibo(54,93,'qswcrtest2@qq.com')
# crawl_weibo(93,147,'qswcrtest3@qq.com')
# crawl_weibo(147,222,'1484526076@qq.com')
# crawl_weibo(222,336,'2475023337@qq.com')
# crawl_weibo(336,498,'qswcrtest1@qq.com')
# crawl_weibo(498,721,'qswcrtest2@qq.com')
# crawl_weibo(721,1200,'qswcrtest3@qq.com')

# extract_weibo(0,9)
# extract_weibo(9,27)
# extract_weibo(27,54)
# extract_weibo(54,93)
# extract_weibo(93,147)
# extract_weibo(147,222)
# extract_weibo(222,336)
# extract_weibo(336,498)
# extract_weibo(498,721)
# extract_weibo(721,1200)
