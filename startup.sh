#!/bin/bash
cd /home/site/wwwroot
pip install -r requirements.txt
cd backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput
cd ..
gunicorn --bind=0.0.0.0 --workers=4 --timeout=60 backend.azurelab.wsgi:application
