FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    # need this for some other problem
    libglib2.0-0 \

    # https://stackoverflow.com/a/63377623/24725311
    ffmpeg \
    libsm6 \
    libxext6 \

    # camera support
    python3-picamera2

COPY . .

EXPOSE 6969
