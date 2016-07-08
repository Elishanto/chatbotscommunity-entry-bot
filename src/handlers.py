from util import handler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from providers import Mongo, Redis, List


class Handlers:
    def __init__(self, config):
        self.config = config
        self.mongo = Mongo()

        # Choose db source based on config
        if self.config['db'] == 'redis':
            self.available = Redis()
        else:
            self.available = List()

    @handler
    def start(self, bot, update):
        chat_id = update.message.chat_id
        # Language choosing
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

        # If callback is language choosing
        if data in self.config['langs'].keys():
            self.mongo.set_user_var(query.from_user.id, 'lang', data)
            return {
                'chat_id': chat_id,
                'text': 'selected_language',
                'button_text': 'find_interlocutor',
                'message_id': query.message.message_id
            }

    @handler
    def message(self, bot, update):
        message = update.message
        chat_id = message.chat_id
        text = message.text

        return {
            'chat_id': chat_id,
            'text': text,
            'type': 'text',
            'message': message
        }
