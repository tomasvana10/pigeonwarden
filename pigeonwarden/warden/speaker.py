import vlc
import threading
import time


def _play_sound(soundfile: str, vol: int) -> None:
    instance = vlc.Instance('--aout=alsa')
    media = instance.media_new(soundfile)
    player = instance.media_player_new()
    player.set_media(media)
    player.audio_set_volume(vol)

    parsed_event = threading.Event()

    def on_parsed(event):
        parsed_event.set()

    media.event_manager().event_attach(
        vlc.EventType.MediaParsedChanged, 
        on_parsed
    )

    media.parse_async()
    parsed_event.wait(timeout=1)

    duration = media.get_duration() / 1000
    print(f"Duration: {duration} seconds")

    player.play()
    time.sleep(duration)


def play_sound(soundfile: str, vol: int) -> None:
    threading.Thread(target=lambda: _play_sound(soundfile, vol)).start()
