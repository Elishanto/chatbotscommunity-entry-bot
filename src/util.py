def handler(func):
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    import logging

    def wrapper(*args, **kwargs):
        self = args[0]
        bot = args[1]
        update = args[2]
        update_or_query = args[2]
        if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
            update_or_query = update_or_query.callback_query
        # logging query
        log_msg, log_args = 'Calling "%s"', [func.__name__]
        # additional data needs to be logged too!
        if hasattr(update_or_query, 'data') and update_or_query.data:
            log_msg += ' with data "%s"'
            log_args.append(update_or_query.data.split(']['))
        elif 'args' in kwargs:
            log_msg += ' with data "%s"'
            log_args.append(kwargs['args'])
        logging.info(log_msg, *log_args, extra={'update_id': update.update_id})

        config = self.config
        message = func(*args, **kwargs)

        lang = self.mongo.get_user_lang(update_or_query.message.from_user.id)
        if 'text' in message and message['text'] in config['langs'][lang]:
            text = message.pop('text')
            text = config['langs'][lang][text]
            message['text'] = text
        if 'button_text' in message and message['button_text'] in config['langs'][lang]:
            button = message.pop('button_text')
            button = config['langs'][lang][button]
            message['reply_markup'] = ReplyKeyboardMarkup([[KeyboardButton(button)]])
        res = bot.sendMessage(**message)
        return res

    return wrapper
