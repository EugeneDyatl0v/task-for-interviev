FROM python:3.12

ENV PYTHONPATH=/app

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade -r /app/requirements.txt

COPY ./ /app/

WORKDIR /app/sql_task
