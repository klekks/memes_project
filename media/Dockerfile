FROM python:3.10-slim

ADD requirements.txt /media/

RUN pip install --upgrade pip
RUN pip install -r /media/requirements.txt

ADD server.py /media/
ADD storage.py /media/
ADD settings.py /media/
ADD validators.py /media/
ADD responses.py /media/

WORKDIR /media/
