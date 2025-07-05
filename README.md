# pigeonwarden

Detect and scare pigeons

> [Link to model used](https://app.roboflow.com/tomasprojects/pigeon-myna-negchicken/1)

## Setup

### Initial preparation

1. Prepare your Raspberry Pi (install an OS, etc)
2. Clone the repo
3. Initialise a virtual environment and install the dependencies (`pip install -r requirements.txt`)
4. Plug in a speaker and camera to your Raspberry Pi
5. Create a Telegram bot and a chat for which pigeonwarden alerts will be sent to. Refer to [this website](https://core.telegram.org/bots/api) for guidance (or just ask AI). 
> [!NOTE]
> Read [Configuring the warden](#extra-manually-configuring-the-warden) to see how Step 5 can be disregarded.
6. Create a `.env.local` file with the following contents:

```
BOT_TOKEN=your_telegram_bot_token (optional, see above)
CHAT_ID=your_telegram_chat_id (optional, see above)

USERNAME=John Smith
USERPASS=super_secret_password (hash with scripts/hash.py)

DEVICE_IP=eg. 192.168.1.105
```

It is recommended that you reserve your Raspberry Pi's IP address on your LAN, as if it changes you will have to modify `.env.local`.

### Initialising YOLO11 object detection model

1. Fetch the dataset: `python -m pigeonwarden dataset`
2. Train the model: `python -m pigeonwarden train`
3. Export the model to NCNN format for better performance: `python -m pigeonwarden ncnn`

### Running with docker (recommended)

1. [Install docker](https://docs.docker.com/engine/install/)
2. Build the image: `docker compose build pigeonwarden-prod`
3. Run the container: `docker compose up -d pigeonwarden-prod`. This will also run the `redis-server` service.

### Running directly on your system


> [!WARNING]
> This will require debugging and installation of various packages. If you run into errors, just copy and paste them into Google and StackOverflow will have the answers you need.

1. For production, you will require `redis-server`. Run these commands to install it:
   ```sh
   sudo apt update
   sudo apt install redis-server
   sudo systemctl enable --now redis-server
   # Test it works:
   redis-cli ping # Should return "PONG"
   ```
2. Run `python -m pigeonwarden dev/deploy` (assuming your virtual environment is active with dependencies installed from [the first subsection of Setup](#initial-preparation)).

### Configuring the warden

1. Open `warden.toml`
2. Add your new settings under `[user-override]`
3. Restart the program/container

## Required Hardware

- Raspberry Pi 4/4b/5 8GB+
- USB Speaker
- USB Camera
