
FROM python:3.8.6-slim-buster

ARG GUNICORN_CMD_ARGS

ENV PYTHONPATH=/app/\
    PYTHONUNBUFFERED=1\
    GUNICORN_CMD_ARGS="--workers 4 -b 0.0.0.0:80 --timeout 30"

RUN apt-get -y update && apt-get -y install git && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man/?? /usr/share/man/??_*

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

EXPOSE 80

CMD gunicorn scrummasterjr.app:flask_app
