FROM tiangolo/uvicorn-gunicorn:python3.10-slim

ADD requirements.txt /server/

RUN pip install --upgrade pip
RUN pip install -r /server/requirements.txt

COPY . /server/

WORKDIR /server/
