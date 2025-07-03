FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install libglib2.0-0 -y
# https://stackoverflow.com/a/63377623/24725311
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y 

COPY . .

EXPOSE 6969
