# Описание

Парсер собирает данные обо всех PEP документах, сравнивает статусы и записывает их в файл. Также реализован сбор информации о статусе версий Python и скачивание архива с документацией.

## Стек технологий

* Python 3.10
* BeautifulSoup4
* Prettytable

## Запуск парсера

1. Клонируйте репозиторий:  
`git clone https://github.com/sheremet-o/bs4_parser_pep`
2. Создайте и активируйте виртуальное окружение:  
`python -m venv .env`  
`source .env/Scripts/activate`  
3. Установите зависимости:  
`pip install -r requirements.txt`

## Примеры комманд  

1. Создание csv файла с таблицей текущих статусов PEP:
`python main.py pep -o file`  
2. Создание таблицы с информацией по версиям Python с указанием статуса и ссылками на документацию:  
`python main.py latest-versions -o pretty`
