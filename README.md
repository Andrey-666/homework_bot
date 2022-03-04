# Homework_bot
Телеграм бот, делающий запрос к API каждые 10 минут для оповещения о статусе домашнего задания.

## Стек технологий:

- Python 3
- python-telegram-bot

## Как запустить проект:
- Клонируйте репозиторий:  
```git clone https://github.com/Andrey-666/homework_bot.git```
- Перейдите в директорию с проектом
- Создайте виртуальное окружение:  
```python -m venv venv```
- Активируйте виртуальное окружение:  
для windows: ```source venv/Scripts/activate```  
для linux: ```source venv/bin/activate```
- Установите зависимости:  
```pip install -r requirements.txt```
- Создайте файл *.env*, в котором укажите переменную окружения *SECRET_KEY*, а так же укажите следующие значения:
```PRACTICUM_TOKEN = <Токен на Яндекс.Практикум>```
```TELEGRAM_TOKEN = <Токен телеграм бота>```
```TELEGRAM_CHAT_ID = <ID чата, в который будут приходить оповещения>```


***
## Об авторе  
Кузнецов Андрей    
<andrey.66677@yandex.ru>
