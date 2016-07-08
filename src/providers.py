from pymongo import MongoClient
from redis import StrictRedis
import threading
from random import shuffle
import logging


class Mongo:
    def __init__(self, db='cbc'):
        self.db = MongoClient()[db]

    def set_user_var(self, user_id, name, var):
        self.db.users.update_one({'user_id': user_id}, {'$set': {name: var}}, upsert=True)

    def unset_user_var(self, user_id, name):
        self.db.users.update_one({'user_id': user_id}, {'$unset': {name: 1}}, upsert=True)

    def get_user_var(self, user_id, name, default=None):
        user = self.db.users.find_one({'user_id': user_id})
        return user[name] if user and name in user else default

    def get_user_where(self, name, var):
        user = self.db.users.find_one({name: var})
        return user if user else None  # If matching user doesn't exist return None


class BaseDB:
    def __init__(self):
        pass

    def push_to_available(self, user_id):
        logging.info('Pushing {} to available...'.format(user_id), extra={'update_id': ''})

    def pop_first_available(self, self_user_id):
        pass

    def remove(self, user_id):
        logging.info('Removing {} from available...'.format(user_id), extra={'update_id': ''})

    def check_available(self):
        logging.info('Checking available queue...', extra={'update_id': ''})


class Redis(BaseDB):
    def __init__(self, host='localhost', port=6379, db=0):
        super().__init__()
        self.db = StrictRedis(host=host, port=port, db=db)
        self.available = False

    def push_to_available(self, user_id):
        self.db.sadd('available', user_id)  # Add user to awaiting queue
        self.check_available()

    def pop_first_available(self, self_user_id):
        while not self.available:
            threading.Event().wait()  # Prevent busy wait and CPU load

        res = [int(x) for x in self.db.smembers('available')]  # Get all available possible interlocutors
        shuffle(res)  # Randomize queue
        if self_user_id in res:  # User may be listed too
            res.remove(self_user_id)  # If so, remove him
        res = res.pop()  # Get random interlocutor
        self.check_available()
        return res

    def remove(self, user_id):
        self.db.srem('available', user_id)
        self.check_available()

    def check_available(self):
        self.available = True if self.db.scard('available') - 1 > 0 else False  # If there are more than 1 user in queue


class List(BaseDB):
    def __init__(self):
        super().__init__()
        self.db = list()
        self.available = False

    def push_to_available(self, user_id):
        self.db.append(user_id) if user_id not in self.db else None  # User may be already waiting for interlocutor
        self.db = list(set(self.db))  # Prevent duplicates
        self.check_available()

    def pop_first_available(self, self_user_id):
        while not self.available:
            threading.Event().wait()

        res = [int(x) for x in self.db]
        shuffle(res)
        if self_user_id in res:
            res.remove(self_user_id)
        res = res.pop()
        self.check_available()
        return res

    def remove(self, user_id):
        if user_id in self.db:
            self.db.remove(user_id)
        self.check_available()

    def check_available(self):
        self.available = True if len(self.db) - 1 > 0 else False
