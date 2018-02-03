from python:3.6.4-jessie

RUN mkdir /wedding-manager
COPY app /wedding-manager/app
COPY instance /wedding-manager/instance
COPY migrations /wedding-manager/migrations
COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt
WORKDIR /wedding-manager

ENTRYPOINT "gunicorn --bind 0.0.0.0:8000 run:app"
