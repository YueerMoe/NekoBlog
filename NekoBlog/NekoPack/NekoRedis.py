import json

import redis

with open("NekoBlog/configs/redis.json", 'r') as f:
    cfg = json.loads(f.read())


class Redis:

    def __init__(self):
        host = cfg['host']
        port = cfg['port']
        pwd = cfg['pwd']
        self.__redis = redis.StrictRedis(host=host, port=port, password=pwd)

    def set(self, key, value, ex):
        return self.__redis.set(key, value, ex)

    def get(self, key):
        if self.__redis.exists(key):
            return self.__redis.get(key)
        else:
            return None

    def delete(self, key):
        if self.__redis.exists(key):
            return self.__redis.delete(key)
        else:
            return True
