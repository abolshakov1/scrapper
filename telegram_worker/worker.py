import datetime

import celery

from dataclasses import dataclass

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, Updater, CallbackQueryHandler

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

    cache: dict = {}
    cache_timeout = 5

    def __init__(self):
        updater = Updater(bot_token)
        updater.dispatcher.add_handler(CallbackQueryHandler(self.callback_handler))
        updater.start_polling()

        updater.idle()

    def callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        data_id = query.data

        updated = self.update_cache(data_id, context)

        if updated: # else remove markup
            self.update_markup(query, context, data_id)

    def update_markup(self, query, context, data_id):
        text = 'Approved'
        cached_object: CacheObject = self.cache.get(data_id)
        if cached_object and not cached_object.approved:
            text = 'Unapproved'

        btn = InlineKeyboardButton(text=text, callback_data=data_id)
        markup = InlineKeyboardMarkup([[btn]])

        bot = context.bot
        bot.edit_message_reply_markup(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=markup,
        )

    def process_cache_object(self, context: CallbackContext):
        print('Process cache object on timeout')

    # def remove_markup_on_timeout(self):
    #     pass

    def update_cache(self, data_id: str, context: CallbackContext):
        if data_id not in self.cache:
            timeout = datetime.datetime.now() + datetime.timedelta(seconds=self.cache_timeout)
            cache_object = CacheObject(data_id, timeout, True)
            self.cache[data_id] = cache_object

            print(timeout)
            context.job_queue.run_once(self.process_cache_object,
                                       timeout, context=context,
                                       name=str(data_id))

            print(f'Img with data_id={data_id} was approved')
        else:
            cache_object: CacheObject = self.cache[data_id]
            # if cache_object.is_expired:
            #     return False

            cache_object.approved = False
            print(f'Img with data_id={data_id} was unapproved')

        return True


if __name__ == "__main__":
    worker = TelegramWorker()
