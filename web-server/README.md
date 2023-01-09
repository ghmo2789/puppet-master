## Requirements
To run the webserver you need to have python 3 installed. Navigate to the directory containing the requirements.txt file and install the required python packages by running
- pip install -r requirements.txt

## Starting the web server
First configure the .env file in the web-server/django-web-server directory by setting SECRET_KEY, CONTROL_SERVER_URL, CONTROL_SERVER_PREFIX and CONTROL_SERVER_AUTHORIZATION

Navigate to the django_web_server directory containing the manage.py file and run the following commands
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver

The web server is now running and the administrator user interface can be accessed in a web browser from the address http://127.0.0.1:8000/website/
