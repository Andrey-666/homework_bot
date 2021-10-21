import logging
import os
import time

import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
from telegram import Bot

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filemode='a'
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('AUTH_TOKEN')

PRACTICUM_ENDPOINT = (
    'https://practicum.yandex.ru/api/user_api/homework_statuses/'
)

PRACTICUM_HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}

PRACTICUM_HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TELEGRAM_RETRY_TIME = 600


def get_api_answer(url, current_timestamp):
    """Отправляем запрос к серверу."""
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url,
            headers=PRACTICUM_HEADERS,
            params=payload
        )
        logging.info('Server response')
        if homework_statuses.status_code != 200:
            raise Exception('Error')
        return homework_statuses.json()
    except RequestException:
        logging.error('Invalid response')
        return 'Что-то пошло не так, попробуйте позже'


def check_response(response):
    """
    Проверяем полученный ответ от сервера на корректность.
    Проверяем именение статуса.
    """
    homeworks = response.get('homeworks')
    if not homeworks:
        raise Exception('Нет такой домашней работы')
    for homework in homeworks:
        status = homework.get('status')
        if status in PRACTICUM_HOMEWORK_STATUSES:
            return homework
        raise Exception('Нет такого статуса')
    return homeworks[0]


def parse_status(homework):
    """При изменении статуса анализируем его."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        error_message = 'Homework_name doesnt exist'
        logging.error(error_message)
        return error_message
    try:
        verdict = PRACTICUM_HOMEWORK_STATUSES[homework.get('status')]
    except KeyError:
        logging.error('No such dict key')
        return 'Ошибка в получении статуса'
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Отправляем сообщение."""
    try:
        logging.info(f'Message sent: {message}')
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except RequestException:
        logging.error('Telegram is down')
        return 'Ошибка на стороне мессенджера'


def main():
    """Цикл работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    url = PRACTICUM_ENDPOINT
    while True:
        logging.debug('Bot is running')
        try:
            response_result = check_response(
                get_api_answer(
                    url,
                    current_timestamp
                ))
            if response_result:
                for homework in response_result:
                    parsing = parse_status(homework)
                    send_message(bot, parsing)
            time.sleep(TELEGRAM_RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error('Failure')
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
            time.sleep(TELEGRAM_RETRY_TIME)


if __name__ == '__main__':
    main()
