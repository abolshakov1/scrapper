import datetime

from dataclasses import dataclass

from flask_apscheduler import APScheduler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, Updater, CallbackQueryHandler

from db_layer.db import DbConnection
from telegram_worker.settings import bot_token
from utils import Singleton


@dataclass
class CacheObject:
    data_id: str = None
    timeout: datetime.datetime = None
    approved: bool = None

    @property
    def is_expired(self):
        return self.timeout < datetime.datetime.now()


class TelegramWorker(metaclass=Singleton):

    cache: dict = {int: CacheObject}
    cache_timeout = 10
    db = DbConnection()
    scheduler: APScheduler = None

    def __init__(self, scheduler: APScheduler):
        self.scheduler = scheduler

    @classmethod
    def start(cls, scheduler: APScheduler):
        instance = TelegramWorker(scheduler)
        instance._start()

    def _start(self):
        print ('Telegram worker start polling')
        updater = Updater(bot_token)
        updater.dispatcher.add_handler(CallbackQueryHandler(self.callback_handler))
        updater.start_polling()

        # updater.idle()

    def callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        data_id = query.data

        updated = self._update_cache(data_id)

        self._update_markup(query, context, data_id, updated)

    def _update_markup(self, query, context, data_id, updated):
        if updated:
            text = 'Approved'
            cached_object: CacheObject = self.cache.get(data_id)
            if cached_object and not cached_object.approved:
                text = 'Unapproved'
        else:
            # todo: remove markup
            text = ''

        btn = InlineKeyboardButton(text=text, callback_data=data_id)
        markup = InlineKeyboardMarkup([[btn]])

        bot = context.bot
        bot.edit_message_reply_markup(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=markup,
        )

    def process_cache_object(self, data_id):

        cache_object: CacheObject = self.cache.pop(data_id, None)
        if not cache_object:
            print(f'Something went wrong and cache object with id {data_id} was deleted before processing')
            # todo: remove markup?
            return

        print(f'Process cache object on timeout with data_id={data_id}, approved={cache_object.approved}')

        self.db.open_connection()
        self.db.update_processed_by_me([(cache_object.approved, int(data_id))])
        self.db.close_connection()

        self.scheduler.remove_job(data_id)
        # todo: remove markup for disable approve

    def _schedule_process_task(self, cache_object: CacheObject):
        self.scheduler.add_job(id=cache_object.data_id,
                               func=self.process_cache_object,
                               args=[cache_object.data_id],
                               next_run_time=cache_object.timeout)

    def _update_cache(self, data_id: str):
        if data_id not in self.cache:
            timeout = datetime.datetime.now() + datetime.timedelta(seconds=self.cache_timeout)
            cache_object = CacheObject(data_id, timeout, True)
            self.cache[data_id] = cache_object
            self._schedule_process_task(cache_object)

            print(f'Img with data_id={data_id} was approved')
        else:
            cache_object: CacheObject = self.cache[data_id]
            if cache_object.is_expired:
                return False

            cache_object.approved = False
            print(f'Img with data_id={data_id} was unapproved')

        return True


if __name__ == "__main__":
    worker = TelegramWorker()
