from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Bot

from db_layer.db import db
from telegram_worker.settings import hurma_id, bot_token
from utils import Singleton
import time


class ScrapperTelegramBot(metaclass=Singleton):
    bot: Bot = Bot(token=bot_token)

    def _send_photo(self, data_id: str, img_link: str, chat_id: str = hurma_id):
        btn = InlineKeyboardButton(text='like', callback_data=data_id)
        markup = InlineKeyboardMarkup([[btn]])

        self.bot.send_photo(chat_id=chat_id,
                            photo=img_link,
                            reply_markup=markup)

    def _delimiter_decorator(func: callable):
        def decorate(self, *args, **kwargs):
            self.bot.sendMessage(chat_id=hurma_id,
                                 text='New images for approve')
            time.sleep(1.5)
            self.bot.sendMessage(chat_id=hurma_id,
                                 text='=================================')
            time.sleep(1.5)

            result = func(self, *args, **kwargs)

            time.sleep(1.5)
            self.bot.sendMessage(chat_id=hurma_id,
                                 text='=================================')
            return result
        return decorate

    @_delimiter_decorator
    def send_unprocessed_img_for_approve(self):
        unprocessed = db.select_processed_by_me(processed=False)

        i = 0
        for data in unprocessed:
            if i > 0:
                break

            data_id, link = data
            self._send_photo(data_id, link)
            time.sleep(1.5)
            i += 1


bot = ScrapperTelegramBot()
bot.send_unprocessed_img_for_approve()

