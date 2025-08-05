#!/bin/bash

python manage.py migrate
python manage.py collectstatic --no-input

python manage.py mqtt_listener &

gunicorn backend_task.wsgi:application --bind 0.0.0.0:$PORT
