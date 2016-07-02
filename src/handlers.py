from util import handler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from mongo import Mongo


class Handlers:
    def __init__(self, config):
        self.config = config
        self.mongo = Mongo()

    @handler
    def start(self, bot, update):
        chat_id = update.message.chat_id
        return {
            'chat_id': chat_id,
            'text': 'Choose language',
            'reply_markup': InlineKeyboardMarkup([[
                InlineKeyboardButton('Русский', callback_data='ru'),
                InlineKeyboardButton('English', callback_data='en')
            ]])
        }

    @handler
    def callback(self, bot, update):
        query = update.callback_query
        chat_id = query.message.chat_id
        data = query.data
        bot.answerCallbackQuery(query.id)

        if data in self.config['langs'].keys():
            self.mongo.insert_user_lang(query.message.from_user.id, data)
            return {
                'chat_id': chat_id,
                'text': 'selected_language',
                'button_text': 'find_interlocutor',
                'message_id': query.message.message_id
            }

    @handler
    def message(self, bot, update):
        text = update.message.text
