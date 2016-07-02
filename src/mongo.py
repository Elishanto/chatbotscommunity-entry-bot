from pymongo import MongoClient


class Mongo:
    def __init__(self, db='cbc'):
        self.db = MongoClient()[db]

    def insert_user_lang(self, user_id, lang):
        self.db.users.update_one({'user_id': user_id}, {'$set': {'lang': lang}}, upsert=True)

    def get_user_lang(self, user_id):
        user = self.db.users.find_one({'user_id': user_id})

        return user['lang'] if user and 'lang' in user else 'ru'
