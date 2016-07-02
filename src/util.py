def handler(func):
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    import logging

    def wrapper(*args, **kwargs):
        # logging query
        log_msg, log_args = 'Calling "%s"', [func.__name__]
        # additional data needs to be logged too!
        if hasattr(args[2], 'callback_query') and args[2].callback_query:
            log_msg += ' with data "%s"'
            log_args.append(args[2].callback_query.data.split(']['))
        elif 'args' in kwargs:
            log_msg += ' with data "%s"'
            log_args.append(kwargs['args'])
        logging.info(log_msg, *log_args, extra={'update_id': args[2].update_id})

        # TODO: Get language from MongoDB
        lang = 'ru'

        config = args[0].config
        message = func(*args, **kwargs)
        if 'text' in message and message['text'] in config['langs'][lang]:
            text = message.pop('text')
            text = config['langs'][lang][text]
            message['text'] = text
        if 'button_text' in message and message['button_text'] in config['langs'][lang]:
            button = message.pop('button_text')
            button = config['langs'][lang][button]
            message['reply_markup'] = ReplyKeyboardMarkup([[KeyboardButton(button)]])
        res = args[1].sendMessage(**message)
        return res

    return wrapper
