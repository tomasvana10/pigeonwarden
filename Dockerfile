FROM debian:bookworm

# Install basic tools and GPG for adding RPi repo
RUN apt update && apt install -y --no-install-recommends gnupg wget

# Add Raspberry Pi repository for picamera2
RUN echo "deb http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E

RUN apt update && apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    libglib2.0-0 \
    ffmpeg \
    libsm6 \
    libxext6 \
    python3-picamera2 && \
    apt-get clean && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6969
