# Телеграм-бот футбольной статистики - FootballStats

С помощью данного бота можно просматривать статистику команд из ТОП-5 чемпионатов за последние 10 игр, узнать актуальные матчи предстоящего тура Лиги, узнать и сравнить статистику играющих команд и узнать их шансы на победу на основе последних 10-ти сыгранных матчей.

## Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)

## Выполняемые команды
/start - запускает бота, приветствие<br />
/matchday - вывод списка лиг -> вывод актуальных матчей -> вывод статистки команд выбранного матча<br />
/teams - вывод списка лиг -> вывод команд лиги -> вывод статистики выбранной команды<br />

## Запуск бота
Разверните и активируйте виртуально окружение
```
python -m venv venv
source venv/Scripts/ativate
```
Перейдите в папку с manage.py
```
cd backend
```
Чтобы запустить бота создана специальная команда для manage.py - runbot
```
python manage.py runbot
```
