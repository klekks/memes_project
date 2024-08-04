FROM python:3.10-slim

ADD requirements.txt /server/

RUN pip install -r /server/requirements.txt

COPY *.py /server/

WORKDIR /server/
