import redis

def clear(index = 1):
    r = redis.Redis(host='127.0.0.1', port=6379, db=index)
    for i in r.keys():
        r.delete(i)
# clear()

def saveBackup():
    r = redis.Redis(host='127.0.0.1', port=6379)
    print(r.config_get('dir'))

# def loadBackup():



saveBackup()