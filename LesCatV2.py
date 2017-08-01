import urllib.request
import bs4
from bs4 import BeautifulSoup
import re,os
import time
import redis
import random
import math
import hashlib

websiteUrl = 'http://www.lesmao.com/portal.php?page='
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
cookie = 'A1Hl_2132_saltkey=hFn5o5Cz; A1Hl_2132_lastvisit=1494939215; UM_distinctid=15c1183a31428a-0c6909d4478a18-396a7807-1fa400-15c1183a315c3f; __cfduid=df9dfa31b53e5fd254f56d4e6dc0aadad1494942458; A1Hl_2132_st_p=0%7C1495030946%7Cb6f728b0a1ed683464f142c575b95ef5; A1Hl_2132_visitedfid=40D124D99D84D45D125D109D108; A1Hl_2132_onlineusernum=677; A1Hl_2132_viewid=tid_16052; CNZZDATA226185=cnzz_eid%3D692885768-1494938002-%26ntime%3D1495111130; A1Hl_2132_sid=etvzVL; A1Hl_2132_lastact=1495114420%09home.php%09misc; A1Hl_2132_sendmail=1'
host = 'www.lesmao.com'
headers = {'User-Agent': user_agent, 'Cookie': cookie, 'Host': host}
r = redis.Redis(host='127.0.0.1', port=6379)
# cats = redis.Redis(host='127.0.0.1', port=6380)
class LesCat():
    directorys = []
    pageUrls = []

    def requestWebPageBody(self,url):
        print('request ' + url)
        try:
            # proxy_support = urllib.request.ProxyHandler({'http': '113.77.241.145:9797'})
            # opener = urllib.request.build_opener(proxy_support)
            # opener.addheaders = [('User-Agent', user_agent),('Cookie', cookie)]
            # urllib.request.install_opener(opener)
            # response = opener.open(url,timeout=10)
            # pageSoup = BeautifulSoup(response, 'html.parser')
            # return pageSoup


            request = urllib.request.Request(url,headers = headers)
            response = urllib.request.urlopen(request,timeout=10)
            pageSoup = BeautifulSoup(response, 'html.parser')
            return pageSoup
        except:
            print(url + ' spider faild' )
            return

#按顺序爬取目录
    def crawlTheDirectory(self,url):
        print('crawlTheDirectory ' + url)
        values = []
        pageSoup = self.requestWebPageBody(url)
        if type(pageSoup) is type(None):
            print('maybe forbidden')
            return values
        for item in pageSoup.find(class_='clearfix').children:
            if type(item) == bs4.element.Tag:
                tag = item.find(class_='title')
                title = tag.string
                url = tag.a['href']
                coverImg = item.img['src']
                values.append({'cover':coverImg,'title':title,'url':url,'crawl':0})
        return values
#存入数据库
    def saveTheDirectorylToDB(self,value):
        id = self.createRandomId(value['url'])
        if not r.exists(id):
            r.hmset(id,value)

    def saveTheValueToDB(self,value):
        print(value)
#爬取内容页面
    def crawlThePage(self,title,url):
        pageSoup = self.requestWebPageBody(url)
        imgUrlArray = []
        try:
            for img in pageSoup.find_all(alt=re.compile(title)):
                imgUrl = img['src']
                if imgUrl.endswith('jpg'):
                    imgUrlArray.append(imgUrl)

            tags = []
            for tag in pageSoup.find(id=re.compile('thread-tag')).children:
                tags.append(tag.get('title'))
            source = pageSoup.find(id='thread-title').a.string
            host = pageSoup.find(id='thread-title').a['href']
            time = pageSoup.find(id='thread-title').em.string
            scan = pageSoup.find(id='thread-title').span.string
            scan = scan[3:len(scan)]
            id = self.createRandomId(url)
            dic = {'source':source,'host':host,'time':time,'scan':scan,'crawl':1,'img':imgUrlArray,'tag':tags}
            r.hmset(id, dic)
        except:
            id = self.createRandomId(url)
            dic = {'crawl':2}
            r.hmset(id, dic)
            print(url + '   spider faild' )
            return
#缓存图片
    def storeTheImg(self,imgs):
        print('saveImage')

    def startCrawl(self):
        #爬取目录
        #当返回到的内容数为0的话停止爬取
        # for index in range(1,3):
        for index in range(1,1000):
            print('crawl page  ' + str(index))
            directoryUrl = websiteUrl + str(index)
            values = self.crawlTheDirectory(directoryUrl)
            if len(values) > 0 :
                for value in values:
                    self.saveTheDirectorylToDB(value)
                time.sleep(2)
            else:
                print('page have no value   ' + directoryUrl)
                break
        self.startCrawlThePage()


    def startCrawlThePage(self):
        keys = r.keys()
        for key in keys:
            crawl = bytes.decode(r.hmget(key,'crawl')[0])
            if int(crawl) == 0:
                self.crawlThePage(bytes.decode(r.hget(key,'title')),bytes.decode(r.hget(key,'url')))
                time.sleep(2)
            else:
                continue
    def createRandomId(self,value):
        return str(hashlib.sha1(str(value).encode('utf8')).hexdigest())

print('start time  ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
cat = LesCat()
cat.startCrawl()
print('end time  ' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
