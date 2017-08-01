from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import os
class Mongo:
    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client['admin']
        self.collection_useraction = self.db['lesmao']
    # def __init__(self,table):
    #     self.client = MongoClient('127.0.0.1', 27017)
    #     self.db = self.client['admin']
    #     self.collection_useraction = self.db[table]
    # def __init__(self,database,table):
    #     self.client = MongoClient('127.0.0.1', 27017)
    #     self.db = self.client[database]
    #     self.collection_useraction = self.db[table]
    # def __init__(self,url,port,database,table):
    #     self.client = MongoClient(url, port)
    #     self.db = self.client[database]
    #     self.collection_useraction = self.db[table]
    def insertData(self,post):
        try:
            self.collection_useraction.insert(post)
        except Exception as e:
            print('insert failed' + repr(e) + str(post))
        except Exception as ex:
            print("表达式为空，请检查")
    def saveTags(self,tags,url):
        try:
            item = self.collection_useraction.find_one({'url':url})
            item['tag'] = tags
            self.collection_useraction.save(item)
        except Exception as e:
            print(str(e))
    def saveTime(self,time,url):
        try:
            item = self.collection_useraction.find_one({'url':url})
            item['time'] = time
            self.collection_useraction.save(item)
        except Exception as e:
            print(str(e))

    def printAllKeys(self):
        # posts = self.collection_useraction.posts
        for post in self.collection_useraction.find():
            path =  '/Users/ay/Desktop/PythonLearning/lesCat/'+str(post['_id']) +'/'
            if(os.path.exists(path)):
                imglist = os.listdir(path)
                if len(imglist) > 0 :
                    continue
                    print("--------" + path)
                    # post["img"] = imglist
                    # self.collection_useraction.save(post)
                else:
                    print("+++++++++++" + path)
                    post["img"] = []
                    self.collection_useraction.save(post)
            else:
                print("+++++++++++" + path)
                post["img"] = []
                self.collection_useraction.save(post)




mongo = Mongo()
mongo.printAllKeys()