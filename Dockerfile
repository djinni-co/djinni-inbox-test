# Use an official Python runtime as a parent image
FROM python:3.9.11

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install postgresql-client -y

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

# Expose the port that the application will run on
EXPOSE 8000

# Start the application
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
