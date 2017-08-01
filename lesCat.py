import urllib.request
import bs4
from bs4 import BeautifulSoup
import re,os
import time
import redis
import random
import math
from MongoDBClient import Mongo

websiteUrl = 'http://www.lesmao.com/portal.php?page='
infoPageUrlArray = []
index = 0
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
cookie = 'A1Hl_2132_saltkey=hFn5o5Cz; A1Hl_2132_lastvisit=1494939215; UM_distinctid=15c1183a31428a-0c6909d4478a18-396a7807-1fa400-15c1183a315c3f; __cfduid=df9dfa31b53e5fd254f56d4e6dc0aadad1494942458; A1Hl_2132_st_p=0%7C1495030946%7Cb6f728b0a1ed683464f142c575b95ef5; A1Hl_2132_visitedfid=40D124D99D84D45D125D109D108; A1Hl_2132_onlineusernum=677; A1Hl_2132_viewid=tid_16052; CNZZDATA226185=cnzz_eid%3D692885768-1494938002-%26ntime%3D1495111130; A1Hl_2132_sid=etvzVL; A1Hl_2132_lastact=1495114420%09home.php%09misc; A1Hl_2132_sendmail=1'
host = 'www.lesmao.com'
headers = {'User-Agent': user_agent, 'Cookie': cookie, 'Host': host}
fiveTimesOneSleep = 0
r = redis.Redis(host='127.0.0.1', port=6379)
mongo = Mongo()
class lesCat:
    #开始爬取
    def startSpiderWithPageCount(self,page):
        startPage = page
        for i in range(startPage,startPage+150):
            print('startPage' + str(i))
            self.spiderWithPage(i)
            time.sleep(1)
    #爬取指定page页面中列表
    def spiderWithPage(self,page):
        infoPageUrlArray = []
        global headers
        global fiveTimesOneSleep
        url = websiteUrl + str(page)
        print(url)
        try:
            request = urllib.request.Request(url,headers = headers)
            response = urllib.request.urlopen(request,timeout=10)
            pageSoup = BeautifulSoup(response, 'html.parser')
        except:
            print('spider list exceptUrl' + url)
            return
        # contentArray = pageSoup.find_all(id='wp',class_='wp')
        for item in pageSoup.find(class_='clearfix').children:
            if type(item) == bs4.element.Tag:
                # fiveTimesOneSleep += 1
                # if fiveTimesOneSleep >= 5:
                #     time.sleep(1.5)
                #     fiveTimesOneSleep = 1
                tag = item.find(class_='title')
                title = tag.string
                url = tag.a['href']
                # mongo.insertData({'title':str(title),'url':str(url)})
                # print(title, url)
                infoPageUrlArray.append([title, url])
                # self.spiderImgUrlFromPageUrl(title,url)
        self.insertToDataBase(infoPageUrlArray)

    def spiderUpdateTime(self,url):

        try:
            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request, timeout=10)
            pageSoup = BeautifulSoup(response, 'html.parser')
            return pageSoup.find(id=re.compile('thread-title')).em.string

        except Exception as  e:
            print('error' + str(e) + url)
    def spiderTagsWithUrl(self,url):
        try:
            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request, timeout=10)
            pageSoup = BeautifulSoup(response, 'html.parser')
            tags = []
            for tag in pageSoup.find(id=re.compile('thread-tag')).children:
                tags.append(tag.get('title'))
        except Exception as  e:
            print('error' + str(e) + url)
        return tags
    #进入详情页爬取图片地址
    def spiderImgUrlFromPageUrl(self,title,url):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        # print(title,'\t',url)
        imageUrlArray = []
        baseUrl = url[0:-8]
        for page in range(1,6):
            try:
                pageUrl = baseUrl + str(page) + '-1.html'
                request = urllib.request.Request(pageUrl, headers=headers)
                response = urllib.request.urlopen(request,timeout = 10)
                pageSoup = BeautifulSoup(response, 'html.parser')
                # print( pageSoup.find_all(alt = re.compile(title)))
                for img in pageSoup.find_all(alt=re.compile(title)):
                    imgUrl = img['src']
                    if imgUrl.endswith('jpg'):
                        imageUrlArray.append(imgUrl)
            except:
                print('spider image exceptUrl' + pageUrl)
                continue
                    # print(imgUrl)
        self.saveImage(title,imageUrlArray)
        # for item in pageSoup.find(id='thread-pic').ul.children:
        #     # if type(item) == bs4.element.Tag:
        #     print(item)
    #保存图片
    def saveImage(self,title,imageUrlArray):
        title.replace('/',',')
        savePath = '/Users/ay/Desktop/PythonLearning/lesCat/'+title+'/'

        if not os.path.exists(savePath):
            try:
                os.mkdir(savePath)
            except:
                r.append('faildUrl','%^'+title+'#$')
        else:
            return
        for imageUrl in imageUrlArray:
            name = self.getImageName(imageUrl)
            imgPath = savePath + name
            try:
                urllib.request.urlretrieve(imageUrl,imgPath)
            except:
                print('save exceptUrl' +imageUrl)
                continue
    def getImageName(self,imageUrl):
        arr = imageUrl.split("/")
        return arr[len(arr) - 1]
    def insertToDataBase(self,lists):
        for item in lists:
            randomId = self.createRandomId()
            r.hset(randomId,'title',item[0])
            r.hset(randomId,'url',item[1])
            print('-------- %s' %item)

    def createRandomId(self):
        return (str(math.ceil((time.time() + random.random()*1000000)*1000000)))
    def spiderImageFromRedis(self):
        # r = redis.Redis(host='127.0.0.1', port=6379)
        for name in r.keys():
            title = str(r.hget(name,'title'),'utf-8')
            url = str(r.hget(name,'url'),'utf-8')
            print('title:'+title,'url:'+url)
            self.saveTagAndTime(url)
            # self.spiderImgUrlFromPageUrl(title,url)
            # r.set('currentId',name)
            time.sleep(1)

    def spiderImageFromCurrentIndex(self):
        lists = r.keys()
        currentIndex = lists.index(r.get('currentId'))
        for name in  lists[currentIndex + 1:]:
            try:
                title = str(r.hget(name,'title'),'utf-8')
                url = str(r.hget(name,'url'),'utf-8')
                print('title:'+title,'url:'+url)
                self.spiderImgUrlFromPageUrl(title,url)
                r.set('currentId',name)
                time.sleep(2)
            except:
                continue

    def saveTagAndTime(self,url):
        time = self.spiderUpdateTime(url)
        tags = self.spiderTagsWithUrl(url)
        mongo.saveTags(tags,url)
        mongo.saveTime(time,url)
# print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
# cat = lesCat()
# cat.startSpiderWithPageCount(1)
# load detail page directly
# cat.spiderImgUrlFromPageUrl('Goddes 头条女神 No.207 Modo 何娇娇药药肉丝[有删减包完整]','http://www.lesmao.com/thread-15172-2-1.html')
# print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

# cat.spiderImageFromRedis()
# cat.spiderImageFromCurrentIndex()
# r = redis.Redis(host='127.0.0.1', port=6379)
# print(len(r.keys()))



