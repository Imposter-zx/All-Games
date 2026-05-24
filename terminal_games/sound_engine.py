"""
Waveform-based sound engine for Retro Terminal Arcade.
Replaces simple \a beeps with synthesized waveform audio.
Supports sound effects and background music.
"""

import logging
import math
import os
import struct
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional

from stats_manager import get_stats_manager

logger = logging.getLogger(__name__)

SAMPLE_RATE = 44100
MAX_AMPLITUDE = 32767  # 16-bit signed

# Cache for generated waveforms
_wave_cache: Dict[str, bytes] = {}


def _generate_sine_wave(freq: float, duration: float, volume: float = 0.3) -> bytes:
    """Generate a sine wave as 16-bit PCM bytes."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Apply envelope (fade in/out to avoid clicks)
        envelope = 1.0
        fade_len = int(SAMPLE_RATE * 0.005)
        if i < fade_len:
            envelope = i / fade_len
        elif i > num_samples - fade_len:
            envelope = (num_samples - i) / fade_len
        value = int(MAX_AMPLITUDE * volume * envelope * math.sin(2 * math.pi * freq * t))
        samples.append(value)
    return struct.pack(f'<{len(samples)}h', *samples)


def _generate_square_wave(freq: float, duration: float, volume: float = 0.2) -> bytes:
    """Generate a square wave."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    period = SAMPLE_RATE / freq
    for i in range(num_samples):
        envelope = 1.0
        fade_len = int(SAMPLE_RATE * 0.003)
        if i < fade_len:
            envelope = i / fade_len
        elif i > num_samples - fade_len:
            envelope = (num_samples - i) / fade_len
        value = int(MAX_AMPLITUDE * volume * envelope * (1 if (i % period < period / 2) else -1))
        samples.append(value)
    return struct.pack(f'<{len(samples)}h', *samples)


def _generate_noise(duration: float, volume: float = 0.15) -> bytes:
    """Generate white noise."""
    import random
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        envelope = 1.0
        fade_len = int(SAMPLE_RATE * 0.003)
        if i < fade_len:
            envelope = i / fade_len
        elif i > num_samples - fade_len:
            envelope = (num_samples - i) / fade_len
        value = int(MAX_AMPLITUDE * volume * envelope * random.uniform(-1, 1))
        samples.append(value)
    return struct.pack(f'<{len(samples)}h', *samples)


def _build_wav(data: bytes) -> bytes:
    """Wrap raw PCM data in a WAV container."""
    data_size = len(data)
    file_size = 36 + data_size
    buf = bytearray()
    # RIFF header
    buf += b'RIFF'
    buf += struct.pack('<I', file_size)
    buf += b'WAVE'
    # fmt chunk
    buf += b'fmt '
    buf += struct.pack('<I', 16)          # chunk size
    buf += struct.pack('<H', 1)            # PCM format
    buf += struct.pack('<H', 1)            # mono
    buf += struct.pack('<I', SAMPLE_RATE)  # sample rate
    buf += struct.pack('<I', SAMPLE_RATE * 2)  # byte rate
    buf += struct.pack('<H', 2)            # block align
    buf += struct.pack('<H', 16)           # bits per sample
    # data chunk
    buf += b'data'
    buf += struct.pack('<I', data_size)
    buf += data
    return bytes(buf)


def _get_wav(event: str) -> Optional[bytes]:
    """Generate or retrieve cached WAV data for a sound event."""
    if event in _wave_cache:
        return _wave_cache[event]

    params = {
        'move':       (220, 0.05, 0.15),
        'correct':    (440, 0.08, 0.2),
        'eat':        (660, 0.1, 0.25),
        'invalid':    (150, 0.15, 0.2),
        'win':        (880, 0.3, 0.3),
        'lose':       (200, 0.4, 0.25),
        'game_over':  (120, 0.5, 0.25),
        'achievement':(523, 0.15, 0.3),
        'level_up':   (1047, 0.2, 0.3),
    }

    if event == 'achievement':
        # Rising three-note chime
        data = b''
        for freq in (523, 659, 784):
            data += _generate_sine_wave(freq, 0.12, 0.3)
            data += _generate_sine_wave(freq, 0.12, 0.3)
        _wave_cache[event] = _build_wav(data)
    elif event == 'level_up':
        data = _generate_sine_wave(1047, 0.08, 0.3) * 3
        _wave_cache[event] = _build_wav(data)
    elif event == 'win':
        data = _generate_sine_wave(880, 0.15, 0.3) + _generate_sine_wave(1100, 0.15, 0.3)
        _wave_cache[event] = _build_wav(data)
    elif event == 'lose' or event == 'game_over':
        data = _generate_square_wave(200, 0.2, 0.2) + _generate_square_wave(150, 0.3, 0.2)
        _wave_cache[event] = _build_wav(data)
    elif event in params:
        freq, dur, vol = params[event]
        data = _generate_sine_wave(freq, dur, vol)
        _wave_cache[event] = _build_wav(data)
    else:
        data = _generate_sine_wave(440, 0.1, 0.2)
        _wave_cache[event] = _build_wav(data)

    return _wave_cache[event]


def _play_wav(wav_data: bytes) -> None:
    """Play a WAV blob on the current platform."""
    if not wav_data:
        return
    tmp_dir = Path.home() / ".retro_arcade" / ".sounds"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / "_sfx.wav"
    try:
        with open(tmp_path, 'wb') as f:
            f.write(wav_data)
    except IOError:
        return
    _play_file(str(tmp_path))


def _play_file(path: str) -> None:
    """Play a WAV file using platform-appropriate command."""
    if os.name == 'nt':
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except Exception:
            pass
    else:
        # Unix: try aplay, paplay, or sox
        for player in ('aplay', 'paplay', 'sox', 'ffplay'):
            try:
                subprocess.Popen([player, path, '-q'], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return
            except FileNotFoundError:
                continue


def play_sound(event: str = "correct") -> None:
    """Play a synthesized sound effect."""
    mgr = get_stats_manager()
    settings = mgr.get_settings()
    if not settings.get('sound_enabled', True):
        return
    try:
        wav = _get_wav(event)
        if wav:
            _play_wav(wav)
    except Exception as e:
        logger.warning(f"Sound error: {e}")
        # Fallback to terminal beep
        try:
            print("\a", end="", flush=True)
        except Exception:
            pass


# --- Background Music ---

_music_thread: Optional[threading.Thread] = None
_music_stop = threading.Event()


def _music_worker(bpm: int = 120) -> None:
    """Play a simple looping background melody."""
    # Simple retro melody (C major pentatonic)
    notes = [262, 294, 330, 392, 440, 523, 587, 659]
    beat_dur = 60.0 / bpm
    melody: List[int] = []
    pattern = [0, 2, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 2, 0, -1]
    for p in pattern:
        if p >= 0:
            melody.append(notes[p % len(notes)])
        else:
            melody.append(0)

    wav_data = b''
    for note in melody:
        if note > 0:
            wav_data += _generate_sine_wave(note, beat_dur * 0.8, 0.08)
            wav_data += _generate_sine_wave(note * 2, beat_dur * 0.2, 0.04)
        else:
            wav_data += b'\x00' * int(SAMPLE_RATE * beat_dur * 2)

    while not _music_stop.is_set():
        mgr = get_stats_manager()
        settings = mgr.get_settings()
        if settings.get('sound_enabled', True):
            _play_wav(_build_wav(wav_data))
        _music_stop.wait(beat_dur * len(melody) * 0.5)


def start_background_music(bpm: int = 120) -> None:
    """Start background music in a daemon thread."""
    global _music_thread, _music_stop
    stop_background_music()
    _music_stop.clear()
    _music_thread = threading.Thread(target=_music_worker, args=(bpm,), daemon=True)
    _music_thread.start()


def stop_background_music() -> None:
    """Stop background music."""
    _music_stop.set()
    global _music_thread
    if _music_thread and _music_thread.is_alive():
        _music_thread.join(timeout=1)
    _music_thread = None
