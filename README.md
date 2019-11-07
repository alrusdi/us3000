# US3000

[![Build Status](https://travis-ci.org/mechanicalmachine/us3000.svg?branch=master)](https://travis-ci.org/mechanicalmachine/us3000)

Сервис для изучения английских слов.

How to deploy for development:
1) Clone/copy this repository
2) Make virtual environment: python3 -m venv env
3) Activate virtual environment: source env/bin/activate
4) Install development dependencies: python -m pip install -r requirements_dev.txt
5) Make your main/settings_local.py to override default settings (use main/settings_local.py.template as reference)
6) Make required directorie: mkdir -p logs media/od media/forvo media/sounds
7) Run tests to check if everything ok: python manage.py test 

TODO:
1. Добавить описания загрузки и сохранения словарных статей и произношений в БД
 
