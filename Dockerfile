FROM python:3.10.13-slim-bullseye

COPY . /project/

WORKDIR /project

RUN pip install -r requirements.txt
RUN pip install wheel gunicorn


CMD gunicorn --bind 0.0.0.0:5000 -w 3 wsgi:app
