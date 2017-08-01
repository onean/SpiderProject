import hashlib


def createRandomId(value):
    return str(hashlib.sha1(str(value).encode('utf8')).hexdigest())

print(createRandomId('http://www.lesmao.com/thread-12645-1-1.html'))