FROM python:3.9.11

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install postgresql-client -y

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000
