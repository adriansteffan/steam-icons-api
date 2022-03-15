FROM python:3.7-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN python steamicons/updateicons.py