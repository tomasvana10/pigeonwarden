import time
from threading import Event, Thread

import vlc

from ..constants import ASSETS_PATH


def _play_sound(soundfile: str, vol: int) -> None:
    instance = vlc.Instance("--aout=alsa")
    media = instance.media_new(ASSETS_PATH / "sound" / soundfile)
    player = instance.media_player_new()
    player.set_media(media)
    player.audio_set_volume(vol)

    parsed_event = Event()
    media.event_manager().event_attach(
        vlc.EventType.MediaParsedChanged, lambda e: parsed_event.set()
    )

    media.parse_async()
    parsed_event.wait(timeout=1)

    duration = media.get_duration() / 1000

    player.play()
    time.sleep(duration)


def play_sound(soundfile: str, vol: int) -> None:
    Thread(target=lambda: _play_sound(soundfile, vol)).start()
