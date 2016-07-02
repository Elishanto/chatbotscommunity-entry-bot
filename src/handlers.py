from util import handler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class Handlers:
    def __init__(self, config):
        self.config = config

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
    def callback(self, bot, update, ):
        query = update.callback_query
        chat_id = query.message.chat_id
        data = query.data

        if data in self.config['langs'].keys():
            # TODO: Add language to MongoDB
            bot.answerCallbackQuery(query.id)
            return {
                'chat_id': chat_id,
                'text': 'chosen_language',
                'button_text': 'find_interlocutor',
                'message_id': query.message.message_id
            }
