release: python manage.py migrate
web: gunicorn tango_with _django_project/wsgi.py --log-file -
web: python manage.py runserver 0.0.0.0:$PORT --noreload
