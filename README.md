Проект по парсингу 2ух сайтов.
---
* airforce-technology.com/news/
* aircosmosinternational.com/actualite/industry/

Установка и запуск.
---
`(Необходима версия питона не ниже 3.6)`
1. virtualenv --no-site-packages -p python3.6 venv
2. source venv/bin/activate
3. pip3 install -r requerments.txt
4. python3.6 parser.py
##
Результат работы программы можно увидеть в sqlite my_app.db, а также в папках media/images/*
