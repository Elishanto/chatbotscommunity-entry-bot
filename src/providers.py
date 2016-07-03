from pymongo import MongoClient
from redis import StrictRedis


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

    def push_to_available(self, user_id):
        self.db.sadd('available', user_id)

    def pop_first_available(self, ban):
        while not self.is_available(ban):
            continue
        return self.db.spop('available')

    def is_available(self, user_id):
        if not self.db.exists('available'):
            return False
        keys = self.db.smembers('available')
        keys = [x for x in keys if int(x) != user_id]
        return len(keys) > 0


class List:
    def __init__(self):
        self.db = list()

    def push_to_available(self, user_id):
        self.db.append(user_id) if user_id not in self.db else None

    def pop_first_available(self, ban):
        while not self.is_available(ban):
            continue
        return self.db.pop()

    def is_available(self, user_id):
        keys = [x for x in self.db if int(x) != user_id]
        return len(keys) > 0
