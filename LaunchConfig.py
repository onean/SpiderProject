import os
class LaunchConfig():
    def __init__(self):
        self.launchMongoDB()
        # self.launchRedis()
    def launchRedis(self):
        print(os.system("redis-server"))
        print('launchRedis')
    def launchMongoDB(self):
        os.system("mongod --config /usr/local/etc/mongod.conf")
launch = LaunchConfig()