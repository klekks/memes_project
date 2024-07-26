FROM python:3.10-slim

ADD server.py /media/
ADD storage.py /media/
ADD model.py /media/
ADD requirements.txt /media/

RUN pip install -r /media/requirements.txt

WORKDIR /media/
