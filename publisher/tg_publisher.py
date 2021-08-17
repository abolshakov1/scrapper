from telegram import Bot

from db_layer.db import DbConnection
from publisher.settings import bot_token


class TgPublisher:

    bot: Bot = Bot(token=bot_token)
    _db = DbConnection()
    chat_ids = [

    ]
    cache: list = []

    def update_cache(self):
        for_publish = self._db.select_records_for_publish()
        self.cache.extend(for_publish)

    def publish(self):
        if len(self.cache) == 0:
            print('No cache for publish. Trying to fetch updates.')
            self.update_cache()

        data_id, link = self.cache.pop()
        if not data_id or not link:
            print('Still no data for publish')
            return

        print (f'Publish {data_id} {link}')
        for id_ in self.chat_ids:
            self.bot.send_photo(chat_id=id_,
                                photo=link)

        self._db.update_processed_by_bot(data_id)
