FROM python:3.10-slim

ADD requirements.txt /media/

RUN pip install -r /media/requirements.txt

ADD server.py /media/
ADD storage.py /media/

WORKDIR /media/
