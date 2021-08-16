from telegram import Bot

from db_layer.db import DbConnection


class TgPublisher:

    bot_token = '1903625927:AAEksNDK1GupjYl_LOPI-kd0aaWyfxSIOv0'

    bot: Bot = Bot(token=bot_token)
    _interval: int = 3600
    _db = DbConnection()
    chat_ids = [

    ]
    cache: list = []

    def update_cache(self):
        for_publish = self._db.select_records_for_publish()
        self.cache.extend(for_publish)

    def publish(self):
        if len(self.cache) == 0:
            print ('Not cache for publish. Trying to fetch updates.')
            self.update_cache()

        data_id, link = self.cache.pop()
        if not data_id or not link:
            print('Still no data for publish')

        for id_ in self.chat_ids:
            self.bot.send_photo(chat_id=id_,
                                photo=link)



