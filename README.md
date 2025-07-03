# pigeonwarden

Detect and scare pigeons

> [Link to model used](https://app.roboflow.com/tomasprojects/pigeon-myna-negchicken/1)

## Setup

### Initial preparation

1. Prepare your Raspberry Pi (install an OS, etc)
2. Clone the repo
3. Initialise a virtual environment and install the dependencies (`pip install -r requirements.txt`)
4. Plug in a speaker and camera to your Raspberry Pi
5. Create a Telegram bot and a chat for which pigeonwarden alerts will be sent to. Refer to [this website](https://core.telegram.org/bots/api) for guidance (or just ask AI). **NOTE**: Read the [final section](#extra-manually-configuring-the-warden) to see how this step can be avoided.
6. Create a `.env.local` file with the following contents:

```
BOT_TOKEN=your_telegram_bot_token (optional, see above)
CHAT_ID=your_telegram_chat_id (optional, see above)

USERNAME=John Smith
USERPASS=super_secret_password (hash with scripts/hash.py)

DEVICE_IP=(eg 192.168.1.105)
```

It is recommended that you reserve your Raspberry Pi's IP address on your LAN.

### Initialising YOLO11 object detection model

1. Load the dataset: `python -m pigeonwarden dataset`
2. Train the model: `python -m pigeonwarden train`
3. Export the model to NCNN format for better performance: `python -m pigeonwarden ncnn`

### Running with docker (recommended)

1. [Install docker](https://docs.docker.com/engine/install/)
2. Build the image: `docker compose build pigeonwarden-prod`
3. Run the container: `docker compose up -d pigeonwarden-prod`. This will also run the `redis` service for rate limiting.

### Running directly on your system

**NOTE**: This will require debugging and installation of various packages. If you run into errors, just copy and paste them into Google and StackOverflow will have the answers you need.

1. Run `python -m pigeonwarden dev/prod` (assuming your virtual environment is active with dependencies installed from [the first subsection of Setup](#initial-preparation)).

### Extra: manually configuring the Warden

Currently, the only way you can make changes to how the warden operates is directly in the source code. Here are the default values for the configurable settings:

```py
min_confidence = 0.8 # how confident the warden should to do it's job (0 = lowest, 1 = highest)
labels = ["common-mynas", "pigeons"] # labels to look out for
sound = "airhorn.mp3" # the default sound file to play. add a new one in assets/sound if you wish
volume = 150 # sound of alert
alert_cooldown_seconds = 10 # how long before another alert can be sent
fps = 1 # how often inference is performed on the camera's frame (which equals the framerate). do not increase this beyond 15 frames unless you are certain your PI will not die
telegram_alerts = True # whether you want to receive alerts on Telegram or not. if this setting is False, you do not need to provide the relevant values to .env.local
```

To modify these settings, follow these steps:

1. Open the server package file: `nano pigeonwarden/server/__init__.py` (or however you like)
2. Find this code,
```py
def _factory(dev: bool = False) -> Flask:
    ...
    warden = Warden(fps=4)

    # change to Warden(fps=5, telegram_alerts=False) for example
```
3. and simply add the settings you wish to override as keyword arguments.

## Required Hardware

- Raspberry Pi 4/4b/5 8GB+
- USB Speaker
- USB Camera
