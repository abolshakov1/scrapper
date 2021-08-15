from apscheduler.job import Job
from flask import Flask

from flask_apscheduler import APScheduler

from app_logger import logger
from scrappers.dtf.dtf import DtfScrapper
from telegram_worker.sender import ScrapperTelegramBot
from telegram_worker.worker import TelegramWorker

from threading import Thread

dtf_scrap_schedule_timer = 1800
approve_schedule_timer = 1000

app = Flask(__name__)
scheduler = APScheduler()

dft_scrapper = DtfScrapper()
telegram_sender_bot = ScrapperTelegramBot()


@app.route("/")
def index():
    return "<p>I'm scrapper app</p>"


@app.route('/start_t_worker')
def start_t_worker():
    logger.info('Telegram worker starts')
    thread = Thread(target=TelegramWorker.start, args=[scheduler])
    thread.daemon = True
    thread.start()

    return "Thread with telegram worker started"


@app.route('/sender_status')
def sender_status():
    job: Job = scheduler.get_job('Telegram sender task')
    job_dead = job is None

    logger.info('--------------------------------')
    logger.info('     Telegram sender status: ')
    logger.info(f'        Job status: {not job_dead}')
    logger.info(f'        Telegram bot status: {telegram_sender_bot.ping()}')
    logger.info(f'        Next job run time: {job.next_run_time}')
    logger.info('--------------------------------')

    return ''


def schedule_scrapping():
    logger.info('Scheduled scrapping task')
    scheduler.add_job(id='Scrapping task',
                      func=dft_scrapper.scrap_best_pages,
                      trigger='interval',
                      seconds=dtf_scrap_schedule_timer)


def schedule_telegram_sender():
    logger.info('Scheduled telegram sender task')
    scheduler.add_job(id='Telegram sender task',
                      func=telegram_sender_bot.send_unprocessed_img_for_approve,
                      trigger='interval',
                      seconds=approve_schedule_timer)


if __name__ == '__main__':
    logger.info('Scrapper app start working')

    # schedule_scrapping()
    schedule_telegram_sender()

    scheduler.start()
    start_t_worker()

    app.run(host='0.0.0.0', port=8080)

