FROM python:3.7

WORKDIR /app

RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

ADD . /app

RUN pip install -r requirements/production.txt

EXPOSE 5000