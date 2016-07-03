from pymongo import MongoClient
from redis import StrictRedis
import threading


class Mongo:
    def __init__(self, db='cbc'):
        self.db = MongoClient()[db]

    def set_user_var(self, user_id, name, var):
        self.db.users.update_one({'user_id': user_id}, {'$set': {name: var}}, upsert=True)

    def get_user_var(self, user_id, name, default):
        user = self.db.users.find_one({'user_id': user_id})
        return user[name] if user and name in user else default


class Redis:
    def __init__(self, host='localhost', port=6379, db=0):
        self.db = StrictRedis(host=host, port=port, db=db)
        self.available = False

    def push_to_available(self, user_id):
        self.db.sadd('available', user_id)
        self.available = True if self.db.scard('available') > 1 else False

    def pop_first_available(self):
        while not self.available:
            threading.Event().wait()

        res = self.db.spop('available')
        self.available = True if self.db.scard('available') > 1 else False
        return res

    def is_available(self, user_id):
        if not self.db.exists('available'):
            return False
        keys = self.db.smembers('available')
        keys = [x for x in keys if int(x) != user_id]
        return len(keys) > 0


class List:
    def __init__(self):
        self.db = list()
        self.available = False

    def push_to_available(self, user_id):
        self.db.append(user_id) if user_id not in self.db else None
        self.db = list(set(self.db))
        self.available = True if len(self.db) > 1 else False

    def pop_first_available(self):
        while not self.available:
            threading.Event().wait()

        res = self.db.pop()
        self.available = True if len(self.db) > 1 else False
        return res
