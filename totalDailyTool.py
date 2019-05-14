# 视频排行榜爬取
from Tool import simpleToolEnter
import requests
from bs4 import BeautifulSoup  # 安装BeautifulSoup4插件
import re

def getHTMLText(url):
    try:
        # print("获取url中...")
        r=requests.get(url,timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        # print("获取url完成")
        return r.text
    except:
        print("获取Url失败")

def top20get():
    url = "https://www.bilibili.com/ranking/origin/0/0/3"
    html = getHTMLText(url)
    soup = BeautifulSoup(html, "html.parser")
    rankWrap = soup.find_all(class_='rank-item')
    avNumList = []
    for link in rankWrap:
        av = re.findall(r'av[\d]*', link.a['href'])[0][2:]
        avNumList.append(av)
    for n in range(100):
        if avNumList[n] == '26396676' or avNumList[n] == '26651811' or avNumList[n] == '26820009'\
                or avNumList[n] == '26853744' or avNumList[n] == '26956955':  # 删除bug视频号
            print("跳过异常{}/100".format(n + 1))
            continue
        simpleToolEnter(avNumList[n], n)
        print("已完成{}/100".format(n + 1))

for n in range(1):
    top20get()