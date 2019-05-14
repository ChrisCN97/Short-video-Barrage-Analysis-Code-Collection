#单个视频弹幕爬取
import requests
import re
from bs4 import BeautifulSoup
import operator#排序
import time
import os
import codecs

# 获取网址源代码
def getHTMLText(url):
    try:
        #print("获取url中...")
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        #print("获取url完成")
        return r.text
    except:
        print("获取Url失败")

# 网站源码解析
def parsePage(text, av):
    try:
        #print("解析文本...")
        keyStr = re.findall(r'"cid":[\d]*',text)  # B站有两种寻址方式，第二种多一些
        if not keyStr:  # 若列表为空，则等于“False”
            keyStr = re.findall(r'cid=[\d]*', text)
            key = eval(keyStr[0].split('=')[1])
        else:
            key = eval(keyStr[0].split(':')[1])
        commentUrl = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(key)  # 弹幕存储地址
        commentText=getHTMLText(commentUrl)
        soup = BeautifulSoup(commentText, "html.parser")
        soup2=BeautifulSoup(text,"html.parser")
        title=soup2.find('h1').get_text().strip()  # find()方法，获取文本，去掉空格
        title = re.sub('[/\|:*?<>"]', '', title)  # 去掉非法字符
        commentList = readFile(av, title)
        for comment in soup.find_all('d'):
            time = float(comment.attrs['p'].split(',')[0])  # tag.attrs（标签属性，字典类型） 弹幕在视频里的时间
            time2 = float(comment.attrs['p'].split(',')[4])  # 弹幕发布时间
            # 验证是否重复
            if (time in commentList) and commentList[time][1] == comment.string:
                #print(commentList[time],comment.string)
                continue
            else:
                #print(time,commentList[time], comment.string)
                info = [time2, comment.string]
                commentList[time] = info
        newDict = sorted(commentList.items(), key=operator.itemgetter(0))  # 字典排序
        commentList = dict(newDict)
        #print("解析文本完成")
        return commentList, title
    except:
        print("解析失败")

def float2time(f):
    timePlus=int(f)
    m=timePlus//60
    s=timePlus-m*60
    return str(m)+':'+str(s).zfill(2)

def readFile(av, title):
    path = "Data" + "/" + av + title + '.txt'
    commentList = {}
    if os.path.exists(path):
        f = codecs.open(path, 'r', 'utf-8')
        for line in f.readlines()[5:]:
            time = float(line.split()[0])
            time2 = float(line.split()[1])
            string = line.split()[2]
            info = [time2, string]
            commentList[time] = info
        f.close()
    return commentList

def ioFunc(commentList, title, url, av, dayTime, rank):
    # print("写入文本中...")
    path = "Data" + "/" + av + title+ '.txt'  # 目录段
    print("av{} {}  ".format(av, title))
    f = open(path, 'w',encoding='utf-8')  # windows默认gbk编码输出，与网络编码“utf-8”不符
    begin = "排名：{}\n网址：{}\n更新时间：{}\n弹幕总量：{}\n".format(rank+1, url, dayTime, len(commentList))
    f.write(begin)
    ws = "{:<15}{:<16}{}\n".format('preciseTime', 'ofTime', 'comment')
    f.write(ws)
    for time, info in commentList.items():  # 记得items()
        ws = "{:<15}{:<16}{}\n".format(time, info[0], info[1])
        f.write(ws)  # 手动换行
    f.close()

def simpleToolEnter(av, rank):
    dayTime = time.strftime("%m-%d", time.localtime(time.time()))
    url=r"https://www.bilibili.com/video/av"+str(av)
    text=getHTMLText(url)
    commentList, title= parsePage(text, av)
    ioFunc(commentList, title, url, av, dayTime, rank)

#simpleToolEnter("24049574")