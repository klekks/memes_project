FROM tiangolo/uvicorn-gunicorn:python3.10-slim

ADD requirements.txt /media/

RUN pip install --upgrade pip
RUN pip install -r /media/requirements.txt

COPY . /media/

WORKDIR /media/
