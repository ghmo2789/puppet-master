# syntax=docker/dockerfile:1

FROM python:3.11.0-bullseye

WORKDIR /control_server

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=src/router.py:init
CMD [ "python3", "-u", "-m" , "flask", "run", "--host=0.0.0.0"]