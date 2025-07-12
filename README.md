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
> Read [Configuring the warden](#configuring-the-warden) to see how Step 5 can be disregarded.

1. Create a `.env.local` file with the following contents:

```
BOT_TOKEN=your_telegram_bot_token (optional, see above)
CHAT_ID=your_telegram_chat_id (optional, see above)
```

7. Add a user and secret key to `.env.local` for authentication:

```
python scripts/add_user.py <username> <password>
python scripts/add_secret.py
```

> [!NOTE]
> You can add as many users as you wish.

### Initialising YOLO11 object detection model

1. Fetch the dataset: `python -m pigeonwarden dataset`

2. Train the model: `python -m pigeonwarden train`

3. Export the model to NCNN format for better performance: `python -m pigeonwarden ncnn`

### Running with docker (recommended)

1. [Install docker](https://docs.docker.com/engine/install/)

2. Build and run the container: `docker compose up -d --build pigeonwarden-prod`.

### Running directly on your system

> [!WARNING]
> This will require debugging and installation of various packages. If you run into errors, just copy and paste them into Google and StackOverflow will have the answers you need.

1. For production, you will require `redis-server`. Run these commands to install it:

```sh
sudo apt update && sudo apt install redis-server
sudo systemctl enable --now redis-server
# Test it works:
redis-cli ping # Should return "PONG"
```

2. Run `python -m pigeonwarden dev/deploy` (assuming your virtual environment is active with dependencies installed from [the first subsection of Setup](#initial-preparation)).

### Configuring the warden

1. Open `warden.toml`

2. Add your new settings under `[user-override]`

3. Restart the program/container

### Debugging
1. If the speaker isn't playing sound, you may have to update your ALSA audio device:

   1. `sudo apt update && sudo apt install alsa-utils` (or enter the docker container which already has the package installed - `docker exec -it pigeonwarden-prod /bin/bash`)
   
   2. List your devices using `aplay -l`:

   ```
   **** List of PLAYBACK Hardware Devices ****
   ...
   
   card 2: UACDemoV10 [UACDemoV1.0], device 0: USB Audio [USB Audio]
   Subdevices: 1/1
   Subdevice #0: subdevice #0
   ```

   3. Using the output from above, the speaker is determined to be card `2` and device `0`.
   
   4. Add the following key to `.env.local`:
   
   ```
   ALSA_AUDIO_DEVICE='<card_number>,<device_number>' e.g. 2,0
   ```

## Hardware
### Required
- USB Speaker
- USB Camera
- Raspberry Pi Active Cooler

> [!NOTE]
> You can use an analogue speaker but it hasn't been tested. You will likely have to add a device mapping for `/dev/snd` to `compose.yaml`. 

### Minimum
- Raspberry Pi 4 4GB

### Recommended
- Raspberry Pi 5 8GB
