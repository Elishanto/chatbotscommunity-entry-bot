from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler
import yaml
from handlers import Handlers
import logging

# Set logging format
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(update_id)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

if __name__ == '__main__':
    # Config file location may vary
    try:
        config = yaml.load(open('config.yml', encoding='utf-8'))
    except FileNotFoundError:
        config = yaml.load(open('../config.yml', encoding='utf-8'))
    handlers = Handlers(config)
    updater = Updater(config['TELEGRAM_API_TOKEN'])
    updater.dispatcher.add_handler(CommandHandler('start', handlers.start))
    # Filters for all types of incoming messages
    updater.dispatcher.add_handler(MessageHandler([
        Filters.audio, Filters.contact, Filters.document, Filters.location, Filters.photo,
        Filters.sticker, Filters.text, Filters.venue, Filters.video, Filters.voice
    ], handlers.message))
    updater.dispatcher.add_handler(CallbackQueryHandler(handlers.callback))

    updater.start_polling()
    updater.idle()
