from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, CallbackQuery
import logging
import threading


def handler(func):
    """
    Every handler should have this decorator
    """
    def wrapper(*args, **kwargs):
        self = args[0]
        bot = args[1]
        update = args[2]
        update_or_query = args[2]
        # Update may be a callback query (it's tricky)
        if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
            update_or_query = update_or_query.callback_query
        # Logging query
        log_msg, log_args = 'Calling "%s" handler', [func.__name__]
        # Additional data needs to be logged too!
        if hasattr(update_or_query, 'data') and update_or_query.data:
            log_msg += ' with data "%s"'
            log_args.append(update_or_query.data.split(']['))
        elif 'args' in kwargs:
            log_msg += ' with data "%s"'
            log_args.append(kwargs['args'])
        elif hasattr(update_or_query.message, 'text') and update_or_query.message.text:
            log_msg += ' with text "%s"'
            log_args.append(update_or_query.message.text)
        logging.info(log_msg, *log_args, extra={'update_id': update.update_id})

        message = func(*args, **kwargs)  # Get decorated function return
        # Get user lang if exists
        if isinstance(update_or_query, Update):
            lang = self.mongo.get_user_var(update_or_query.message.from_user.id, 'lang', 'ru')
        elif isinstance(update_or_query, CallbackQuery):
            lang = self.mongo.get_user_var(update_or_query.from_user.id, 'lang', 'ru')
        else:  # Otherwise set lang to russian
            lang = 'ru'
        phrases = self.config['langs'][lang]

        if 'type' in message and message['type'] == 'text':  # If message is text
            if message['text'] in (
                        phrases['find_interlocutor'], phrases['change_interlocutor']
            ):  # If user wants to change/find interlocutor
                message['text'] = phrases['search_began']
                threading.Thread(target=start_search, args=(self, bot, update)).start()
            else:  # Otherwise send his message to interlocutor
                send_to_interlocutor(self, bot, update, message)
                return
        else:
            if 'text' in message and message['text'] in phrases:  # If message is a command
                text = message.pop('text')
                text = phrases[text]
                message['text'] = text
            if 'button_text' in message and message['button_text'] in phrases:  # If user contacts me first time
                button = message.pop('button_text')
                button = phrases[button]
                message['reply_markup'] = ReplyKeyboardMarkup([[KeyboardButton(button)]])
        res = bot.sendMessage(**message)
        return res

    return wrapper


def send_to_interlocutor(self, bot, update, message):
    user_id = update.message.from_user.id
    interlocutor = self.mongo.get_user_var(user_id, 'interlocutor')  # Get user's interlocutor from db
    if not interlocutor:
        return

    msg = message['message'].to_dict()
    # There are a lot of message types in telegram
    if 'audio' in msg and msg['audio']:
        bot.sendAudio(interlocutor, msg['audio']['file_id'])
    elif 'contact' in msg and msg['contact']:
        bot.sendContact(interlocutor, **msg['contact'])
    elif 'document' in msg and msg['document']:
        bot.sendDocument(interlocutor, msg['document']['file_id'])
    elif 'location' in msg and msg['location']:
        bot.sendLocation(interlocutor, msg['location']['latitude'], msg['location']['longitude'])
    elif 'photo' in msg and msg['photo']:
        for photo in msg['photo']:  # There are always a lot of photos, even if it is one (idk why, telegram???)
            bot.sendPhoto(interlocutor, photo['file_id'])
    elif 'sticker' in msg and msg['sticker']:
        bot.sendSticker(interlocutor, msg['sticker']['file_id'])
    elif 'text' in message and message['text']:
        bot.sendMessage(interlocutor, message['text'])
    elif 'venue' in msg and msg['venue']:
        venue = msg['venue']
        bot.sendVenue(interlocutor, venue['latitude'], venue['longitude'], venue['title'], venue['address'])
    elif 'video' in msg and msg['video']:
        bot.sendVideo(interlocutor, msg['video']['file_id'])
    elif 'voice' in msg and msg['voice']:
        bot.sendVoice(interlocutor, msg['voice']['file_id'])


def start_search(self, bot, update):
    user_id = update.message.from_user.id
    lang = self.mongo.get_user_var(user_id, 'lang', 'ru')  # Get user's lang from db

    interlocutor = self.mongo.get_user_where('interlocutor', user_id)  # Get user's interlocutor from db
    # Change interlocutor if exists
    if interlocutor:
        interlocutor_id = interlocutor['user_id']
        interlocutor_lang = self.mongo.get_user_var(interlocutor_id, 'lang', 'ru')
        self.mongo.unset_user_var(interlocutor_id, 'interlocutor')
        self.mongo.unset_user_var(user_id, 'interlocutor')
        self.available.remove(interlocutor_id)
        bot.sendMessage(
            interlocutor_id,
            text=self.config['langs'][interlocutor_lang]['connection_lost'],
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(self.config['langs'][interlocutor_lang]['find_interlocutor'])]]
            )
        )
    # Otherwise find new one
    self.available.push_to_available(user_id)

    interlocutor_id = int(self.available.pop_first_available(user_id))
    interlocutor_lang = self.mongo.get_user_var(interlocutor_id, 'lang', 'ru')

    self.mongo.set_user_var(interlocutor_id, 'interlocutor', user_id)  # Set interlocutor's interlocutor (user)
    self.mongo.set_user_var(user_id, 'interlocutor', interlocutor_id)  # Set user's interlocutor

    # Success!
    bot.sendMessage(update.message.chat_id,
                    text=self.config['langs'][lang]['found'],
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(self.config['langs'][lang]['change_interlocutor'])]]))
    bot.sendMessage(interlocutor_id,
                    text=self.config['langs'][interlocutor_lang]['found'],
                    reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(self.config['langs'][interlocutor_lang]['change_interlocutor'])]]))
