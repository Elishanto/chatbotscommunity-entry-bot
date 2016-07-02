from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler
import yaml
from handlers import Handlers
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(update_id)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

if __name__ == '__main__':
    try:
        config = yaml.load(open('config.yml', encoding='utf-8'))
    except FileNotFoundError:
        config = yaml.load(open('../config.yml', encoding='utf-8'))
    handlers = Handlers(config)
    updater = Updater(config['TELEGRAM_API_TOKEN'])
    updater.dispatcher.add_handler(CommandHandler('start', handlers.start))
    updater.dispatcher.add_handler(MessageHandler([Filters.text], handlers.message))
    updater.dispatcher.add_handler(CallbackQueryHandler(handlers.callback))

    updater.start_polling()
    updater.idle()
