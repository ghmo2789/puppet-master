## Requirements
In requirements.txt

## Starting the web server
First configure the .env file by setting SECRET_KEY, CONTROL_SERVER_URL, CONTROL_SERVER_PREFIX and CONTROL_SERVER_AUTHORIZATION

Navigate to the django_web_server directory and run the commands
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver

If it's your first time running the program run 
- python manage.py migrate
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver

The website will be accessed from http://127.0.0.1:8000/website/