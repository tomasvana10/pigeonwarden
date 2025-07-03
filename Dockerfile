FROM debian:bookworm

RUN apt update && apt install -y --no-install-recommends gnupg

RUN echo "deb http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E

RUN apt update && apt install -y --no-install-recommends \
    python3 python3-pip libglib2.0-0 ffmpeg libsm6 libxext6 \
    cmake libboost-dev libdrm-dev libexif-dev libpng-dev libtiff-dev \
    qtbase5-dev libjpeg-dev libcamera-dev python3-picamera2 \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY . .
