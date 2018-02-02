from python:3.6.4-jessie

COPY csv_manager /csv_manager
COPY sms_sender /sms_sender

RUN cd /csv_manager && pip install --editable . && cd /sms_sender && pip install --editable .