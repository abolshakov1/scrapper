import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Bot, chat

import app_logger
from db_layer.db import DbConnection
from telegram_worker.settings import hurma_id, bot_token
from utils import Singleton
import time


class ScrapperTelegramBot(metaclass=Singleton):
    bot: Bot = Bot(token=bot_token)
    db = DbConnection()

    _logger = app_logger.bot_sender_logger

    def _send_photo(self, data_id: str, img_link: str, chat_id: str = hurma_id):
        btn = InlineKeyboardButton(text='like', callback_data=data_id)
        markup = InlineKeyboardMarkup([[btn]])
        self._logger.debug(f'Send photo to chat {chat_id}, data_id={data_id}, img_link={img_link}')

        self.bot.send_photo(chat_id=chat_id,
                            photo=img_link,
                            reply_markup=markup)

    def _delimiter_decorator(func: callable):
        def decorate(self, *args, **kwargs):
            self.bot.sendMessage(chat_id=hurma_id,
                                 text='New images for approve')
            time.sleep(1)
            self.bot.sendMessage(chat_id=hurma_id,
                                 text='=================================')
            time.sleep(1)

            result = func(self, *args, **kwargs)

            time.sleep(1)
            self.bot.sendMessage(chat_id=hurma_id,
                                 text='=================================')
            return result
        return decorate

    @_delimiter_decorator
    def send_unprocessed_img_for_approve(self, limiter=1):
        self.db.open_connection()
        unprocessed = self.db.select_unprocessed_and_unsent()

        sent = []

        try:
            if len(unprocessed) == 0:
                self.bot.send_message(
                    chat_id=hurma_id,
                    text="No unprocessed images"
                )

            i = 0
            for data in unprocessed:
                if limiter and i >= limiter:
                    break

                data_id, link = data
                self._send_photo(data_id, link)
                time.sleep(1.5)
                i += 1
                sent.append((int(data_id), ))

            self.db.update_sent(sent)
        except Exception as exc:
            self._logger.error("Some error on send unprocessed images ", exc)
        finally:
            self.db.close_connection()

    def ping(self):
        return 'pong'


if __name__ == "__main__":
    bot = ScrapperTelegramBot()
    bot.send_unprocessed_img_for_approve()

