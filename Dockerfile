FROM debian:bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg wget python3 python3-pip libglib2.0-0 ffmpeg libsm6 libxext6 \
    cmake libboost-dev libdrm-dev libexif-dev libpng-dev libtiff-dev \
    qtbase5-dev libjpeg-dev libcamera-dev \
    && rm -rf /var/lib/apt/lists/*

# Add Raspberry Pi repo for python3-picamera2
RUN echo "deb http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E && \
    apt-get update && apt-get install -y --no-install-recommends python3-picamera2

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

EXPOSE 6969
