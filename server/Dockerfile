FROM python:3.10-slim

ADD requirements.txt /server/

RUN pip install -r /server/requirements.txt

ADD server.py /server/
ADD model.py /server/
ADD media_connector.py /server/

WORKDIR /server/
