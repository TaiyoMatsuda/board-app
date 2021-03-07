# tourist guide board
This application enables you to organize and join events.

# Description
This application is based on Single Page Application model by Django REST framework and Vue.js.

# Requirement
- Ubuntu 20.04.1 LTS
- Docker 20.10.1
- docker-compose 1.25.0
- mysql 5.7
- nginx 1.17.8
- python 3.8.1
- Django 3.0.8
- djangorestframework 3.11.0
- django-environ 0.4.5
- django-filter 2.4.0
- django-rest-auth 0.9.5
- django-allauth 0.44.0
- django-cors-headers 3.7.0
- mysqlclient 2.0.1
- uwsgi 2.0.18
- flake8 3.7.9
- pillow 7.1.0
- isort 5.7.0
- factory-boy 3.2.0
- drf-spectacular 0.13.2
- pytest-django 3.10.0
- tox 3.14.3
- npm 6.14.10
- Vue 2.6.12
- VueCli 4.5.10

# Usage
## run backend
$docker-compose up

## migration
$make makemigrations
$make migrate

## make demo data
$make loaddata

## test
$make tox

## run frontend
$npm run serve 

# Install
$ git clone https://github.com/TaiyoMatsuda/board-app.git
