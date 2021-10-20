import logging
import os
import time

import requests
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

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}


def get_api_answer(url, current_timestamp):
    """Отправляем запрос к серверу."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        url,
        headers=headers,
        params=payload
    )
    if homework_statuses.status_code != 200:
        raise Exception('Ошибка ответа сервера')
    logging.info('Server response')
    return homework_statuses.json()


def check_response(response):
    """
    Проверяем полученный ответ от сервера на корректность.
    Проверяем именение статуса.
    """
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise Exception('Нет такой домашней работы')
    for homework in homeworks:
        status = homework.get('status')
        if status in HOMEWORK_STATUSES.keys():
            return homeworks
        else:
            raise Exception('Нет такого статуса')
    return homeworks


def parse_status(homework):
    """При изменении статуса анализируем его."""
    verdict = HOMEWORK_STATUSES[homework.get('status')]
    homework_name = homework.get('homework_name')
    if homework_name is None:
        error_message = 'Homework_name doesnt exist'
        logging.error(error_message)
        return error_message
    if verdict is None:
        error_message = 'Verdict doesnt exist'
        logging.error(error_message)
        return error_message
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Отправляем сообщение."""
    logging.info(f'Message sent: {message}')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    """Цикл работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    url = ENDPOINT
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
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error('Failure')
            bot.send_message(chat_id=CHAT_ID, text=message)
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
