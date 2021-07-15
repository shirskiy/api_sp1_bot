import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
)
logger = logging.getLogger('main.log')

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

core_url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        elif homework_status == 'reviewing':
            verdict = 'Работа взята в ревью'
        elif homework_status == 'approved':
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        else:
            verdict = (f'Работе присвоен статус "{homework_status}".'
                       '\nОбратитесь к куратору, что бы уточнить ситуацию.')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as e:
        logger.info(f'error {e}')
        time.sleep(1)


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            core_url, headers=headers, params=payload)
    except ConnectionError as e:
        logger.info(f'error {e}')
        time.sleep(1)
    return homework_statuses.json()


def send_message(message):
    logger.info(f'отправка сообщения {message}')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            current_homework = get_homeworks(
                current_timestamp)['homeworks'][0]
            send_message(parse_homework_status(current_homework))
            time.sleep(5 * 60)

        except Exception as e:
            logger.info(f'error {e}')
            send_message(f'Бот упал с ошибкой: {str(e)}')
            exit()


if __name__ == '__main__':
    main()
