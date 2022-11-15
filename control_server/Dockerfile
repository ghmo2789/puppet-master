# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /control_server

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=src/router.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]