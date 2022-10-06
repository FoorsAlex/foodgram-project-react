# Проект доступен по адресу:
http://130.193.55.25/
# Стек технологий
Python Django Django REST Framework PostgreSQL Nginx gunicorn docker  Yandex.Cloud

# Описание проекта
Foodgram - «Продуктовый помощник»
С помощью этого онлайн сервиса люди могут делиться своими рецептами, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект использует базу данных PostgreSQL. Проект запускается в трёх контейнерах (nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) через docker-compose на сервере. Образ с проектом загружен на Docker Hub.

# Запуск проекта с помощью Docker
- Склонируйте репозиторий на локальную машину:
git clone git@github.com:FoorsAlex/foodgram-project-react.git
- Создайте .env файл в директории backend/foodgram/, в котором должны содержаться следующие переменные для подключения к базе PostgreSQL:

DB_ENGINE=django.db.backends.postgresql
DB_NAME=Имя вашей базы данных
POSTGRES_USER=username пользователя с доступом к базе данных
POSTGRES_PASSWORD=Пароль пользователя
DB_HOST=db
DB_PORT=5432
Перейдите в директорию infra/ и выполните команду для создания и запуска контейнеров.

sudo docker compose up -d 

В контейнере web выполните миграции, создайте суперпользователя и соберите статику.

sudo docker compose exec backend python manage.py makemigrations
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py createsuperuser
sudo docker compose exec backend python manage.py collectstatic --no-input 

Готово! Ниже представлены доступные адреса проекта:

http://ваш_ip/ - главная страница сайта;
http://ваш_ip/admin/ - админ панель;
http://ваш_ip/api/ - API проекта
http://ваш_ip/api/docs/redoc.html - документация к API

Автор
Шепилов Алексей - создание api, деплой на сервер.
