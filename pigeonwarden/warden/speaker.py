import time
import os
from threading import Event, Thread

import vlc

from .. import ASSETS_PATH

DEFAULT_ALSA_AUDIO_DEVICE = "2,0"

def _play_sound(soundfile: str, vol: int) -> None:
    instance = vlc.Instance(f"--aout=alsa --alsa-audio-device=hw:{os.getenv('ALSA_AUDIO_DEVICE', DEFAULT_ALSA_AUDIO_DEVICE)}")
    media = instance.media_new(ASSETS_PATH / "sound" / soundfile)
    player = instance.media_player_new()
    player.set_media(media)
    player.audio_set_volume(vol)

    on_media_parse = Event()
    media.event_manager().event_attach(
        vlc.EventType.MediaParsedChanged, lambda e: on_media_parse.set()
    )

    media.parse_async()
    on_media_parse.wait(timeout=1)

    duration = media.get_duration() / 1000

    player.play()
    time.sleep(duration)


def play_sound(soundfile: str, vol: int) -> None:
    Thread(target=lambda: _play_sound(soundfile, vol)).start()
