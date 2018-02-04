from python:3.6.4-jessie

RUN mkdir /wedding-manager
COPY app /wedding-manager/app
COPY instance /wedding-manager/instance
COPY migrations /wedding-manager/migrations
COPY requirements.txt /requirements.txt
COPY run.py /wedding-manager/run.py
COPY manage.py /wedding-manager/manager.py
COPY docker_entrypoint.sh /wedding-manager/docker_entrypoint.sh

RUN pip install -r /requirements.txt && chmod +x /wedding-manager/docker_entrypoint.sh && rm /requirements.txt

WORKDIR /wedding-manager

ENTRYPOINT "docker_entrypoint.sh"
