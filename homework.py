import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

# Настройка логов
logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
)
logger = logging.getLogger('main.log')
handler = RotatingFileHandler('main.log', maxBytes=33000, backupCount=1)
logger.addHandler(handler)

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status == 'rejected':
            verdict = 'К сожалению, в работе нашлись ошибки.'
        elif homework_status == 'reviewing':
            verdict = 'Работа взята в ревью'
        else:
            verdict = 'Ревьюеру всё понравилось, работа зачтена!'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as e:
        logging.exception(e, exc_info=True)
        time.sleep(1)


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except ConnectionError as e:
        logging.exception(e, exc_info=True)
        time.sleep(1)
    return homework_statuses.json()


def send_message(message):
    logging.info(f'отправка сообщения {message}')
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp

    while True:
        try:
            current_homework = get_homeworks(
                current_timestamp)['homeworks'][0]
            send_message(parse_homework_status(current_homework))
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logging.exception(e, exc_info=True)
            send_message(f'Бот упал с ошибкой: {str(e)}')
            print(f'Бот упал с ошибкой: {e}')
            exit() # Выход после ошибки, что бы не создавать спам от бота.


if __name__ == '__main__':
    main()
