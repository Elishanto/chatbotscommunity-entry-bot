# @CBCEntryBot
> Telegram bot

## Install

Install dependencies with pip

```sh
$ pip install -r requirements.txt
```

Rename config.example.yml to config.yml

```sh
$ mv config.example.yml config.yml
```

Add API keys and choose db in config.yml
```
TELEGRAM_API_TOKEN: TELEGRAM_API_TOKEN
db: redis OR list
```

If you've chosen `redis` as db you need to install&run redis-server.

Also you need to [install MongoDB](https://www.mongodb.com/download-center?jmp=nav#community) to store user data.

## Contributing

Pull requests and stars are always welcome. For bugs and feature requests, [please create an issue](https://github.com/elishanto/chatbotscommunity-entry-bot/issues)

## Author

**Alexey Shekhirin**

* [github/elishanto](https://github.com/elishanto)
* [vk/elishanto](http://vk.com/elishanto)

## License

Copyright © 2016 [Alexey Shekhirin](https://github.com/elishanto)
Licensed under the Apache License.
